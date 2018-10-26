from flask import Flask, request, Response
from flask import session
from flask_socketio import emit, join_room, leave_room
from twilio.twiml.voice_response import VoiceResponse, Gather
from flask_socketio import SocketIO
from hodor.entity.conv import Conversation
from hodor.bpns.resetPassword import reset_password_api
import hodor.entity.twilio_unit as twilio_response
import hodor.utils.luisnlp as luis
from hodor.utils.logger import log
import uuid, urllib, re

app = Flask(__name__)
socketio = SocketIO(app)
app.register_blueprint(reset_password_api, url_prefix='/api/reset-password')

@app.route('/answer', methods=['GET','POST'])
def answer():
    print(request.form)
    uid = request.form.get('CallSid')
    print("uid = " + uid)
    caller = request.form.get('Caller')
    status = 'on'
    conv = Conversation(uid, caller, status)
    conv.save()

    resp = twilio_response.Redirect()
    resp.text = "Hello! welcome to NTT service desk. How may I help?"
    data = {
        'ntry': 1,
        'reprompt': resp.text
        
    }
    data_url = urllib.parse.urlencode(data)
    resp.url = "/gatherIntent?{}".format(data_url)
    log(caller,'bot',resp.text,uid, event="startConversation")

    return str(resp.twiml)


@app.route("/gatherIntent", methods=['GET','POST'])
def gatherIntent():
    caller = request.form.get('Caller')
    uid = request.form.get('CallSid')

    speech = request.form.get('SpeechResult', None)
    if speech:
        log(caller,'caller',speech,uid)
        speech = re.sub(r'(\d)\s+(\d)', r'\1\2', speech)
        route, entities = luis.getRoute(speech)
        print(speech)
        print(entities)
        
        if route is None:
            resp = twilio_response.Hangup()
            resp.text = "No intent found"
            log(caller,'bot',resp.text,uid, event="endConversation")
            return str(resp.twiml)
        
        if route:
            resp = twilio_response.Redirect()
            if entities and len(entities.items()) != 0:
                luis_entities = urllib.parse.urlencode(entities)
                print(luis_entities)
                route = route + '?' + luis_entities
            resp.url = route
            log(caller,'bot',resp.text,uid)
            return str(resp.twiml)



    ntry = int(request.args.get('ntry', '1'))
    if ntry > 4:
        resp = twilio_response.Hangup()
        resp.text = "You have reached your retry limit. Routing to service desk"    
        log(caller,'bot', resp.text ,uid, event="endConversation")
        return str(resp.twiml)


    reprompt = request.args.get("reprompt", "I am sorry. I didn't quite catch that. Please try again!")
    resp = twilio_response.GatherSpeech()
    resp.text = reprompt
    resp.say =  ntry > 1
    ntry += 1
    data = {
        'reprompt': resp.text,
        'ntry': ntry
    }
    data_url = urllib.parse.urlencode(data)
    resp.url = '/gatherIntent?{}'.format(data_url)
    log(caller,'bot',resp.text,uid)

    return str(resp.twiml);






if __name__ == '__main__':
    app.run(debug=True)