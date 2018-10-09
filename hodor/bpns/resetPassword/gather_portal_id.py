import urllib
from flask import request
from hodor.entity.conv import Conversation
import hodor.entity.twilio_unit as twilio_response
from hodor.utils.luisnlp import luis
from hodor.utils.logger import log

from . import reset_password_api

@reset_password_api.route('/gather-portal-id', methods=['GET','POST'])
def gather_portal_id():
    
    uid = request.form.get("CallSid")
    caller = request.form.get('Caller')
    session = Conversation.from_uid(uid)

    user_speech = request.form.get('SpeechResult',None)
    input_digits = request.form.get('Digits', None)
    data = input_digits or user_speech
    ad_error = request.args.get('ad_error', False)

    ntry = int(request.args.get('ntry','0'))
    invalid = request.args.get('invalid',False)
    if ntry > 4:
        text = "Maximum Number of Retries reached. Contecting to Service Desk. Please Wait"
        resp = twilio_response.Hangup(text=text)
        return str(resp.twiml)

    ntry += 1


    luis_portal_id = session.get_param("luis_portal_id")
    if luis_portal_id:
        luis_portal_id = luis_portal_id.decode()
        resp = twilio_response.Redirect()
        resp.url = '/api/reset-password/check-portal-id?portalId={}&ntry={}'.format(str(luis_portal_id),str(ntry))
        return str(resp.twiml)

    if ad_error:
        text = request.args.get('error_text','Something went wrong while feteching data from AD.')
        text += 'Please enter your 6 digit portal id again!'
        url = '/api/reset-password/gather-portal-id?ntry={}'.format(str(ntry))
        resp = twilio_response.GatherSpeech(text, url)
        log(caller,'bot', resp.text, uid)
        return str(resp.twiml)

    if not data:
        text = "I didn't quite catch that. Please enter your portal ID again."
        url = '/api/reset-password/gather-portal-id?ntry={}'.format(str(ntry))
        resp = twilio_response.GatherSpeech(text, url)
        log(caller,'bot', resp.text, uid)
        return str(resp.twiml)
    
    
    if data:
        print("data = " + data)
        log(caller, caller, data, uid)
        portalId, text = parsePortalId(data)
        print(portalId)
        if portalId is None:
            url = '/api/reset-password/gather-portal-id?ntry={}'.format(str(ntry))
            resp = twilio_response.GatherSpeech(text, url)
            log(caller,'bot', resp.text, uid)
            return str(resp.twiml)
        
        resp = twilio_response.Redirect(text=text)
        url = '/api/reset-password/check-portal-id?portalId={}&ntry={}'.format(str(portalId),str(ntry))
        resp.url = url
        log(caller,'bot', resp.text, uid)
        return str(resp.twiml)


        


def parsePortalId(data):
    entities = luis.analyze(data).entities
    portalId = filter(lambda x: x.type == 'builtin.number', entities)
    portalId = list(portalId)
    if len(portalId) == 0:
        return None, "I could not find any portal ID. You can also enter it using keypad. Please try again!"

    portalId = portalId[0]
    portalId = portalId.resolution.get('value')
    portalId = ''.join(portalId.split(' '))
    if len(portalId) != 6:
        return None, "This is an invalid portal Id. It has to be 6 digits. Please try again!"

    return int(portalId), "Please wait while I check if {} is a valid portal ID".format(portalId)
    