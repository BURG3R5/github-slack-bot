import json
import os
import urllib.parse

import requests
from bottle import redirect


class GitHubOAuth:

    @staticmethod
    def redirect_to_oauth_flow(repository: str):
        endpoint = f"https://github.com/login/oauth/authorize/"
        params = {
            "scope":
            "admin:repo_hook",
            "client_id":
            os.environ["GITHUB_APP_CLIENT_ID"],
            "redirect_uri":
            f"http://127.0.0.1:5556/github/auth/redirect/{repository}",
        }
        redirect(endpoint + "?" + urllib.parse.urlencode(params))

    @classmethod
    def set_up_webhooks(cls, code: str, repository: str) -> str:
        try:
            github_oauth_token = cls.exchange_code_for_token(code)
            cls.use_token_for_webhooks(github_oauth_token, repository)
        except AuthenticationError:
            return ("GitHub Authentication failed. Access to "
                    "webhooks is needed to set up your repository")
        except WebhookCreationError:
            return "Webhook Creation failed. Please retry in five seconds"
        else:
            return "Webhooks have been set up successfully!"

    @staticmethod
    def exchange_code_for_token(code: str) -> str:
        data = {
            "code": code,
            "client_id": os.environ["GITHUB_APP_CLIENT_ID"],
            "client_secret": os.environ["GITHUB_APP_CLIENT_SECRET"],
            # "redirect_uri": "https://google.com/"
        }

        response = requests.post(
            "https://github.com/login/oauth/access_token",
            data=json.dumps(data),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        if response.status_code != 200:
            raise AuthenticationError

        return response.json()["access_token"]

    @staticmethod
    def use_token_for_webhooks(token: str, repository: str):
        data = {
            "name": "web",
            "active": True,
            "events": ["*"],
            "config": {
                "url": os.environ["BASE_URL"] + "/github/events",
                "content_type": "json",
            },
        }

        response = requests.post(
            f"https://api.github.com/repos/{repository}/hooks",
            data=json.dumps(data),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
            },
        )

        if response.status_code != 201:
            raise WebhookCreationError


class AuthenticationError(Exception):
    pass


class WebhookCreationError(Exception):
    pass
