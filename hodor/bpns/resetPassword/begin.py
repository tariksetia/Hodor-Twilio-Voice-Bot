from flask import request
from hodor.entity.conv import Conversation
import hodor.entity.twilio_unit as twilio_response
from hodor.utils.logger import log
from . import reset_password_api
import urllib


@reset_password_api.route('/begin', methods=['GET','POST'])
def begin():
    uid = request.form.get("CallSid")
    caller = request.form.get('Caller')
    conversation = Conversation.from_uid(uid)
    conversation.set_param("intent", "resetPassword")
    
    url = '/api/reset-password/gather-portal-id?ntry=1'
    
    payload = None
    entities = list(filter(lambda x: 'luis' in x[0] , request.args.items()))
    entities = { x[0]:x[1] for x in entities}
    if entities.items():
        payload = urllib.parse.urlencode(entities)
    for entity in entities.items():
        conversation.set_param(entity[0],entity[1])

    if entities.get('luis_portal_id'):
        resp = twilio_response.Redirect()
        resp.text = "Sure! I can help you with that. Let me check your portal ID against active directory data"
        url = '/api/reset-password/check-portal-id?portalId={}'.format(entities.get('luis_portal_id'))
        url = url + '&' + payload
        resp.url = url
        log(caller,'bot', resp.text, uid)
        return str(resp.twiml)
    else:
        text =  "Sure! I can help you with password reset. What is your 6 digit portal ID."

    resp = twilio_response.GatherSpeech()
    resp.url = url
    resp.text = text
    log(caller,'bot', resp.text, uid)
    return str(resp.twiml)

