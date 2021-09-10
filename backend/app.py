  
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
    testUser=User( public_id=str(uuid.uuid4()),
                    firstName='User',
                    lastName='Test',
                    email='doctor@doctor.com',
                    phoneNumber='4166666666',
                    accountNumberCHEQ='ADCCCHDHFH1111',
                    accountNumberSAV='ADSHJDSHDSFHDSHF',
                    savings=12699.42,
                    chequing=200.12,
                    code="69696969")
    db.session.add(testUser)
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

@app.route("/accountBalance", methods=["POST"])
def viewBalanceSMS():
    current_user = User.query.filter_by(code="69696969").first()
    user_data={}
    user_data['accountNumberSAV']=current_user.accountNumberSAV
    user_data['savings']=current_user.savings
    user_data['accountNumberCHEQ']=current_user.accountNumberCHEQ
    user_data['chequing']=current_user.chequing

    return jsonify(user_data)

@app.route("/userMessage", methods=["POST", "GET"])
def userMessage():
    user_input = request.values.get('Body', '').lower()

    response = MessagingResponse()
    msg = response.message()
    content = ""

    # Add code for what to send back here

    # Some test code
    content += "Your message is the following:\n"
    content += user_input


    msg.body(content)
    return str(response)
  
@app.route("/transaction", methods=["GET", "POST"])
def transactionSMS():
    trans=request.json

    current_user = User.query.filter_by(code="69696969").first()
    print(trans)
    transNew=Transaction(public_id=str(uuid.uuid4()),
                        accountNumber=trans["AN"],
                        transactionValue=trans["value"],
                        accFrom=trans['from'],
                        date=datetime.datetime.now())
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



@app.route('/recentTranscations', methods=['GET'])
def trans():
    current_user = User.query.filter_by(code="69696969").first()
    req=request.json
    numRecent=req['recentValues']
    user_data={}
    user_data['accountNumberSAV']=current_user.accountNumberSAV
    user_data['savings']=current_user.savings
    user_data['accountNumberCHEQ']=current_user.accountNumberCHEQ
    user_data['chequing']=current_user.chequing

    transall=Transaction.query.filter_by(accountNumber=req['AN']).order_by('date').all()
    output=[]
    count = 0
    if transall:
        for data in reversed(transall):
            if count!=numRecent:
                transData={}
                transData['AccountNumber']=data.accountNumber
                transData['TransactionValue']=data.transactionValue
                transData['From']=data.accFrom
                transData['Date']=data.date
                count+=1

                output.append(transData)
            else:
                break
        return jsonify(userData=output)
    else:
        return jsonify(message='You do not have any Transaction Data')

@app.route('/transfer')
def transfer():
    current_user = User.query.filter_by(code="69696969").first()
    req=request.json
    sendTo=req["sendTo"]
    transNew=Transaction(public_id=str(uuid.uuid4()),
                        accountNumber=sendTo,
                        transactionValue=req["value"],
                        accFrom=current_user.accountNumberCHEQ,
                        date=datetime.datetime.now())
    db.session.add(transNew)
    db.session.commit()
    
    user_data={}
    user_data['chequing']=current_user.chequing

    current_user.chequing = user_data['chequing']-req["value"]


    return jsonify(message="TRANSFER SUCCESS")







if __name__ == '__main__':
    app.run(debug=True)