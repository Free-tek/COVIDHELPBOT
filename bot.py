from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd
from firebase import firebase
from random import randrange
import firebase_admin
from firebase_admin import db
from firebase_admin import credentials
import datetime as dt
from datetime import datetime
from datetime import timedelta
import phonenumbers
from phonenumbers.phonenumberutil import region_code_for_country_code
from phonenumbers.phonenumberutil import region_code_for_number
import pycountry
from rasa_nlu.model import Interpreter
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
import warnings




app = Flask(__name__)


@app.route('/bot', methods=['POST'])

def bot():
    warnings.filterwarnings("ignore", category=FutureWarning)
    
    
    #TODO:
    #Preposition switching of you and they for when you are asking the doctor for yourself or for someone else
    #if last time of conversation with dr bot is less than 5 minutes send a prompt to either continue conversation or not
    #Festus must add this line of code beneath everyline of code to track news features
    #ref = db.reference('lastCommandNews')
    #ref = db.reference('lastCommandNews').child(sender).set('False')
    
    

    
    # Initialize the app with a service account, granting admin privileges
    if not firebase_admin._apps:
        #fetch credentials
        cred = credentials.Certificate("service_account.json")
        firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://free-from-corona-virus.firebaseio.com/'
    })
    
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    responded = False
    
    
    #countriesIndex
    countryIndex = ['AF', 'AL', 'DZ', 'AO', 'AR', 'AM', 'AU', 'AT', 'AZ', 'BS', 'BD', 'BY', 'BE', 'BZ', 'BJ', 'BT', 'BO', 'BA', 'BW', 'BR', 'BN', 'BG', 'BF', 'BI', 'KH', 'CM', 'CA', 'CI', 'CF', 'TD', 'CL', 'CN', 'CO', 'CG', 'CD', 'CR', 'HR', 'CU', 'CY', 'CZ', 'DK', 'DP', 'DJ', 'DO', 'CD', 'EC', 'EG', 'SV', 'GQ', 'ER', 'EE', 'ET', 'FK', 'FJ', 'FI', 'FR', 'GF', 'TF', 'GA', 'GM', 'GE', 'DE', 'GH', 'GR', 'GL', 'GT', 'GN', 'GW', 'GY', 'HT', 'HN', 'HK', 'HU', 'IS', 'IN', 'ID', 'IR', 'IQ', 'IE', 'IL', 'IT', 'JM', 'JP', 'JO', 'KZ', 'KE', 'KP', 'XK', 'KW', 'KG', 'LA', 'AV', 'LB', 'LS', 'LR', 'LY', 'LT', 'LU', 'MK', 'MG', 'MW', 'MY', 'ML', 'MR', 'MX', 'MD', 'MN', 'ME', 'MA', 'MZ', 'MN', 'NA', 'NP', 'NL', 'NC', 'NZ', 'NI', 'NE', 'NG', 'KP', 'NO', 'OM', 'PK', 'PS', 'PA', 'PG', 'PY', 'PE', 'PH', 'PL', 'PT', 'PR', 'QA', 'XK', 'RO', 'RU', 'RW', 'SA', 'SN', 'RS', 'SL', 'SG', 'SK', 'SI', 'SB', 'SO', 'ZA', 'KR', 'SS', 'ES', 'LK', 'SD', 'SR', 'SJ', 'SZ', 'SE', 'CH', 'SY', 'TW', 'TJ', 'TZ', 'TH', 'TL', 'TG', 'TT', 'TN', 'TR', 'TM', 'AE', 'UG', 'GB', 'UA', 'US', 'UY', 'UZ', 'VU', 'VE', 'VN', 'EH', 'YE', 'ZM', 'ZW']
    
    
    countryList = [ "afghanistan","albania","algeria","angola","argentina","armenia","australia","austria","azerbaijan","bahamas","bangladesh","belarus","belgium","belize","benin","bhuta","bolivia","bosnia and herzegovina","botswana","brazil","brunei darussalam","bulgaria","burkina faso","burundi","cambodia","cameroon","canada","ivory coast","central african republic","chad","chile","china",
            "colombia","congo","democratic republic of congo","costa rica","croatia","cuba","cyprus","czech republic","denmark","diamond princess","djibouti","dominican republic","dr congo","ecuador","egypt","el salvador","equatorial guinea","eritrea","estonia","ethiopia","falkland islands","fiji","finland","france","french guiana","french southern territories","gabon","gambia","georgia","germany",
            "ghana","greece","greenland","guatemala","guinea","guinea-bissau","guyana","haiti","honduras","hong kong","hungary","iceland","india","indonesia","iran","iraq","ireland","israel","italy","jamaica","Japan","Jordan","Kazakhstan","Kenya","Korea","Kosovo","Kuwait","kyrgyzstan","lao","latvia","lebanon","lesotho","liberia","libya","lithuania","luxembourg","macedonia","madagascar","malawi","malaysia",
            "mali","mauritania","mexico","moldova","mongolia","montenegro","morocco","mozambique","myanmar","namibia","nepal","netherlands","new caledonia","new zealand","nicaragua","niger","nigeria","north korea","norway","oman","pakistan","palestine","panama","papua new guinea","paraguay","peru","philippines","poland","portugal","puerto rico","qatar","republic of kosovo","romania","russia","rwanda",
            "saudi arabia","senegal","serbia","sierra leone","singapore","slovakia","slovenia","solomon islands","somalia","south africa","south korea","south sudan","spain","sri lanka","sudan","suriname","svalbard and jan mayen","swaziland","sweden","switzerland","syrian arab republic","taiwan","tajikistan","tanzania","thailand","timor-leste","togo","trinidad and tobago","tunisia","turkey","turkmenistan","uae",
            "uganda","united kingdom","ukraine","usa","uruguay","uzbekistan","vanuatu","venezuela","vietnam","western sahara","yemen","zambia","zimbabwe"]
            
            
    countryDict = {"uk": "GB", "bosnia": "BA", "herzegovina": "BA", "united states of america": "US" , "dubai": "AE"}

    otherIntents = ['get_news', 'get_news_country', 'get_tips', 'get_statsAll', 'get_statsCountry', 'get_economyBounce', 'get_goodNews', 'symptoms', 'symptom_question', 'get_tips', 'help']
    
    firebase_instance = firebase.FirebaseApplication('https://free-from-corona-virus.firebaseio.com/')
    data = firebase_instance.get('/', None)
               
    sender = request.values.get('From', '').split(':')[1]
    try:
        previousConversationDate = data[sender]['previousConversationDate']
    except:
        previousConversationDate = False
        
    try:
        previousConversationStep = data[sender]['previousConversationStep']
    except:
        previousConversationStep = False
        
    
    try:
        drConversationDone = data[sender]['drConversationDone']
    except:
        drConversationDone = 'True'
    
    '''
    conversation steps
    1 - Disclaimer
    2 - Introduction
    3 - BIODATA
        3A - Country
        3B - Who you are asking for
        3C - Sex
        3D - Age
        3E - Gender
    4 - Life threatning symptoms
    5A - No Life threatning Symptom
    5B - No Symptom
    6 - Mild and no trouble breathing
    7 - Where you have been
    '''
    
    interpreter = Interpreter.load('./models/nlu/default/COVIDHelpbot')
    result = interpreter.parse(incoming_msg)
    intentName = result['intent']['name']
    
    datetimeFormat = '%Y/%m/%d %H:%M:%S'
    now = datetime.now()
    dateNow = now.strftime("%Y/%m/%d %H:%M:%S")
    
     
    try:
        dateBefore = data[sender]['previousConversationDate']
    except:
        dateBefore = '2017/05/28 19:02:01'
         
     
    
    diff = dt.datetime.strptime(dateNow, datetimeFormat)\
        - dt.datetime.strptime(dateBefore, datetimeFormat)


    print(f'this is the intent name {intentName}')
    #more news is requested
    if 'more' == incoming_msg or '\'more\'' == incoming_msg or ('more' in incoming_msg and 'news' in incoming_msg) or ('\'more\'' in incoming_msg and 'news' in incoming_msg):
        
        smileyBox = ['🤔', '🤭', '😷', '🙎‍♀️', '🙎‍♂️', '🕶', '🌎', '🌍', '🚨', '🏥', '📈', '📉', '📊', '📜', '📃', '📄', '🗞', '📌', '⭕', '💭' ]
        
        
        #allNews
        sender = request.values.get('From', '').split(':')[1]
        
        try:
            lastCommandNews = data['lastCommandNews'][sender]
        except:
            lastCommandNews = False
            
            
        
        if lastCommandNews == False:
            message = f'🤔Oops..., i am sorry. I think i am lost here but i can help you with some 📃news.'
        elif lastCommandNews == 'allNews':
        
            try:
                commands = data['commands'][sender]
            except:
                commands = False
                  
           
            
            news = data['news']
            error = False
            
            if commands != None:
                commands = int(commands)
                news = news[commands:commands+5]
            else:
                news = news[1:6]
                error = True

                       
                       
            message = ''
            index = commands
            for item in news:
                for key, value in item.items():
                    if key == 'title':
                        title = value
                    elif key == 'description':
                        description = value
                    elif key == 'date':
                        date = value
                    elif key == 'url':
                        link = value
                           
                message += f'\n {index}: {smileyBox[randrange((len(smileyBox)-1))]} {title} \n'
                index+=1
                
                if error == False:
                    ref = db.reference('commands').child(sender).set(commands+5)
                else:
                    ref = db.reference('commands').child(sender).set(6)
                
                ref = db.reference('lastCommandNews').child(sender).set('allNews')
                ref = db.reference(sender).child('drConversationDone').set('True')
                    
            message += f'\n \n ↪️Reply with the number of the news you will like to read more about or ↪️reply with \'more\' to get more headlines'
                       
                    
            
            msg.body(message)
            responded = True
            print(f'1 - {message}')
            
            
            
        else:
            #user wants more of his country news
            try:
                commands = data['commands'][sender]
            except:
                commands = False
                       
            news = data['country_news'][f'{lastCommandNews}_news']
            error = False
            if commands != None:
                commands = int(commands)
                news = news[commands:commands+5]
            else:
                news = news[1:6]
                error = True

                       
                       
            message = ''
            index = commands
            for item in news:
                for key, value in item.items():
                    if key == 'title':
                        title = value
                    elif key == 'description':
                        description = value
                    elif key == 'date':
                        date = value
                    elif key == 'url':
                        link = value
                           
                message += f'\n {index}: {smileyBox[randrange((len(smileyBox)-1))]} {title} \n'
                index+=1
                
                if error == False:
                    ref = db.reference('commands').child(sender).set(commands+5)
                else:
                    ref = db.reference('commands').child(sender).set(6)
                
                ref = db.reference('lastCommandNews').child(sender).set(f'{lastCommandNews}')
                ref = db.reference(sender).child('drConversationDone').set('True')
                    
            message += f'\n \n ↪️Reply with the number of the news you will like to read more about or ↪️reply with \'more\' to get more headlines'
                       
                    
            
            msg.body(message)
            responded = True
            
            print(f'2 - {message}')
            
    
    #specific message is requested
    elif incoming_msg.isdigit() and drConversationDone == 'True':
    
        smileyBox = ['🤔', '🤭', '😷', '🙎‍♀️', '🙎‍♂️', '🕶', '🌎', '🌍', '🚨', '🏥', '📈', '📉', '📊', '📜', '📃', '📄', '🗞', '📌', '⭕', '💭' ]

                   
        sender = request.values.get('From', '').split(':')[1]
        try:
            commands = data['lastCommandNews'][sender]
        except:
            commands = False
            
    
        
        
        if commands == 'allNews' or commands == False:
            #fecth the news at number for the user
            news = data['news'][int(incoming_msg)]
            for key, value in news.items():
                if key == 'title':
                    title = value
                elif key == 'description':
                    description = value
                elif key == 'date':
                    date = value
                elif key == 'url':
                    link = value
                       
            message = f'\n {smileyBox[randrange((len(smileyBox)-1))]} {title} \n \n {description}           -{date} \n \n {link}'
            ref = db.reference('lastCommandNews').child(sender).set('allNews')
            ref = db.reference(sender).child('drConversationDone').set('True')
        
        
        else:
            news = data['country_news'][f'{commands}_news'][int(incoming_msg)]
            for key, value in news.items():
                if key == 'title':
                    title = value
                elif key == 'description':
                    description = value
                elif key == 'date':
                    date = value
                elif key == 'url':
                    link = value
                       
            message = f'\n {smileyBox[randrange((len(smileyBox)-1))]} {title} \n \n {description}           -{date} \n \n {link}'
            ref = db.reference('lastCommandNews').child(sender).set(f'{commands}')
            ref = db.reference(sender).child('drConversationDone').set('True')
        
        
        msg.body(message)
        responded = True
        #print(message)
        
        
        
        
    #check if it is a conversation with dr Ore exists in the last 5 min
    elif diff.seconds <= 300 and drConversationDone == 'False':
        #still talking to the dr
        
        
        #Do Introduction
        if previousConversationStep == '1' and (incoming_msg == 'agree' or incoming_msg == '\'agree\'' ):
        
            message = 'Hello, I am Dr Ore 👩‍⚕️ (a bot doctor). \n \n I\'ll be asking you a few questions just to assist you in making the decision to seek medical care and please remember that i am not a healthcare practitioner, so please ☎️ contact one if you need to. \n \n Can I proceed?'
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('2')
            ref = db.reference(sender).child('drConversationDone').set('False')
            
            msg.body(message)
            responded = True
            print(message)
               
        elif previousConversationStep == '1'and (incoming_msg == 'disagree' or incoming_msg == '\'disagree\'' ):
        
            message = 'Alright, it was nice speaking to you ✌️'
            
            msg.body(message)
            responded = True
            print(message)
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('1')
            ref = db.reference(sender).child('drConversationDone').set('True')
            
            
            
        elif previousConversationStep == '1':
                
                message = 'Ooops.. 🤔, i do not understand your last message, Do you ✅agree or ❌disagree with the disclaimer. \n \n Send Agree or Disagree to proceed'
                
                msg.body(message)
                responded = True
                print(message)
                
                now = datetime.now()
                date = now.strftime("%Y/%m/%d %H:%M:%S")
                
                ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
                ref = db.reference(sender).child('previousConversationStep').set('1')
                ref = db.reference(sender).child('drConversationDone').set('False')
                
        
        #ask country 3a
        elif previousConversationStep == '2' and ( 'yes' in incoming_msg or 'y' == incoming_msg or 'proceed' == incoming_msg  ) and 'not' not in incoming_msg:
            
            message = 'Which 🇳🇬country are you currently staying in?'
            
            msg.body(message)
            responded = True
            print(message)
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('3a')
            ref = db.reference(sender).child('drConversationDone').set('False')
        
        
        elif previousConversationStep == '2' and ('no' in incoming_msg or incoming_msg == 'n' or incoming_msg == 'dont' or incoming_msg == 'do\'nt') and 'not' not in incoming_msg:
        
            message = 'Alright, it was nice speaking to you ✌️'
            
            msg.body(message)
            responded = True
            print(message)
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('1')
            ref = db.reference(sender).child('drConversationDone').set('True')
                
        
        elif previousConversationStep == '2':
                
            message = 'Ooops.. 🤔, i do not understand your last message, should i ✅proceed with the questions i\'ll like to ask you or not ? \n \n Send Yes or No to proceed.'
            
            msg.body(message)
            responded = True
            print(message)
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('2')
            ref = db.reference(sender).child('drConversationDone').set('False')
            
            
        
        #take record (do NER to be sure you were given a country) country and ask who they asking for
        elif previousConversationStep == '3a':
            country = getNER(incoming_msg)
            
            print(f'NER result {country}')
            if country == None:
                message = 'Ooops.. 🤔, i do not understand your last message, you were supposed to ↪️reply with the name of the country🌍 you are staying in.'
                
                msg.body(message)
                responded = True
                print(message)
                
                now = datetime.now()
                date = now.strftime("%Y/%m/%d %H:%M:%S")
                
                ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
                ref = db.reference(sender).child('previousConversationStep').set('3a')
                ref = db.reference(sender).child('drConversationDone').set('False')
            
            else:
                #save users Response to db
                message = 'Are you 📄answering for yourself or for someone else?'
                
                msg.body(message)
                responded = True
                print(message)
                
                now = datetime.now()
                date = now.strftime("%Y/%m/%d %H:%M:%S")
                date2 = now.strftime("%Y/%m/%d %H")
                
                ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
                ref = db.reference(sender).child('previousConversationStep').set('3b')
                ref = db.reference(sender).child('drConversationDone').set('False')
                
                ref = db.reference(sender).child('response').child(f'{date2}').child('country').set(f'{country}')

            
        #ask sex
        elif previousConversationStep == '3b' and ( 'yes' in incoming_msg or 'y' == incoming_msg or 'proceed' == incoming_msg ) and 'not' not in incoming_msg:
            
            message = 'What is your gender, Male🙍‍♂️ or Female🙍‍♀️?'
            
            msg.body(message)
            responded = True
            print(message)
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            date2 = now.strftime("%Y/%m/%d %H")
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('3c')
            ref = db.reference(sender).child('drConversationDone').set('False')
            
            
            ref = db.reference(sender).child('response').child(f'{date2}').child('answeringForY_SE').set(f'Yes')
        
        
        elif previousConversationStep == '3b' and ('no' in incoming_msg or incoming_msg == 'n') and 'not' not in incoming_msg:
        
            message = 'What is your gender, Male🙍‍♂️ or Female🙍‍♀️?'
            
            msg.body(message)
            responded = True
            print(message)
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            date2 = now.strftime("%Y/%m/%d %H")
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('3c')
            ref = db.reference(sender).child('drConversationDone').set('False')
            
            
            ref = db.reference(sender).child('response').child(f'{date2}').child('answeringForY_SE').set(f'No')
            
        elif previousConversationStep == '3b':
        
            message = 'Ooops.. 🤔, i do not understand your last message, i asked if you were answering for someone else? \n \n Send Yes or No to proceed.'
            
            msg.body(message)
            responded = True
            print(message)
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('3b')
            ref = db.reference(sender).child('drConversationDone').set('False')
            
            
            
            
        #ask age
        elif previousConversationStep == '3c' and ( 'male' in incoming_msg or 'man' == incoming_msg or 'boy' == incoming_msg ) and 'not' not in incoming_msg:
            
            message = 'What is your age, just ↪️reply with a number 🔢 e.g 20?'
            
            msg.body(message)
            responded = True
            print(message)
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            date2 = now.strftime("%Y/%m/%d %H")
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('4')
            ref = db.reference(sender).child('drConversationDone').set('False')
            
            
            ref = db.reference(sender).child('response').child(f'{date2}').child('gender').set(f'Male')
        
        
        elif previousConversationStep == '3c' and ('female' in incoming_msg or incoming_msg == 'woman' or incoming_msg == 'girl') and 'not' not in incoming_msg:
        
            message = 'What is your age, just ↪️reply with a number 🔢 e.g 20?'
            
            msg.body(message)
            responded = True
            print(message)
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            date2 = now.strftime("%Y/%m/%d %H")
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('4')
            ref = db.reference(sender).child('drConversationDone').set('False')
            
            
            ref = db.reference(sender).child('response').child(f'{date2}').child('gender').set(f'Female')
            
        elif previousConversationStep == '3b':
        
            message = 'Ooops.. 🤔, i do not understand your last message, i asked what your gender was? \n \n Your response should be either Male🙍‍♂️ or Female🙍‍♀️.'
            
            msg.body(message)
            responded = True
            print(message)
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('3b')
            ref = db.reference(sender).child('drConversationDone').set('False')
            
            
            
        elif previousConversationStep == '4' and incoming_msg.isdigit() == True:
            
            message = 'Have you shown any of these life-threatening symptoms🤒? \n \n 😨Blue-colored lips or face \n \n 🤢Severe and constant pain or pressure in the chest  \n \n 😴Severe and constant dizziness or lightheadedness \n \n 😕Acting confused (new or worsening) \n \n 😰Unconscious or very difficult to wake up \n \n 🤭Slurred speech (new or worsening) \n \n 😫New seizure or seizures that won’t stop \n \n \n ↪️Reply with a ✅Yes or ❌No'
            msg.body(message)
            responded = True
            print(message)
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            date2 = now.strftime("%Y/%m/%d %H")
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('5a')
            ref = db.reference(sender).child('drConversationDone').set('False')
            
            
            ref = db.reference(sender).child('response').child(f'{date2}').child('age').set(f'{incoming_msg}')
        
        elif previousConversationStep == '4':
            
            message = 'Ooops.. 🤔, i do not understand your last message, i asked what your age was? \n \n Your response should be a number.'
            
            msg.body(message)
            responded = True
            print(message)
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('4')
            ref = db.reference(sender).child('drConversationDone').set('False')
            
            
        elif previousConversationStep == '5a' and ( 'yes' in incoming_msg or 'y' == incoming_msg) and 'not' not in incoming_msg:
        
            firebase_instance = firebase.FirebaseApplication('https://free-from-corona-virus.firebaseio.com/')
            data = firebase_instance.get('/', None)
        
            sender = request.values.get('From', '').split(':')[1]
            
            pn = phonenumbers.parse(sender)
            countryCode = pn.country_code
            
            
            country = pycountry.countries.get(alpha_2=region_code_for_number(pn))
            nameCountry = country.name
        
            try:
                CDC = data['cdc_help'][nameCountry]
            except:
                CDC = ''
            
        
            message = f'I\'ll suggest that based on your symptoms 🤢, you may need urgent medical attention 👨‍⚕️. \n \n Please ☎️call your countries emergency number and tell them if you have had contact with someone with COVID-19 🦠 or if you have recently been to an area where COVID-19 🦠 is spreading. Your Countries CDC number is {CDC}'
            
            msg.body(message)
            responded = True
            print(message)
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            date2 = now.strftime("%Y/%m/%d %H")
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('5a')
            ref = db.reference(sender).child('drConversationDone').set('True')
            
            ref = db.reference(sender).child('response').child(f'{date2}').child('lifeThreatningSymptoms').set(f'True')
        
        
        
        elif previousConversationStep == '5a' and ('no' in incoming_msg or incoming_msg == 'n') and 'not' not in incoming_msg:
        
        
            message = f'Have you experienced any of the following symptoms🤢? \n \n 😤Coughing up blood (more than about 1 teaspoon). \n \n  🥶Signs of low blood pressure (too weak to stand, light-headed, feeling cold, pale, clammy skin) \n \n \n ↪️Reply with a ✅Yes or ❌No'
            
            msg.body(message)
            responded = True
            print(message)
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            date2 = now.strftime("%Y/%m/%d %H")
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('5b')
            ref = db.reference(sender).child('drConversationDone').set('False')
            
            ref = db.reference(sender).child('response').child(f'{date2}').child('lifeThreatningSymptoms').set(f'False')
            
            
        elif previousConversationStep == '5a':
        
            message = 'Ooops.. 🤔, i do not understand your last message, have you experienced any of the symptoms above? \n \n Your response should ✅Yes or ❌No.'
            
            msg.body(message)
            responded = True
            print(message)
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('5a')
            ref = db.reference(sender).child('drConversationDone').set('False')
            
        
        
        
        elif previousConversationStep == '5b' and ( 'yes' in incoming_msg or 'y' == incoming_msg) and 'not' not in incoming_msg:
        
            firebase_instance = firebase.FirebaseApplication('https://free-from-corona-virus.firebaseio.com/')
            data = firebase_instance.get('/', None)
        
            sender = request.values.get('From', '').split(':')[1]
            
            pn = phonenumbers.parse(sender)
            countryCode = pn.country_code
            
            
            country = pycountry.countries.get(alpha_2=region_code_for_number(pn))
            nameCountry = country.name
        
            try:
                CDC = data['cdc_help'][nameCountry]
            except:
                CDC = ''
            
        
            message = f'I\'ll suggest that based on your symptoms 🤢, you may need urgent medical attention 👨‍⚕️. \n \n Please ☎️call your countries emergency number and tell them if you have had contact with someone with COVID-19 🦠 or if you have recently been to an area where COVID-19 🦠 is spreading. Your Countries CDC number is {CDC}'
            
            msg.body(message)
            responded = True
            print(message)
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            date2 = now.strftime("%Y/%m/%d %H")
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('5b')
            ref = db.reference(sender).child('drConversationDone').set('True')
            
            ref = db.reference(sender).child('response').child(f'{date2}').child('severeSymptoms').set(f'True')
        
        
        
        elif previousConversationStep == '5b' and ('no' in incoming_msg or incoming_msg == 'n') and 'not' not in incoming_msg:
        
        
            message = f'How many of the following do you have? \n \n 🤒Fever or feeling feverish (chills, sweating) \n \n 😤Cough  \n \n 🥵Sore throat \n \n 🤕Muscle aches or body aches \n \n 🤮Vomiting or diarrhea \n \n 👃Change in smell or taste \n \n \n ↪️Reply with the number of these symptoms you show e.g 3 or None if you show none'
            
            msg.body(message)
            responded = True
            print(message)
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            date2 = now.strftime("%Y/%m/%d %H")
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('6')
            ref = db.reference(sender).child('drConversationDone').set('False')
            
            ref = db.reference(sender).child('response').child(f'{date2}').child('severeSymptoms').set(f'False')
            
            
        elif previousConversationStep == '5b':
        
            message = 'Ooops.. 🤔, i do not understand your last message, have you experienced any of the symptoms above? \n \n Your response should ✅Yes or ❌No.'
            
            msg.body(message)
            responded = True
            print(message)
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('5b')
            ref = db.reference(sender).child('drConversationDone').set('False')
            
            
        elif previousConversationStep == '6' and incoming_msg.isdigit() == True:
            
            message = 'In the 📅two weeks before you felt 🤢sick, did you: \n \n 🤝Have contact with someone diagnosed with COVID-19 \n 🏥Live in or visit a place where COVID-19 is spreading \n \n 🏥Live in a long-term care facility or  nursing home? \n \n ✙ Volunteer to help people with COVID-19 \n \n 🚖Visit a facility where COVID-19 patients are treated? \n ↪️Reply with a ✅Yes or ❌No'
            msg.body(message)
            responded = True
            print(message)
            
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            date2 = now.strftime("%Y/%m/%d %H")
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('7')
            ref = db.reference(sender).child('drConversationDone').set('False')
            
            
            ref = db.reference(sender).child('response').child(f'{date2}').child('generalSymptomsShown').set(f'{incoming_msg}')
        
        elif previousConversationStep == '6' and 'none' in incoming_msg:
        
            message = 'In the 📅two weeks before you felt 🤢sick, did you: \n \n 🤝Have contact with someone diagnosed with COVID-19 \n 🏥Live in or visit a place where COVID-19 is spreading \n \n 🏥Live in a long-term care facility or  nursing home? \n \n ✙ Volunteer to help people with COVID-19 \n \n 🚖Visit a facility where COVID-19 patients are treated? \n ↪️Reply with a ✅Yes or ❌No'
            msg.body(message)
            responded = True
            print(message)
            
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            date2 = now.strftime("%Y/%m/%d %H")
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('7')
            ref = db.reference(sender).child('drConversationDone').set('False')
            
            
            ref = db.reference(sender).child('response').child(f'{date2}').child('generalSymptomsShown').set(f'{incoming_msg}')
            
        
        elif previousConversationStep == '6' :
            
            message = 'Ooops.. 🤔, i do not understand your last message, i asked if you have shown any of the 🤢symptoms above? \n \n Your response should be ✅Yes or ❌No.'
            
            msg.body(message)
            responded = True
            print(message)
            
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('6')
            ref = db.reference(sender).child('drConversationDone').set('False')

            
            

        elif previousConversationStep == '7' and ( 'yes' in incoming_msg or 'y' == incoming_msg) and 'not' not in incoming_msg:
        
            
            message = f'🏥Living in a long-term care facility, a nursing home, 🚖visiting facilities where people are treated from COVID-19 may put you at a higher risk for 🤢severe illness. Tell a 👨‍⚕️medical personel that you are sick and need to see a medical provider as soon as possible. \n \n ⚠️Help protect others from getting sick: \n \n 🏠Stay in your room except to get medical care \n \n 😷Cover your nose and mouth with a nose mask \n \n 🚿Wash your hands often'
            
            msg.body(message)
            responded = True
            print(message)
            
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            date2 = now.strftime("%Y/%m/%d %H")
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('7')
            ref = db.reference(sender).child('drConversationDone').set('True')
            
            ref = db.reference(sender).child('response').child(f'{date2}').child('visit').set(f'True')
        
        
        
        elif previousConversationStep == '7' and ('no' in incoming_msg or incoming_msg == 'n') and 'not' not in incoming_msg:
        
        
            message = f'Sorry you\’re feeling 🤢ill. 🏠Stay at home and monitor your symptoms 🥵. ☎️Call a health practitoner if you get worse. 🧐Watch for COVID-19 symptoms. If you develop any of these 🤢symptoms or if you start to feel 🥵worse, ☎️ call your healthcare provider. \n \n ✅Here are some steps that may help you feel better and prevent the spread of COVID-19:  \n \n 🏠Stay at home and rest. \n 🥤Drink plenty of water and other clear liquids to prevent fluid loss (dehydration). \n \n 😷Cover your nose and mouth with a nose mask \n \n 🚿Wash your hands often'
            
            msg.body(message)
            responded = True
            print(message)
            
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            date2 = now.strftime("%Y/%m/%d %H")
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('7')
            ref = db.reference(sender).child('drConversationDone').set('True')
            
            ref = db.reference(sender).child('response').child(f'{date2}').child('visit').set(f'False')
            
        elif previousConversationStep == '7':
        
            message = 'Ooops.. 🤔, i do not understand your last message, please read the question again and ↪️ reply with a ✅Yes or ❌No.'
            
            msg.body(message)
            responded = True
            print(message)
            
            
            now = datetime.now()
            date = now.strftime("%Y/%m/%d %H:%M:%S")
            
            
            ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
            ref = db.reference(sender).child('previousConversationStep').set('7')
            ref = db.reference(sender).child('drConversationDone').set('False')
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    else:
        #not talking to the dr
        print('enntered here too')
    
    
        #predict intent
        intentName = result['intent']['name']
        confidence = result['intent']['confidence']
        entity = result['entities']
        
        print(intentName, entity, int(confidence*100))
        
        if int(confidence*100) >= 60:
            print('connfidence reached')
            if intentName == 'greeting':
                
                message = ''
                sender = request.values.get('From', '').split(':')[1]
                
                pn = phonenumbers.parse(sender)
                countryCode = pn.country_code
                
                
                country = pycountry.countries.get(alpha_2=region_code_for_number(pn))
                nameCountry = country.name
                
                greetingsList = ['Hi, i trust you are doing good ✌️.', f'Hello, hope you are enjoying your stay in {nameCountry}']
                otherMessage = 'How may i help you? I can provide you with \n \n - 📰News on Coronavirus from around the world \n \n - 📊Live stats on Coronavirus in various countries \n \n - 👩‍⚕️Doctor Ore can walk you through our Coronavirus symptom checker, provide you with 🥴tips and answer some ❔questions about the virus'
                
                
                message = f'{greetingsList[randrange((len(greetingsList)))]} \n \n {otherMessage}'

                responded = True
                
            elif intentName == 'get_news':
                print('step1')
                
                message = ''
                newsConversationStarters = ["I just read the news about 30 minutes ago so i think i can help you with that", "Sure i can fill you in on what is happening about Coronavirus around the world", "Yea i was trained to always keep tabs on what's happening around the world so i can help you with some news"]
                
                
                thanks = ["I am always happy to be of help", "Anything to serve you boss", "I need to run down to my boss to tell him i made you happy today", "Hmmmm, someone thinks i was helpful, thanks for the compliment", "Anything to help you, anytime", "Alright i am glas i could help", "Don't mention it man, i was built for this stuff"]
                
                smileyBox = ['🤔', '🤭', '😷', '🙎‍♀️', '🙎‍♂️', '🕶', '🌎', '🌍', '🚨', '🏥', '📈', '📉', '📊', '📜', '📃', '📄', '🗞', '📌', '⭕', '💭' ]
                
                sender = request.values.get('From', '').split(':')[1]
                try:
                    commands = data['commands'][sender]
                except:
                    commands = False
                        
                        
                        
                        
                news = data['news']
                news = news[1:6]
                        
                message = f'{newsConversationStarters[randrange((len(newsConversationStarters)-1))]} \n \n'
                index = 1
                for item in news:
                    for key, value in item.items():
                        if key == 'title':
                            title = value
                        elif key == 'description':
                            description = value
                        elif key == 'date':
                            date = value
                        elif key == 'url':
                            link = value
                            
                    message += f'\n {index}: {smileyBox[randrange((len(smileyBox)-1))]} {title} \n'
                    index+=1
                            
                
                ref = db.reference('commands').child(sender).set(6)
                ref = db.reference('lastCommandNews').child(sender).set('allNews')
                message += f'\n \n ↪️Reply with the number of the news you will like to read more about or ↪️reply with \'more\' to get more headlines'
                                
                responded = True

                
                
            elif intentName == 'get_news_country':
                
                message = ''
                entity = []
                for item in result['entities']:
                    entity.append(item['value'])
                    
                    
                    
                newsConversationStarters = ["I just read the news about 30 minutes ago so i think i can help you with that", "Sure i can fill you in on what is happening about Coronavirus around the world", "Yea i was trained to always keep tabs on what's happening around the world so i can help you with some news"]
                 
                 
                thanks = ["I am always happy to be of help", "Anything to serve you boss", "I need to run down to my boss to tell him i made you happy today", "Hmmmm, someone thinks i was helpful, thanks for the compliment", "Anything to help you, anytime", "Alright i am glas i could help", "Don't mention it man, i was built for this stuff"]
                 
                smileyBox = ['🤔', '🤭', '😷', '🙎‍♀️', '🙎‍♂️', '🕶', '🌎', '🌍', '🚨', '🏥', '📈', '📉', '📊', '📜', '📃', '📄', '🗞', '📌', '⭕', '💭' ]
                 
                sender = request.values.get('From', '').split(':')[1]

                 
                entity = nltk.word_tokenize(' '.join(entity))
                entity = nltk.pos_tag(entity)
                countries = []
                print(f'this is the entitiy {entity}')
                for item in entity:
                    if item[1][:2] == 'NN':
                        countries.append(item[0])
                 
                 
                
                 
                if countries == []:
                    message = f'🤔Oops..., i am sorry i don\'t have any news from this country '
                    return message
                else:
                    message = ''
                     
                    for country in countries:
                         
                        try:
                            news = data['country_news'][f'{country}_news']
                        except:
                             
                            try:
                                country = data['city_to_country'][country][country]
                                news = data['country_news'][f'{country}_news']
                            except:
                                news = False
                             
                         
                        if news != False:
                            index = 1

                            for item in news[1:6]:
                                for key, value in item.items():
                                    if key == 'title':
                                        title = value
                                    elif key == 'description':
                                        description = value
                                    elif key == 'date':
                                        date = value
                                    elif key == 'url':
                                        link = value
                                         
                                message += f'\n {index}: {smileyBox[randrange((len(smileyBox)-1))]} {title} \n'
                                index+=1
                                         
                             
                            ref = db.reference('commands').child(sender).set(6)
                            ref = db.reference('lastCommandNews').child(sender).set(f'{country}')
                         
                    if message == '':
                        message += f'🤔Oops..., i am sorry i don\'t have any news from this country '
                        return message
                    else:
                        message = f'{newsConversationStarters[randrange((len(newsConversationStarters)-1))]} \n \n' + message + f'\n \n ↪️Reply with the number of the news you will like to read more about or ↪️reply with \'more\' to get more headlines'
                        
                responded = True
                
            elif intentName == 'get_statsAll':
                print('get_statsAll')
            
            elif intentName == 'get_statsCountry':
                print('get_statsCountry')
                
            elif intentName == 'get_goodNews':
                print('get_goodNews')
                
            elif intentName == 'get_economyBounce':
                print('get_economyBounce')
                
            elif intentName == 'call_cdc':
                print('call_cdc')
                
            elif intentName == 'symptoms':
                symptom = []
                for item in result['entities']:
                    symptom.append(item['value'])
                    
                    
                sender = request.values.get('From', '').split(':')[1]
                
            
                now = datetime.now()
                date = now.strftime("%Y/%m/%d %H:%M:%S")

                message = '⚠️DISCLAIMER \n This bot is just to assist 🖐 you in making the decision to seek appropriate medical care 🏥 and you are still expected to use your level of judgement 🤔. The bot was not developed to diagnose or treat any disease, including Coronavirus. \n \n ↪️Reply with \'Agree\' to proceed.'
                
                now = datetime.now()
                date = now.strftime("%Y/%m/%d %H:%M:%S")
                
                ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
                ref = db.reference(sender).child('previousConversationStep').set('1')
                ref = db.reference(sender).child('drConversationDone').set('False')
                
               
                responded = True
                
            elif intentName == 'symptom_question':
            
                symptom = []
                for item in result['entities']:
                    symptom.append(item['value'])
                
                
                symptoms = ['fever', 'feverish', 'cough', 'coughing', 'tiredness', 'tired', 'aches', 'pains', 'ache', 'pain', 'throat', 'diarrhoea', 'conjunctivitis', 'headache', 'taste', 'smell', 'rash', 'skin', 'discolouration', 'discolour', 'fingers', 'finger', 'toes', 'toes', 'chills', 'chill']
                   
                seriousSymptoms = ['breath', 'breathing', 'shortness', 'chest', 'pain', 'pressure', 'speech', 'movement', 'move', 'speak']
                   
                   
                if symptom != []:
                    [x.lower() for x in symptom]
                    
                setIntersection = set(symptom).intersection(symptoms)
                setIntersection2 = set(symptom).intersection(seriousSymptoms)
                
                setIntersection = list(setIntersection)
                setIntersection2 = list(setIntersection2)

                if len(setIntersection) == 0 and len(setIntersection2) == 0:
                    message = 'I don\'t think 🤔 this is a symptom of COVID-19, this are some other 🤢symptoms accroding 🏥WHO \n \n *Most common symptoms:* \n 🤒fever \n 😤dry cough \n 🤭tiredness \n \n *Less common symptoms:* \n 🤕aches and pains \n 🥵sore throat \n 🤮diarrhoea \n 😶conjunctivitis \n 🤕headache \n 👅loss of taste or smell \n 🤦‍♀️a rash on skin \n 🖐discolouration of fingers or toes \n \n *Serious symptoms:* \n 👃difficulty breathing or shortness of breath \n 😭chest pain or pressure \n 😧loss of speech or movement'
                    
                else:
                    message = 'Yes i think this is a symptom of COVID-19 🤔, this are some 🤢symptoms accroding 🏥WHO \n \n *Most common symptoms:* \n 🤒fever \n 😤dry cough \n 🤭tiredness \n \n *Less common symptoms:* \n 🤕aches and pains \n 🥵sore throat \n 🤮diarrhoea \n 😶conjunctivitis \n 🤕headache \n 👅loss of taste or smell \n 🤦‍♀️a rash on skin \n 🖐discolouration of fingers or toes \n \n *Serious symptoms:* \n 👃difficulty breathing or shortness of breath \n 😭chest pain or pressure \n 😧loss of speech or movement'
                    
                    
                responded = True
                    
                    
            #Stick to saying what is a keyword in the symptom intersection symptomList  is a symptom incase the person added a non symptom
            #and what is not in the intersection is not
            #or if list is empty without a keyword say no it is not a symptom
            
            

            
            elif intentName == 'get_tips':
                print('get_tips')
            
            elif intentName == 'help':
                print('help')
        
            
        else:
        
            msg.body('Ooops... 🤔, i dont think i understand your last message. \n \n I can only help you with 📄news and 📊stats on coronavirus, remind you to 🚿wash your hands, run a 👩‍⚕️selfchecker to advise you wether you should get tested or not and also i know the 🤢symptoms of coronavirus and can give you the CDC ☎️contact of your country, sorry!')
            responded = True
            print('Ooops... 🤔, i dont think i understand your last message. \n \n I can only help you with 📄news and 📊stats on coronavirus, remind you to 🚿wash your hands, run a 👩‍⚕️selfchecker to advise you wether you should get tested or not and also i know the 🤢symptoms of coronavirus and can give you the CDC ☎️contact of your country, sorry! 12')

        
        
    if not responded:
        msg.body('I can only help you with 📄news and 📊stats on coronavirus, remind you to 🚿wash your hands, run a 👩‍⚕️selfchecker to advise you wether you should get tested or not and also i know the 🤢symptoms of coronavirus and can give you the CDC ☎️contact of your country, sorry!')
        print('I can only help you with 📄news and 📊stats on coronavirus, remind you to 🚿wash your hands, run a 👩‍⚕️selfchecker to advise you wether you should get tested or not and also i know the 🤢symptoms of coronavirus and can give you the CDC ☎️contact of your country, sorry! 34')
    
    print(message)
    msg.body('hi')
    return str(resp)





