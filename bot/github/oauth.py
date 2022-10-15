import json

import requests
from bottle import redirect, request

client_id = '9cfb35031c71d9f6e013'
client_secret = '2e7e793b001390e9f2c9dd2e0033747bff890896'
redirect_uri = 'http://localhost:5556/github/oauth/redirect'
scopes = 'admin:repo_hook'
auth_url = 'https://github.com/login/oauth/authorize/?client_id=' + client_id + '&redirect_uri=' + redirect_uri + '&scope=' + scopes
get_token_url = 'https://github.com/login/oauth/access_token'


def redirector() -> None:
    redirect(auth_url)


def authorizer() -> str:
    auth_code: str = request.query.get('code')
    if auth_code:
        token: str = exchanger(auth_code)
        return f"Access-token = {token}"
    else:
        return "Authorization failed!"


def exchanger(code: str) -> str:
    parameters = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri
    }
    payload: str = json.dumps(parameters)
    header: dict[str, str] = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    r = requests.post(get_token_url, data=payload, headers=header)

    if r.status_code != 200:
        return "Failed to get Access-Token"
    else:
        data = r.json()
        token = data['access_token']
        return token
