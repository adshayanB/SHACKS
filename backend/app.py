  
from flask import Flask, request, jsonify
from flask.globals import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager,jwt_required,create_access_token
from sqlalchemy import Column, Integer,String, Float, Boolean
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from twilio.twiml.messaging_response import MessagingResponse

import os
import uuid
import requests
import datetime
import phonenumbers
import re


 
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///' + os.path.join(basedir,'users.db')
app.config['SECRET_KEY']='secret-key'


s = URLSafeTimedSerializer('SECRET_KEY')


db=SQLAlchemy(app)
@app.cli.command('dbCreate')
def db_create():
    db.create_all()
    print('Database created')

@app.cli.command('dbDrop')
def db_drop():
    db.drop_all()
    print('Database Dropped')

@app.cli.command('dbSeed')
def db_seed():
    testUser1=User( public_id=str(uuid.uuid4()),
                    firstName='Brian',
                    lastName='Porter',
                    email='brianporter@scotiabank,ca',
                    phoneNumber='+16475490857',
                    accountNumberCHEQ='003XTMEW438B',
                    accountNumberSAV='006MACLD834N',
                    savings=12699.42,
                    chequing=200.12,
                    code="AXDS")
    testUser2=User( public_id=str(uuid.uuid4()),
                    firstName='Rishan',
                    lastName='R',
                    email='rr@hotmail.com',
                    phoneNumber='+16479685141',
                    accountNumberCHEQ='002FSZFX223A',
                    accountNumberSAV='005GSDFC223Y',
                    savings=7800.42,
                    chequing=500.12,
                    code="BXDS")
    testUser3=User( public_id=str(uuid.uuid4()),
                    firstName='Adshayan',
                    lastName='B',
                    email='ab@hotmail.com',
                    phoneNumber='+16478095275',
                    accountNumberCHEQ='004FMWXEN44O',
                    accountNumberSAV='002NCELD354B',
                    savings=25000.42,
                    chequing=800.12,
                    code="CXDS")
    db.session.add(testUser1)
    db.session.add(testUser2)
    db.session.add(testUser3)
    db.session.commit()
    print('Seeded')


class User(db.Model):
    id=Column(Integer, primary_key=True)
    public_id=Column(String(50), unique=True)
    firstName=Column(String(50))
    lastName=Column(String(50))
    email=Column(String(50), unique=True)
    phoneNumber=Column(Integer)
    accountNumberCHEQ=Column(String(50))
    accountNumberSAV=Column(String(50))
    savings=Column(Float())
    chequing=Column(Float())
    code=Column(String(50),unique=True)

class Transaction(db.Model):
     id=Column(Integer, primary_key=True)
     public_id=Column(String(50), unique=True)
     accountNumber=Column(String(50))
     transactionValue=Column(Float())
     accFrom = Column(String())
     date=Column(String())

def viewBalanceSMS(phoneNumberVal):
    current_user = User.query.filter_by(phoneNumber=phoneNumberVal).first()
    user_data={}
    user_data['accountNumberSAV']=current_user.accountNumberSAV
    user_data['savings']=current_user.savings
    user_data['accountNumberCHEQ']=current_user.accountNumberCHEQ
    user_data['chequing']=current_user.chequing

    return user_data

