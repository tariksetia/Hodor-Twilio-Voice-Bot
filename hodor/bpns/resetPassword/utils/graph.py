import requests,json,random

class Graph:

    def __init__(self,portal_id, client_id=None, client_secret=None):
        if not portal_id:
            raise Exception("portal ID is none")
        self.portal_id = portal_id
        self.client_id = client_id if client_id else '40264a72-840a-4b83-824a-a3d79349209b'
        self.client_secret = client_secret if client_secret else 'wcixfXIH6}}{rmBVDS5683$'
        self.token = self.getAuthToken(client_id=self.client_id, client_secret=self.client_secret)
        self.headers = {'Authorization': self.token}

    def getAuthToken(self, client_id, client_secret):
        token_url = "https://login.microsoftonline.com/dc91a4f8-7b3f-41f5-a0b3-e6a58770c92b/oauth2/v2.0/token"
        tokenData = {
            "grant_type": 'client_credentials',
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": 'https://graph.microsoft.com/.default'
        };
    
        res = requests.post(token_url,data=tokenData)
        if res.status_code != 200:
            raise Exception("I am sorry. I am facing problems while fetching you active directory data. Please try again later.")
        data = res.json()
        token = data['token_type'] + ' ' + data['access_token']
        return token
    
    def getUserData(self):
        result = {}
        user_url = 'https://graph.microsoft.com/v1.0/users/' + str(self.portal_id) + '@sherlockbotoutlook.onmicrosoft.com'
        res = requests.get(url=user_url, headers=self.headers)
        if res.status_code != 200:
            raise Exception("Error While fetching user data from active driectory.")
        user = res.json()
        result['name'] = user['displayName']
        result['city'] = user['officeLocation']
        result['phone_number'] = user['businessPhones'][0]
        result['mail'] = user['mail'].lower() if user['mail'] else None

        
        zip_url = user_url + '/postalcode'
        res = requests.get(url=zip_url, headers=self.headers)
        if res.status_code != 200:
            result['postal_code'] = None
        zip_ = res.json().get('value', None)
        result['postal_code'] = zip_
        return result

    def resetPassword(self):
        user_url = 'https://graph.microsoft.com/v1.0/users/' + str(self.portal_id) + '@sherlockbotoutlook.onmicrosoft.com'
        headers = dict(self.headers)
        headers['Content-Type'] = 'application/json'
        newPassword = self.generateRandomPassword()
        data = {
            "passwordProfile" : {
                "forceChangePasswordNextSignIn": True,
                "password": newPassword
            }
        }
        res = requests.patch(url=user_url, headers=headers, data=json.dumps(data))
        if res.status_code != 204:
            print (res.json())
            raise Exception("I can't reset your password at this time. Please wait while I connect you to N T T  representative")
        
        return {"newPassword":newPassword}

    def generateRandomPassword(self):
        upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        lower = 'abcdefghijklmnopqrstuvwxyz'
        digit = '012345678'
        schar = '!@#$%^&*'

        passowrd = ''

        for i in range(3):
            passowrd += random.choice(upper)
        
        for i in range(4):
            passowrd += random.choice(lower)

        passowrd += random.choice(schar)

        for i in range(4):
            passowrd += random.choice(digit)

        return passowrd

        