def getNews():

    #no country in specific show all coronavirus news
    
    newsConversationStarters = ["I just read the news about 30 minutes ago so i think i can help you with that", "Sure i can fill you in on what is happening about Coronavirus around the world", "Yea i was trained to always keep tabs on what's happening around the world so i can help you with some news"]
    
    
    thanks = ["I am always happy to be of help", "Anything to serve you boss", "I need to run down to my boss to tell him i made you happy today", "Hmmmm, someone thinks i was helpful, thanks for the compliment", "Anything to help you, anytime", "Alright i am glas i could help", "Don't mention it man, i was built for this stuff"]
    
    smileyBox = ['🤔', '🤭', '😷', '🙎‍♀️', '🙎‍♂️', '🕶', '🌎', '🌍', '🚨', '🏥', '📈', '📉', '📊', '📜', '📃', '📄', '🗞', '📌', '⭕', '💭' ]
    
         
    firebase_instance = firebase.FirebaseApplication('https://free-from-corona-virus.firebaseio.com/')
    data = firebase_instance.get('/', None)
        
    sender = request.values.get('From', '').split(':')[1]
    try:
        commands = data['commands'][sender]
    except:
        commands = False
            
            
            
            
    news = data['news']
    news = news[1:6]
            
    message = f'{newsConversationStarters[randrange((len(newsConversationStarters)-1))]} \n \n'
    index = 1
    for item in news:
        for key, value in item.items():
            if key == 'title':
                title = value
            elif key == 'description':
                description = value
            elif key == 'date':
                date = value
            elif key == 'url':
                link = value
                
        message += f'\n {index}: {smileyBox[randrange((len(smileyBox)-1))]} {title} \n'
        index+=1
                
    
    ref = db.reference('commands').child(sender).set(6)
    ref = db.reference('lastCommandNews').child(sender).set('allNews')
    message += f'\n \n ↪️Reply with the number of the news you will like to read more about or ↪️reply with \'more\' to get more headlines'
        

    
    return message
    

