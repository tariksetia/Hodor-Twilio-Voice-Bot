from flask import request
from hodor.entity.conv import Conversation
import  hodor.entity.twilio_unit as twilio_response
from . import reset_password_api

@reset_password_api.route('/reset-ad-password', methods=['GET','POST'])
def reset_password():
    resp = twilio_response.Hangup("please wait while I reset your password")
    success = request.args.get('success',False)
    failed = request.args.get('failed', False)
    text = request.args.get('text', None)

    if success:
        resp = twilio_response.Redirect()
        s_text = ""
        resp.text = ""
    return str(resp.twiml)

