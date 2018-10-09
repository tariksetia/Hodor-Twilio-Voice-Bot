import urllib
from flask import request
from hodor.entity.conv import Conversation
import hodor.entity.twilio_unit as twilio_response
from hodor.utils.logger import log
from hodor.utils.luisnlp import luis

from . import reset_password_api

@reset_password_api.route('/gather-phone-number', methods=['GET','POST'])
def gather_contact_number():
    user_speech = request.form.get('SpeechResult',None)
    caller = request.form.get('Caller')
    input_digits = request.form.get('Digits', None)
    data = input_digits or user_speech

    uid = request.form.get('CallSid')
    payload = request.args.items()
    payload = { x[0]:x[1] for x in payload}
    session = Conversation.from_uid(uid)
    
    u_phone_number = payload.get('u_phone_number', None)
    u_phone_number = u_phone_number if u_phone_number else session.get_param('u_phone_number').decode()
    print("u_phone_number = "+ str(u_phone_number))

    ntry = int(request.args.get('ntry','0'))    
    if ntry > 4:
        text = "Maximum Number of Retries reached. Contecting to Service Desk. Please Wait"
        resp = twilio_response.Hangup(text=text)
        return str(resp.twiml)

    ntry += 1

    if payload.get('ntry'):
        del payload['ntry']

    if not data:
        text = "I didn't quite catch that. Please enter your 10 digit phone number again."
        url = '/api/reset-password/gather-phone-number?ntry={}'.format(str(ntry))
        if payload:
            url = url + '&' + urllib.parse.urlencode(payload)
        resp = twilio_response.GatherSpeech(text, url)
        log(caller,'bot', resp.text, uid)
        return str(resp.twiml)
    
    
    if data:
        print("data = " + data)
        log(caller,'caller', data, uid)
        gather_contact, text = parseContact(data)
        print("gather_contact = "+ str(gather_contact))
        if gather_contact is None:
            url = '/api/reset-password/gather-phone-number?ntry={}'.format(str(ntry))
            if payload: url += '&' + urllib.parse.urlencode(payload)
            resp = twilio_response.GatherSpeech(text, url)
            log(caller,'bot', resp.text, uid)
            return str(resp.twiml)
        
        spaced_contact_number = ''.join([i + ' ' for i in u_phone_number])

        if str(gather_contact).lower() == u_phone_number.lower():
            if payload.get('luis_postal_code'):
                resp = twilio_response.Redirect()
                spaced_contact_number = ''.join([i + ' ' for i in u_phone_number])
                resp.text = "You contact number, {} is correct. Now I will be validating postal code".format(spaced_contact_number)
                url = '/api/reset-password/check-postal-code?postal_code={}'.format(payload.get('luis_postal_code'))
                if payload:
                    url = url + '&' + urllib.parse.urlencode(payload)
                resp.url = url
                log(caller,'bot', resp.text, uid)
                return str(resp.twiml)
            else:
                resp = twilio_response.GatherSpeech()
                resp.text = "You contact number  {} is correct. Please tell me your postal code".format(spaced_contact_number)
                url = '/api/reset-password/gather-postal-code'
                if payload:
                    url = url + '?' + urllib.parse.urlencode(payload)
                resp.url = url
                log(caller,'bot', resp.text, uid)
                return str(resp.twiml)
        else:
            text = "Your phone number {} did not match with active directory data. Please enter it again".format(spaced_contact_number)
            url = '/api/reset-password/gather-phone-number?ntry={}'.format(str(ntry))
            if payload:
                url = url + '&' + urllib.parse.urlencode(payload)
            resp = twilio_response.GatherSpeech(text, url)
            log(caller,'bot', resp.text, uid)
            return str(resp.twiml)



        


def parseContact(data):
    entities = luis.analyze(data).entities
    contact = filter(lambda x: x.type == 'builtin.phonenumber', entities)
    contact = list(contact)
    if len(contact) == 0:
        return None, "I could not recognize any contact nymber ID. You can also enter it using keypad. Please try again!"

    contact = contact[0]
    contact = contact.resolution.get('value')
    contact = ''.join(contact.split(' '))
    if len(contact) != 10:
        return None, "This is an invalid cotact number. It has to be 10 digits. Please try again!"

    return int(contact.strip()), None
    