@app.route("/userMessage", methods=["POST", "GET"])
def userMessage():

    BALANCE_KEYWORDS = ['balance']
    TRANSACTION_KEYWORDS = ['transaction', 'statement', 'recent']
    TRANSFER_KEYWORDS = ['pay', 'send', 'give', 'e-transfer', 'etransfer', 'e transfer', 'electronic transfer', 'transfer']
    HELP_KEYWORDS = ['help', 'assistance']

    from_phone_number = request.values.get('From', '')
    user_input = request.values.get('Body', '').lower()

    response = MessagingResponse()
    msg = response.message()
    content = ""

    # Add code for what to send back here

    # Check account balance
    if (any(balance_keyword in user_input for balance_keyword in BALANCE_KEYWORDS)):
        # Get account balance
        account = viewBalanceSMS(from_phone_number)
        
        content += "\n\nHere are your account balances:\n\n"
        content += "SAVINGS ACCOUNT:\n"
        content += "Account Number: {}\n".format(account['accountNumberSAV'])
        content += "Account Balance: ${}\n".format(round(account['savings'], 2))
        content += "\n"
        content += "CHEQUING ACCOUNT:\n"
        content += "Account Number: {}\n".format(account['accountNumberCHEQ'])
        content += "Account Balance: ${}\n".format(round(account['chequing'], 2))
    # Check recent transactions
    elif (any(transaction_keyword in user_input for transaction_keyword in TRANSACTION_KEYWORDS)):
        account = viewBalanceSMS(from_phone_number)

        user_input_list = user_input.split()
        num_transactions = 10
        cheq_or_saving = "chequing"
        account_number = account['accountNumberCHEQ']

        for word in user_input_list:
            if word.isnumeric():
                num_transactions = int(word)
        
        if ('saving' in user_input):
            cheq_or_saving = 'savings'

        if (cheq_or_saving == 'savings'):
            account_number = account['accountNumberSAV']
            
        # Get recent transactions
        transactions = trans(from_phone_number, num_transactions, account_number)

        if len(transactions) > 0:
            content += "\n\nSure! Here are your {} most recent {} account transactions:".format(num_transactions, cheq_or_saving)
            for transaction in transactions:
                content += "\n\nFrom: {}\n".format(transaction['From'])
                content += "Date: {}\n".format(transaction['Date'])
                content += "Amount: ${}".format(transaction['TransactionValue'])
        else:
            content += "\n\nWe noticed you haven't made any transactions using your {} account yet.".format(cheq_or_saving)
    # E-transfer money
    elif (any(transfer_keyword in user_input for transfer_keyword in TRANSFER_KEYWORDS)):
        user_input_list = user_input.split()
        sendTo = ''
        amountToSend = ''
        error = ''

        for word in user_input_list:
            # Get amount
            if word[0] == "$":
                amountToSend = float(word[1:])

            # Send to recipient
            # Check for email
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if (re.fullmatch(regex, word)):
                sendTo = word

            # Check for phone number       
            try:
                number = phonenumbers.parse(word, None)
                if phonenumbers.is_valid_number(number):
                    sendTo = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.NATIONAL)
            except:
                continue
            

        if not sendTo:
            error = "\n\nIt seems like you didn't send me the recipient info for this transfer.\nPlease try again with either the recipient's email or phone number specified."
        elif not amountToSend:
            error = "\n\nIt seems like you didn't send me the amount to transfer to {}\n. Please try again with the amount to send to the recipient.".format(sendTo)
        
        if error:
            content += error
        else:
            transfer(from_phone_number, sendTo, amountToSend)
            content += "\n\nThe amount of ${} has successfully been transferred to {}".format(amountToSend, sendTo)

    # Help
    elif (any(help_keyword in user_input for help_keyword in HELP_KEYWORDS)):
        content += "\n\nStuck figuring out what to ask me? There's nothing to fear for I am here!🦸🏻‍♂️\n\n"
        content += "You can ask me anything about your Soctiabank account. Whether it be to check your balance, get your most recent transactions, or even transfer money between accounts or to another person, I've got you covered. 👍\n\n"
        content += "Some examples of what you could ask are:\n"
        content += "'What's my account balance?'\n"
        content += "'Show me the last 15 transactions that were made in my chequing account'\n"
        content += "'Transfer $1000 to INSERT_EMAIL_ADDRESS'\n\n"
        content += "So, what can I help you with today? 😃"
    
    else:
        content += "\n\nI am not sure I understand.\n\nIf you need help navigating around here, ask me for help and I'll let you know what you can ask me. 😃"

    msg.body(content)
    return str(response)
  
@app.route("/transaction", methods=["GET", "POST"])
def transactionSMS():
    trans=request.json

    current_user = User.query.filter_by(phoneNumber=trans['phoneNumber']).first()
    print(trans)
    transNew=Transaction(public_id=str(uuid.uuid4()),
                        accountNumber=trans["AN"],
                        transactionValue=trans["value"],
                        accFrom=trans['from'],
                        date=datetime.datetime.now().strftime("%A, %B %d, %Y"))
    db.session.add(transNew)
    db.session.commit()
    user_data={}
    user_data['accountNumberSAV']=current_user.accountNumberSAV
    user_data['savings']=current_user.savings
    user_data['accountNumberCHEQ']=current_user.accountNumberCHEQ
    user_data['chequing']=current_user.chequing

    if (user_data['accountNumberCHEQ'] == trans['AN']):
        current_user.chequing = user_data['chequing']+trans['value']
        db.session.commit()
    if (user_data['accountNumberSAV'] == trans['AN']):
        current_user.savings = user_data['savings']+trans['value']
        db.session.commit()



    return jsonify(message="Transaction SUCCESS")

def trans(phoneNumberVal, numberTrans, accountNumberVal):
    current_user = User.query.filter_by(phoneNumber=phoneNumberVal).first()
    user_data={}
    user_data['accountNumberSAV']=current_user.accountNumberSAV
    user_data['savings']=current_user.savings
    user_data['accountNumberCHEQ']=current_user.accountNumberCHEQ
    user_data['chequing']=current_user.chequing
    if (accountNumberVal != user_data['accountNumberSAV'] and accountNumberVal != user_data['accountNumberCHEQ'] ):
        return []

    transall=Transaction.query.filter_by(accountNumber=accountNumberVal).order_by('date').all()
    output=[]
    count = 0
    if transall:
        for data in reversed(transall):
            if count!=numberTrans:
                transData={}
                transData['TransactionValue']=data.transactionValue
                transData['From']=data.accFrom
                transData['Date']=data.date
                count+=1
                output.append(transData)
            else:
                break
        return output
    else:
        return []

def transfer(phoneNumberVal, sendToVal, valueVal):
    current_user = User.query.filter_by(phoneNumber=phoneNumberVal).first()
    transNew=Transaction(public_id=str(uuid.uuid4()),
                        accountNumber=current_user.accountNumberCHEQ,
                        transactionValue=-valueVal,
                        accFrom="You",
                        date=datetime.datetime.now().strftime("%A, %B %d, %Y"))
    db.session.add(transNew)
    db.session.commit()
    
    user_data={}
    user_data['chequing']=current_user.chequing

    current_user.chequing = user_data['chequing']-valueVal

    db.session.commit()

    return True


if __name__ == '__main__':
    app.run(debug=True)