def getNewsCountry(entity):

    newsConversationStarters = ["I just read the news about 30 minutes ago so i think i can help you with that", "Sure i can fill you in on what is happening about Coronavirus around the world", "Yea i was trained to always keep tabs on what's happening around the world so i can help you with some news"]
    
    
    thanks = ["I am always happy to be of help", "Anything to serve you boss", "I need to run down to my boss to tell him i made you happy today", "Hmmmm, someone thinks i was helpful, thanks for the compliment", "Anything to help you, anytime", "Alright i am glas i could help", "Don't mention it man, i was built for this stuff"]
    
    smileyBox = ['🤔', '🤭', '😷', '🙎‍♀️', '🙎‍♂️', '🕶', '🌎', '🌍', '🚨', '🏥', '📈', '📉', '📊', '📜', '📃', '📄', '🗞', '📌', '⭕', '💭' ]
    
    sender = request.values.get('From', '').split(':')[1]

    firebase_instance = firebase.FirebaseApplication('https://free-from-corona-virus.firebaseio.com/')
    data = firebase_instance.get('/', None)
    
    
    entity = nltk.word_tokenize(' '.join(entity))
    entity = nltk.pos_tag(entity)
    countries = []
    print(f'this is the entitiy {entity}')
    for item in entity:
        if item[1][:2] == 'NN':
            countries.append(item[0])
    
    
   
    
    if countries == []:
        message = f'🤔Oops..., i am sorry i don\'t have any news from this country '
        return message
    else:
        message = ''
        
        for country in countries:
            
            try:
                news = data['country_news'][f'{country}_news']
            except:
                
                try:
                    country = data['city_to_country'][country][country]
                    news = data['country_news'][f'{country}_news']
                except:
                    news = False
                
            
            if news != False:
                index = 1

                for item in news[1:6]:
                    for key, value in item.items():
                        if key == 'title':
                            title = value
                        elif key == 'description':
                            description = value
                        elif key == 'date':
                            date = value
                        elif key == 'url':
                            link = value
                            
                    message += f'\n {index}: {smileyBox[randrange((len(smileyBox)-1))]} {title} \n'
                    index+=1
                            
                
                ref = db.reference('commands').child(sender).set(6)
                ref = db.reference('lastCommandNews').child(sender).set(f'{country}')
            
        if message == '':
            message += f'🤔Oops..., i am sorry i don\'t have any news from this country '
            return message
        else:
            message = f'{newsConversationStarters[randrange((len(newsConversationStarters)-1))]} \n \n' + message + f'\n \n ↪️Reply with the number of the news you will like to read more about or ↪️reply with \'more\' to get more headlines'
            return message
                
            

    



