import urllib
import hodor.entity.twilio_unit as twilio_response
from flask import request
from hodor.entity.conv import Conversation
from hodor.utils.luisnlp import luis
from hodor.utils.logger import log
from hodor.bpns.resetPassword.utils.graph import Graph

from . import reset_password_api

@reset_password_api.route('/gather-city', methods=['GET','POST'])
def gather_city():
    data = request.form.get('SpeechResult',None)
    caller = request.form.get('Caller')
    uid = request.form.get('CallSid')
    payload = request.args.items()
    payload = { x[0]:x[1] for x in payload}
    session = Conversation.from_uid(uid)

    u_city = payload.get('u_city',None)
    u_city = u_city if u_city else session.get_param('u_city').decode()
    
    
    print("AD city = "+str(u_city))

    ntry = int(request.args.get('ntry','0'))
    if ntry > 4:
        text = "Maximum Number of Retries reached. Contecting to Service Desk. Please Wait"
        resp = twilio_response.Hangup(text=text)
        return str(resp.twiml)

    ntry += 1
    if payload.get('ntry'):
        del payload['ntry']
    
    if not data:
        text = "I didn't quite catch that. Please enter your city again."
        url = '/api/reset-password/gather-city?ntry={}'.format(str(ntry))
        if payload:
            url = url + '&' + urllib.parse.urlencode(payload)
        resp = twilio_response.GatherSpeech(text, url)
        log(caller,'bot', resp.text, uid)
        return str(resp.twiml)
    
    
    if data:
        print("data = " + data)
        log(caller,caller, data, uid)
        gather_city, text = parseCity(data)
        print("parsed city = "+str(gather_city))
        if gather_city is None:
            url = '/api/reset-password/gather-city?ntry={}'.format(str(ntry))
            if payload:
                url = url + '&' + urllib.parse.urlencode(payload)
            resp = twilio_response.GatherSpeech(text, url)
            log(caller,'bot', resp.text, uid)
            return str(resp.twiml)
        
        if gather_city.lower() == u_city.lower():

            if payload.get('luis_phone_number'):
                resp = twilio_response.Redirect()
                resp.text = "You city, {} is correct. Now I will be validating your phone number".format(u_city)
                url = '/api/reset-passord/check-phone-number?phone_number={}'.format(payload.get('luis_phone_number'))
                if payload:
                    url = url + '&' + urllib.parse.urlencode(payload)
                resp.url = url
                log(caller,'bot', resp.text, uid)
                return str(resp.twiml)
            else:
                resp = twilio_response.GatherSpeech()
                resp.text = "You city, , {} is correct. Please tell me your 10 digit contact Number".format(u_city)
                url = '/api/reset-password/gather-phone-number'
                if payload:
                    url = url + '?' + urllib.parse.urlencode(payload)
                resp.url = url
                log(caller,'bot', resp.text, uid)
                return str(resp.twiml)
        else:
            text = "Your city did not match with active directory data. Please enter you city again"
            url = '/api/reset-password/gather-city?ntry={}'.format(str(ntry))
            if payload:
                url = url + '&' + urllib.parse.urlencode(payload)
            resp = twilio_response.GatherSpeech(text, url)
            log(caller,'bot', resp.text, uid)
            return str(resp.twiml)


def parseCity(data):
    entities = luis.analyze(data).entities
    city = filter(lambda x: x.type == 'city', entities)
    city = list(city)
    if len(city) == 0:
        return None, "I could not recoginize any ciity Please try again!"

    city = city[0]
    city = city.resolution.get('values')[0]

    return city, None   