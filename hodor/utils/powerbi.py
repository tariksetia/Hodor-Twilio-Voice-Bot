import requests, json, datetime
def log(phone_number, user_name, message, callsid ):
    data = {
        'phone_number': phone_number,
        'user_name': user_name,
        'message': message,
        'callsid': callsid,
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    }
    data = [data]
    url = 'https://api.powerbi.com/beta/65e4e06f-f263-4c1f-becb-90deb8c2d9ff/datasets/8b24600c-8cb3-48dc-97a2-7b9ad9e63329/rows?key=UdsoO6XV07R%2B%2BwspXfn8yleJjxi44xsbOHM7ffV9kOZ2gSW94wtq6%2Fa%2Fwjha6Uw8l6QNliBtgAi8HrEcaGKImg%3D%3D'
    resp = requests.post(url, data=json.dumps(data))
    print('log_response = ' + str(resp.status_code) )

