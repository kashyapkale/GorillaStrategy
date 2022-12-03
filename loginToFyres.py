from fyers_api import fyersModel
from fyers_api import accessToken
import requests
import urllib.parse as urlparse
from urllib.parse import parse_qs
from datetime import datetime
import os
import config

def auto_login():
    session = accessToken.SessionModel(client_id=config.client_id,
                                       secret_key=config.secret_key,
                                       redirect_uri=config.redirect_uri,
                                       response_type='code',
                                       grant_type='authorization_code')

    session.generate_authcode()

    ses = requests.Session()
    payload = {"fy_id":f"{config.username}","password":f"{config.password}","app_id":"2","imei":"","recaptcha_token":""}
    res = ses.post('https://api.fyers.in/vagator/v1/login', json=payload).json()
    print(res)
    request_key = res["request_key"]

    payload_pin = {"request_key":f"{request_key}",
                   "identity_type":"pin",
                   "identifier":f"{config.pin}",
                   "recaptcha_token":""}
    res_pin = ses.post('https://api.fyers.in/vagator/v1/verify_pin', json=payload_pin).json()
    #assert res_pin.status_code == 200, f"Error in getting profile:\n {res_pin.json()}"
    print('*********************LogIn Response***************************')
    print(res_pin)
    print('*********************LogIn Response End***************************')
    ses.headers.update({
        'authorization': f"Bearer {res_pin['data']['access_token']}"
    })

    authParam = {"fyers_id":config.username,
                 "app_id":config.client_id[:-4],
                 "redirect_uri":config.redirect_uri,
                 "appType":"100",
                 "code_challenge":"",
                 "state":"None",
                 "scope":"",
                 "nonce":"",
                 "response_type":"code",
                 "create_cookie":True}

    authres = ses.post('https://api.fyers.in/api/v2/token', json=authParam).json()

    url = authres['Url']
    #print(url)
    parsed = urlparse.urlparse(url)
    auth_code = parse_qs(parsed.query)['auth_code'][0]
    session.set_token(auth_code)
    response = session.generate_token()
    token = response["access_token"]

    return token
