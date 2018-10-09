import urllib
import hodor.entity.twilio_unit as twilio_response
from flask import request
from hodor.entity.conv import Conversation
from hodor.utils.logger import log
from hodor.bpns.resetPassword.utils.graph import Graph

from . import reset_password_api

@reset_password_api.route('/check-postal-code', methods=['GET','POST'])
def check_postal_code():
    uid = request.form.get("CallSid")
    caller = request.form.get('Caller')
    payload = request.args.items()
    payload = { x[0]:x[1] for x in payload}
    session = Conversation.from_uid(uid)

    postal_code = payload.get('postal_code')
    u_postal_code = payload.get('u_postal_code',None)
    u_postal_code = u_postal_code if u_postal_code else session.get_param(u_postal_code).decode()

    if not u_postal_code:
        #gather Postal Code
        resp = twilio_response.GatherSpeech()
        resp.text = "I could not recognize any postal code. Please try again"
        url = '/api/reset-password/gather-postal_code'
        if payload:
            url = url + '?' + urllib.parse.urlencode(payload)
        resp.url = url
        log(caller,'bot', resp.text, uid)
        return str(resp.twiml)
    
    spaced_postal_code = ''.join([ i + ' ' for i in u_postal_code])
    if postal_code == u_postal_code:
        # redirect to reset-ad-password
        resp = twilio_response.Redirect()
        resp.text = "Yaaaay! your portal code {} is correct".format(spaced_postal_code)
        url = '/api/reset-password/reset-ad-password'
        if payload:
            url = url + '?' + urllib.parse.urlencode(payload)
        resp.url = url
        log(caller,'bot', resp.text, uid)
        return str(resp.twiml)
    else:
        resp = twilio_response.GatherSpeech()
        resp.text = "Your postal code {} does not match with active directory data. Please try again".format(spaced_postal_code)
        url = '/api/reset-password/gather-postal-code'
        if payload:
            url = url + '?' + urllib.parse.urlencode(payload)
        resp.url = url
        log(caller,'bot', resp.text, uid)
        return str(resp.twiml)




