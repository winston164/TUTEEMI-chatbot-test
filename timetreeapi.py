import os

from jwcrypto import jwk, jwt
from datetime import datetime
import random
import requests
import json


def generateJWT(app_id: str):
    with open("timetree-connect.2020-12-22.pem", "rb") as pemfile:
        key = jwk.JWK.from_pem(pemfile.read())

    now = int(datetime.now().timestamp())
    payload = {
        "iat": now,
        "exp": now + (10 * 60),
        "iss": app_id,
    }
    Token = jwt.JWT(header={"alg": "RS256"}, claims=payload)
    Token.make_signed_token(key)
    return Token.serialize()


def getAccessToken(app_id, user_id):
    url = 'https://timetreeapis.com/installations/' + user_id + '/access_tokens'
    data = {
        "Accept": "application/vnd.timetree.v1+jsonl",
        "Authorization": "Bearer " + generateJWT(app_id)
    }

    return requests.post(url, headers=data).json()["access_token"]


def listCalendarMembers(accesToken: str):
    url = "https://timetreeapis.com/calendar/members"
    data = {
        "Accept": "application/vnd.timetree.v1+json",
        "Authorization": "Bearer " + accesToken
    }
    response = requests.get(url, headers=data)
    return response.json()


def create_event(accessToken: str, title: str, start_time: datetime, end_time: datetime, description: str):
    url = "https://timetreeapis.com/calendar/events"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.timetree.v1+json",
        "Authorization": "Bearer " + accessToken
    }

    data = {
        "data": {
            "attributes": {
                "category": "schedule",
                "title": title,
                "all_day": False,
                "start_at": start_time.isoformat(),
                "end_at": end_time.isoformat(),
                "description": description
            }
            #"relationships": {"label": {"data": {"id": "1233,2", "type": "label"}}},
        }
    }
    
    
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response.json()


if __name__ == '__main__':
    print(listCalendarMembers(getAccessToken("250", "9345")))
