import requests, json, datetime
from hodor.utils.servicebus import send_to_queue


def log(phone_number, user_name, message, callsid, event="logMessage" ):
    data = {
        'phone_number': phone_number,
        'user_name': user_name,
        'message': message,
        'callsid': callsid,
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'event': event
    }
    send_to_queue(data,'chat-logs')