def doIHaveCoronavirusResponse(symptoms, incoming_msg):

    firebase_instance = firebase.FirebaseApplication('https://free-from-corona-virus.firebaseio.com/')
    data = firebase_instance.get('/', None)
               
    sender = request.values.get('From', '').split(':')[1]
    
    '''
    try:
        previousConversationDate = data[sender]['previousConversationDate']
    except:
        previousConversationDate = False
        
    try:
        previousConversationStep = data[sender]['previousConversationStep']
    except:
        previousConversationStep = False

    
    conversation steps
    1 - Disclaimer
    2 - Introduction
    3 - BIODATA
        3A - Country
        3B - Who you are asking for
        3C - Sex
        3D - Age
        3E - Gender
    4 - Life threatning symptoms
    5A - No Life threatning Symptom
    5B - No Symptom
    6 - Mild and no trouble breathing
    7 - Where you have been
    

    now = datetime.now()
    dateNow = now.strftime("%Y/%m/%d %H:%M:%S")
    datetimeFormat = '%Y/%m/%d %H:%M:%S'
    '''
    
    now = datetime.now()
    date = now.strftime("%Y/%m/%d %H:%M:%S")

    message = '⚠️DISCLAIMER \n This bot is just to assist 🖐 you in making the decision to seek appropriate medical care 🏥 and you are still expected to use your level of judgement 🤔. The bot was not developed to diagnose or treat any disease, including Coronavirus. \n \n ↪️Reply with \'Agree\' to proceed.'
    
    now = datetime.now()
    date = now.strftime("%Y/%m/%d %H:%M:%S")
    
    ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
    ref = db.reference(sender).child('previousConversationStep').set('1')
    ref = db.reference(sender).child('drConversationDone').set('False')
    
    
    '''
     
    try:
        dateBefore = data[sender]['previousConversationDate']
    except:
        dateBefore = '2017/05/28 19:02:01'
        
        
    diff = dt.datetime.strptime(dateNow, datetimeFormat)\
        - dt.datetime.strptime(dateBefore, datetimeFormat)

    print("Seconds:", diff.seconds )

    if previousConversationStep == False:
        message = '⚠️DISCLAIMER /n This bot is just to assist 🖐 you in making the decision to seek appropriate medical care 🏥 and you are still expected to use your level of judgement 🤔. The bot was not developed to diagnose or treat any disease, including Coronavirus. /n /n ↪️Reply with \'Agree\' to proceed.'
        
        now = datetime.now()
        date = now.strftime("%Y/%m/%d %H:%M:%S")
        
        ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
        ref = db.reference(sender).child('previousConversationStep').set('1')
        ref = db.reference(sender).child('drConversationDone').set('False')
        
        
        
        return message

    elif previousConversationDate == False:
        message = '⚠️DISCLAIMER /n This bot is just to assist 🖐 you in making the decision to seek appropriate medical care 🏥 and you are still expected to use your level of judgement 🤔. The bot was not developed to diagnose or treat any disease, including Coronavirus. /n /n ↪️Reply with \'Agree\' to proceed.'
        
        now = datetime.now()
        date = now.strftime("%Y/%m/%d %H:%M:%S")
        
        ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
        ref = db.reference(sender).child('previousConversationStep').set('1')
        ref = db.reference(sender).child('drConversationDone').set('False')
        
        return message


    now = datetime.now()
    dateNow = now.strftime("%Y/%m/%d %H:%M:%S")

     
    diff = dt.datetime.strptime(dateNow, datetimeFormat)\
        - dt.datetime.strptime(dateBefore, datetimeFormat)

    if diff.seconds > 300:
        message = '⚠️DISCLAIMER /n This bot is just to assist 🖐 you in making the decision to seek appropriate medical care 🏥 and you are still expected to use your level of judgement 🤔. The bot was not developed to diagnose or treat any disease, including Coronavirus. /n /n ↪️Reply with \'Agree\' to proceed.'
               
        now = datetime.now()
        date = now.strftime("%Y/%m/%d %H:%M:%S")
               
        ref = db.reference(sender).child('previousConversationDate').set(f'{date}')
        ref = db.reference(sender).child('previousConversationStep').set('1')
        ref = db.reference(sender).child('drConversationDone').set('False')
          
    '''
    return message

   
                
                
