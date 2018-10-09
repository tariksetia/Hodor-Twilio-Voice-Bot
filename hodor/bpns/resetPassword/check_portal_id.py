import urllib
import hodor.entity.twilio_unit as twilio_response
from flask import request
from hodor.entity.conv import Conversation
from hodor.utils.logger import log
from hodor.bpns.resetPassword.utils.graph import Graph

from . import reset_password_api

@reset_password_api.route('/check-portal-id', methods=['GET','POST'])
def check_portal_id():
    uid = request.form.get("CallSid")
    caller = request.form.get('Caller')
    entities = list(filter(lambda x: 'luis' in x[0] , request.args.items()))
    portalId = int(request.args.get('portalId', '0'))
    ntry = int(request.args.get('ntry','2'))
    payload = None
    error = False
    skip_list = {}

    session = Conversation.from_uid(uid)
    entities = { x[0]:x[1] for x in entities}
    ad = Graph(portalId)
    
    try:
        user_data = ad.getUserData()
        user_data = { 'u_'+k : v for k,v in user_data.items() }
        print(user_data)
        user_data['u_portal_id'] = portalId
        url_user_data = urllib.parse.urlencode(user_data)
        payload = {**entities, **user_data}
        for item in user_data.items():
            key, val = item
            session.set_param(key, val)
    except Exception as e:
        error = True
        text = str(e)
        print(text)
        pass
    
    if error:
        url = '/api/reset-password/gather-portal-id?ntry={}&ad_error=True'.format(str(ntry))
        resp = twilio_response.Redirect(url=url)
        session.del_param('luis_portal_id')
        return str(resp.twiml)
    
    if entities.get('luis_city'):
        resp = twilio_response.Redirect()
        resp.text = "Okay! {} your portal ID is correct. Let me validate your city".format(user_data.get('u_name'))
        url = '/api/reset-password/check-city?'.format(entities['luis_city'])
        payload['city'] = payload['luis_city']
        payload = urllib.parse.urlencode(payload)
        if payload:
            url  = url + payload
        resp.url = url
        log(caller,'bot', resp.text, uid)
        return str(resp.twiml)
    

   
    
    resp = twilio_response.GatherSpeech()
    resp.text = "Okay! {} your portal ID is correct. Please tell me the city where you live?".format(user_data.get('u_name'))
    payload = urllib.parse.urlencode(payload)
    resp.url = '/api/reset-password/gather-city?{}'.format(payload)
    log(caller,'bot', resp.text, uid)
    return str(resp.twiml)



