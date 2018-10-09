import urllib
from flask import request
from hodor.entity.conv import Conversation
import  hodor.entity.twilio_unit as twilio_response
from hodor.utils.luisnlp import luis
from hodor.utils.logger import log
from . import reset_password_api

@reset_password_api.route('/gather-postal-code', methods=['GET','POST'])
def gather_postal_code():
    uid = request.form.get('CallSid')
    caller = request.form.get('Caller') 
    user_speech = request.form.get('SpeechResult',None)
    input_digits = request.form.get('Digits', None)
    data = input_digits or user_speech
    session = Conversation.from_uid(uid)

    payload = request.args.items()
    payload = { x[0]:x[1] for x in payload}

    u_postal_code = payload.get('u_postal_code',None)
    u_postal_code = u_postal_code if u_postal_code else session.get_param('u_postal_code').decode()
    
    
    print("u_postal_code = "+ str(u_postal_code))

    ntry = int(request.args.get('ntry','0'))
    
    if ntry > 4:
        text = "Maximum Number of Retries reached. Contecting to Service Desk. Please Wait"
        resp = twilio_response.Hangup(text=text)
        return str(resp.twiml)

    ntry += 1

    if payload.get('ntry'):
        del payload['ntry']

    if not data:
        text = "I didn't quite catch that. Please enter your 6 digit postal or zip code again."
        url = '/api/reset-password/gather-postal-code?ntry={}'.format(str(ntry))
        resp = twilio_response.GatherSpeech(text, url)
        return str(resp.twiml)
    
    
    if data:
        print("data = " + data)
        log(caller,caller, data, uid)
        gather_postal_code, text = parseContact(data)
        print("gather_postal_code = "+ str(gather_postal_code))
        if gather_postal_code is None:
            url = '/api/reset-password/gather-postal-code?ntry={}'.format(str(ntry))
            resp = twilio_response.GatherSpeech(text, url)
            log(caller,'bot', resp.text, uid)
            return str(resp.twiml)
        
        if str(gather_postal_code).lower() == u_postal_code.lower():
            resp = twilio_response.GatherSpeech()
            resp.text = "You postal code, , {} is correct".format(u_postal_code)
            resp.url = '/api/reset-password/reset-ad-password'
            log(caller,'bot', resp.text, uid)
            return str(resp.twiml)
        else:
            text = "Your postal-code did not match with active directory data. Please enter it again"
            url = '/api/reset-password/gather-postal-code?ntry={}'.format(str(ntry))
            resp = twilio_response.GatherSpeech(text, url)
            log(caller,'bot', resp.text, uid)
            return str(resp.twiml)



        


def parseContact(data):
    entities = luis.analyze(data).entities
    zip_ = filter(lambda x: x.type == 'builtin.number', entities)
    zip_ = list(zip_)
    if len(zip_) == 0:
        return None, "I could not recognize any postal code. You can also enter it using keypad. Please try again!"

    zip_ = zip_[0]
    zip_ = zip_.resolution.get('value')
    zip_ = ''.join(zip_.split(' '))
    if len(zip_) != 6:
        return None, "This is an invalid postal code. It has to be 6 digits. Please try again!"

    return zip_, None
    