def symptomQuestion(symptom):

    symptoms = ['fever', 'feverish', 'cough', 'coughing', 'tiredness', 'tired', 'aches', 'pains', 'ache', 'pain', 'throat', 'diarrhoea', 'conjunctivitis', 'headache', 'taste', 'smell', 'rash', 'skin', 'discolouration', 'discolour', 'fingers', 'finger', 'toes', 'toes', 'chills', 'chill']
       
    seriousSymptoms = ['breath', 'breathing', 'shortness', 'chest', 'pain', 'pressure', 'speech', 'movement', 'move', 'speak']
       
       
    if symptom != []:
        [x.lower() for x in symptom]
        
    setIntersection = set(symptom).intersection(symptoms)
    setIntersection2 = set(symptom).intersection(seriousSymptoms)
    
    setIntersection = list(setIntersection)
    setIntersection2 = list(setIntersection2)

    if len(setIntersection) == 0 and len(setIntersection2) == 0:
        message = 'I don\'t think 🤔 this is a symptom of COVID-19, this are some 🤢symptoms accroding 🏥WHO \n \n *Most common symptoms:* \n 🤒fever \n 😤dry cough \n 🤭tiredness \n \n *Less common symptoms:* \n 🤕aches and pains \n 🥵sore throat \n 🤮diarrhoea \n 😶conjunctivitis \n 🤕headache \n 👅loss of taste or smell \n 🤦‍♀️a rash on skin \n 🖐discolouration of fingers or toes \n \n *Serious symptoms:* \n 👃difficulty breathing or shortness of breath \n 😭chest pain or pressure \n 😧loss of speech or movement'
        return message
    else:
        message = 'Yes i think this is a symptom of COVID-19 🤔, this are some 🤢symptoms accroding 🏥WHO \n \n *Most common symptoms:* \n 🤒fever \n 😤dry cough \n 🤭tiredness \n \n *Less common symptoms:* \n 🤕aches and pains \n 🥵sore throat \n 🤮diarrhoea \n 😶conjunctivitis \n 🤕headache \n 👅loss of taste or smell \n 🤦‍♀️a rash on skin \n 🖐discolouration of fingers or toes \n \n *Serious symptoms:* \n 👃difficulty breathing or shortness of breath \n 😭chest pain or pressure \n 😧loss of speech or movement'
        return message



def greeting():
    sender = request.values.get('From', '').split(':')[1]
    
    pn = phonenumbers.parse(sender)
    countryCode = pn.country_code
    
    
    country = pycountry.countries.get(alpha_2=region_code_for_number(pn))
    nameCountry = country.name
    
    greetingsList = ['Hi, i trust you are doing good ✌️.', f'Hello, hope you are enjoying your stay in {nameCountry}']
    otherMessage = 'How may i help you? I can provide you with \n \n - 📰News on Coronavirus from around the world \n \n - 📊Live stats on Coronavirus in various countries \n \n - 👩‍⚕️Doctor Ore can walk you through our Coronavirus symptom checker, provide you with 🥴tips and answer some ❔questions about the virus'
    
    
    message = f'{greetingsList[randrange((len(greetingsList)))]} \n \n {otherMessage}'
    
    return message
   
   
   



def getNER(sent):
    sent = nltk.word_tokenize(sent)
    sent = nltk.pos_tag(sent)
    for item in sent:
        if item[1][:2] == 'NN':
            return item[1]
    return None


if __name__ == '__main__':
    app.run()













