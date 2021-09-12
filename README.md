![](https://img.shields.io/badge/Language-Python-informational?style=flat&logo=<LOGO_NAME>&logoColor=white&color=0047AB)
![](https://img.shields.io/badge/Framework-Flask-informational?style=flat&logo=<LOGO_NAME>&logoColor=white&color=2bbc8a)
![](https://img.shields.io/badge/API-Twilio-informational?style=flat&logo=<LOGO_NAME>&logoColor=white&color=EB4747)
![](https://img.shields.io/badge/Proxy_Server-Ngrok-informational?style=flat&logo=<LOGO_NAME>&logoColor=white&color=FFA500)
![](https://img.shields.io/badge/DB-SQLite-informational?style=flat&logo=<LOGO_NAME>&logoColor=white&color=ADD8E6)

# SMScotia

SMScotia is an SMS service that allows customers to utilize SMS messaging to perform a variety of banking tasks such as checking balance, sending money to other individuals and more! Our team has utilized natural langauge processing, a web python server and the Twilio API to make this possible to allow users to text messages to our service's number and be given accesses to online banking services usually restricted to mobile or desktop platforms. The purpose of this project was to bridge the gap between those who lack an internet connection or mobile data plan to give them more power using the tools they already have, SMS messaging! Users will not even require smartphones to utilize our service, and we hope that by bridging this gap, we empower those who are struggling a key to controlling their finances. 

Demo: https://share.vidyard.com/watch/Ne8jrSmSkSXwedFgmTW8Yd?/

## Inspiration 💡

The focus of S Hacks is to bridge the technological gap between those who can't use modern day technology or simply do not have access to it. We want to give this demographic of individuals a means to still use modern day technology at their convenience and ease. A staple in our modern day society is simple, a working cellphone. While some individuals might not have their own PCs, workstations, IPads and other devices, these same individuals will most likely have at least a phone. 

Our team wanted to utilize this fact and common base of individuals to build something that would allow individuals that have any phone to use modern day tools and services, regardless of if the person had a smart phone, was an elderly person, or not tech saavy. Introducing SMScotia, SMScotia allows any phone user to use text messages to access online banking services usually accessed through a mobile app or website. 

## What It Does 😃

SMScotia is a backend service that a bank can implement to allow it's clients to text a number to view their banking information and perform other actions as well. Users can text the number provided to them a variety of commands and will receive a response back instantly via SMS. Users can also text this number to be provided a growing list of commands to ensure clients can utilize this service to it's maximum potential. We’ve utilized natural language processing to support all types of customer commands, to make sure their requests are serviced! We hope that this service allows individuals who maybe aren't the best at using mobile/desktop apps, or those with phones incapable of downloading apps, or those without an internet connection, can use this service to stay connected and in power of their finances.

## How We Built It 🔨

Our backend service was built in **flask** and **python**. We utilized **flask** to service as the server that the incoming requests would be routed too. We used the **Twilio API** as a way to use SMS messaging for clients to actually send commands and receive responses from our server. We used **SQLite** in our python server to actual hold the bank account models, to use as storage and serve as our mock banking service. Finally we used a service called **Ngrok** as a way to host local python servers on a public domain site so we could test and demo the finished project.

We used **NLP** or **Natural language processing** to process incoming text messages from our users to ensure that they could phrase commands however they like but still receive the information they required! 

The **Twilio API** was especially vital in making our team's vision a reality. As this service is what really allowed us to make a working feature with actual SMS messaging instead of a mock version of it. We decided to use **Flask** so we could spend more time focussing on the features of our service rather than project set up. **Python** and **SQLite** are both easy to use tools that would speed up development. 

## How To Use It 🧠

You can text our service's number with a message in order to utilize online banking services, view your account information or simply get help! 

To get help with available commands simply text a message like *"I need help"* and you will receive a list of available commands you can use via SMS.

To check your account balance simply text a message like *"Check my balance"* or *"I want my balance"* to view your chequings and savings account balance.

To send money to another person, send a message like this: *"Send $[NUMBER HERE] to +1[PHONE NUMBER HERE]"* or *"Send $[NUMBER HERE] to [EMAIL ADDRESS HERE]"* to utilize e-transfer via SMS to send money to another individual through their phone number or email.

Finally to view some of your transactions simply send a message like this: "*View my last [NUMBER OF TRANSACTIONS HERE] transactions"* to be prompted with a list of your last transactions based on how many you would like to view.

