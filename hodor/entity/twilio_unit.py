from abc import ABCMeta, abstractproperty
from twilio.twiml.voice_response import VoiceResponse,Gather,Say
import time

class Message(metaclass=ABCMeta):
    def __init__(self, language=None, voice=None):
        self.language = language if language else 'en-IN'
        self.voice = voice if voice else 'Polly.Joanna'

    @abstractproperty
    def twiml():
        pass
    
class Redirect(Message):
    def __init__(self, text=None, url=None, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.url = url
    
    @property
    def twiml(self):
        resp = VoiceResponse()
        if self.text:
            resp.say(self.text, voice=self.voice)
        resp.redirect(self.url, method="POST");
        return resp


class GatherSpeech(Message):
    def __init__(self, text=None, url=None, say=False,input_='speech', num_digit=None, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.url = url
        self.say = SyntaxWarning
        self.input = input_
        self.digits = num_digit
    
    @property
    def twiml(self):
        resp = VoiceResponse()
        if self.say and self.text:
            resp.say(self.text, voice=self.voice)
        gather = Gather(input="speech", method="POST", action=self.url, language=self.language, speechTimeout='auto')
        resp.append(gather)
        resp.redirect(self.url, method='POST')
        
        return str(resp)

class Hangup(Message):
    def __init__(self, text=None, **kwargs):
        super().__init__(**kwargs)
        self.text = text

    @property
    def twiml(self):
        resp = VoiceResponse()
        resp.say(self.text, voice=self.voice)
        resp.hangup()
        return str(resp)

class HoldCall(Message):
    def __init__(self, text=None, **kwargs):
        super().__init__(**kwargs)
        self.text = text

    @property
    def twiml(self):
        response = VoiceResponse()
        if self.text:
            response.say(self.text, voice=self.voice)
        response.play('https://demo.twilio.com/docs/classic.mp3', loop=0)
        return str(response)


