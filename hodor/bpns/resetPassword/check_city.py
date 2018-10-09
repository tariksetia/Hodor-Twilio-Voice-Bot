import urllib
import hodor.entity.twilio_unit as twilio_response
from flask import request
from hodor.entity.conv import Conversation
from hodor.utils.logger import log
from hodor.bpns.resetPassword.utils.graph import Graph

from . import reset_password_api

@reset_password_api.route('/check-city', methods=['GET','POST'])
def check_city():
    uid = request.form.get("CallSid")
    caller = request.form.get('Caller')

    payload = request.args.items()
    payload = { x[0]:x[1] for x in payload}
    session = Conversation.from_uid(uid)

    city = payload.get('city')
    u_city = payload.get('u_city',None)
    u_city = u_city if u_city else session.get_param(u_city).decode()

    if not city:
        resp = twilio_response.GatherSpeech()
        resp.text = "I could not recognize any city. Please try again"
        url = '/api/reset-password/gather-city'
        if payload:
            url = url + '?' + urllib.parse.urlencode(payload)
        resp.url = url
        log(caller,'bot', resp.text, uid)
        return str(resp.twiml)
    
    if city.lower() == u_city.lower():
        if payload.get('luis_phone_number'):
            # redirect to check_phone_number
            phone_number = payload.get('luis_phone_number')
            resp = twilio_response.Redirect()
            resp.text = "Okay! Your city {} also matches with active directory data. Now let me validate your phone number."
            url = '/api/reset-password/check-phone-number?phone_number={}'.format(phone_number)
            if payload:
                url = url + '&' + urllib.parse.urlencode(payload)
            resp.url = url
            log(caller,'bot', resp.text, uid)
            return str(resp.twiml)
        else:
            #gahter phone Number
            resp = twilio_response.GatherSpeech()
            resp.text = "Okay! Your city {} also matches with active directory data. what is your contact number?"
            url = '/api/reset-password/gather-phone-number'
            if payload:
                url = url + '?' + urllib.parse.urlencode(payload)
            resp.url = url
            log(caller,'bot', resp.text, uid)
            return str(resp.twiml)
    else:
        resp = twilio_response.GatherSpeech()
        resp.text = "Your city {} does not match with active directory data. Please try again".format(city)
        url = '/api/reset-password/gather-city'
        if payload:
            url = url + '?' + urllib.parse.urlencode(payload)
        resp.url = url
        log(caller,'bot', resp.text, uid)
        return str(resp.twiml)






