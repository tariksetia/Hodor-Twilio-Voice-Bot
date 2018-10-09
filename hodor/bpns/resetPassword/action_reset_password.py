import hodor.entity.twilio_unit as twilio_response
from . import reset_password_api
from flask import request, url_for
from hodor.entity.conv import Conversation
from hodor.utils.servicebus import send_to_queue
from hodor.utils.powerbi import log
import json

@reset_password_api.route('/reset-ad-password', methods=['GET','POST'])
def reset_password():
    resp = twilio_response.Hangup("please wait while I reset your password")
    success = request.args.get('success',False)
    failed = request.args.get('failed', False)
    text = request.args.get('text', None)
    uid = request.form.get('CallSid')
    caller = request.form.get('Caller')


    conversation = Conversation(uid)
    print(conversation.to_dict)
    u_portal_id  = conversation.get_param("u_portal_id").decode()
    name = conversation.get_param("u_name").decode()
    print("portal = " + u_portal_id)

    if success:
        resp = twilio_response.Hangup()
        s_text = "Thank you for staying with us. Your password has been reset. An email will be sent to your manager containing new password. Thank you! for using NTT service Desk. Have a nice day!"
        resp.text = request.args.get('text',s_text)
        log(caller,'bot', resp.text, uid,event="endConversation")
        return str(resp.twiml)
    
    if failed:
        resp = twilio_response.Hangup()
        s_text = "An error has occured while reseting your password. Routing you to service desk."
        resp.text = s_text
        log(caller,'bot', resp.text, uid, event="endConversation")
        return str(resp.twiml)
    
    url = url_for(".reset_password", _external=True)
    data = {
        'portalId':u_portal_id,
        'channel':'twilio',
        'redirect_url_success': url + '?success=True',
        'refirect_url_failed': url + '?Failed=True',
        'asid' : request.form.get("AccountSid"),
        'csid' : request.form.get("CallSid"),
        'name': name    
    }

    error = False
    try:
        send_to_queue(data,'graph-requests')
    except Exception as e:
        print(str(e))
        error = True
        text = "Something went wrong while communicating with AD. Routing to service desk"
        pass

    if error:
        resp = twilio_response.Hangup()
        resp.text = text
        return str(resp.twiml)

    resp = twilio_response.HoldCall()
    resp.text = "Enjoy the classic while I reset your password."
    log(caller,'bot', resp.text, uid)
    return str(resp.twiml)

