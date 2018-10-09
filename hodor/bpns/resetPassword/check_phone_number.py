import urllib
import hodor.entity.twilio_unit as twilio_response
from flask import request
from hodor.entity.conv import Conversation
from hodor.utils.logger import log
from hodor.bpns.resetPassword.utils.graph import Graph

from . import reset_password_api

@reset_password_api.route('/check-phone-number', methods=['GET','POST'])
def check_phone_number():
    uid = request.form.get("CallSid")
    caller = request.form.get('Caller')
    payload = request.args.items()
    payload = { x[0]:x[1] for x in payload}
    session = Conversation.from_uid(uid)

    phone_number = payload.get('phone_number')
    u_phone_number = payload.get('u_phone_number', None)
    u_phone_number = u_phone_number if u_phone_number else session.get_param(u_phone_number).decode()



    if not phone_number:
        resp = twilio_response.GatherSpeech()
        resp.text = "I could not recognize any contact number. Please try again"
        url = '/api/reset-password/gather-phone-number'
        if payload:
            url = url + '?' + urllib.parse.urlencode(payload)
        resp.url = url
        log(caller,'bot', resp.text, uid)
        return str(resp.twiml)
    
    if phone_number == u_phone_number:
        if payload.get('luis_postal_code'):
            postal_code = payload.get('luis_postal_code')
            resp = twilio_response.Redirect()
            resp.text = "your contact number matches with active directory data. Now let me validate your postal code."
            url = '/api/reset-password/check-postal-code?postal_code={}'.format(postal_code)
            if payload:
                url = url + '&' + urllib.parse.urlencode(payload)
            resp.url = url
            log(caller,'bot', resp.text, uid)
            return str(resp.twiml)
        else:
            #gahter zip Number
            resp = twilio_response.GatherSpeech()
            resp.text = "your contact number matches with active directory data. What is your postal Code?"
            url = '/api/reset-password/gather-postal-code'
            if payload:
                url = url + '?' + urllib.parse.urlencode(payload)
            resp.url = url
            log(caller,'bot', resp.text, uid)
            return str(resp.twiml)

    else:
        #Gather phone number
        space_phone_number = [ i + ' ' for i in phone_number]
        resp = twilio_response.GatherSpeech()
        resp.text = "Your phone number {} does not match with active directory data. Please try again".format(space_phone_number)
        url = '/api/reset-password/gather-phone-number'
        if payload:
            url = url + '?' + urllib.parse.urlencode(payload)
        resp.url = url
        log(caller,'bot', resp.text, uid)
        return str(resp.twiml)



