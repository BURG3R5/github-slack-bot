import json
import secrets
import urllib.parse

import requests
import sentry_sdk
from bottle import redirect

from bot.github.base import GitHubBase


class Authenticator(GitHubBase):

    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
    ):
        GitHubBase.__init__(self)
        self.base_url = base_url
        self.app_id = client_id
        self.app_secret = client_secret

    def redirect_to_oauth_flow(self, repository: str):
        endpoint = f"https://github.com/login/oauth/authorize"
        params = {
            "scope":
            "admin:repo_hook",
            "client_id":
            self.app_id,
            "redirect_uri":
            f"https://redirect.mdgspace.org/{self.base_url}"
            f"/github/auth/redirect/{repository}",
        }
        redirect(endpoint + "?" + urllib.parse.urlencode(params))

    def set_up_webhooks(self, code: str, repository: str) -> str:
        try:
            github_oauth_token = self.exchange_code_for_token(code)
            self.use_token_for_webhooks(github_oauth_token, repository)
        except AuthenticationError:
            return ("GitHub Authentication failed. Access to "
                    "webhooks is needed to set up your repository")
        except WebhookCreationError:
            return "Webhook Creation failed. Please retry in five seconds"
        else:
            return "Webhooks have been set up successfully!"

    def exchange_code_for_token(self, code: str) -> str:
        data = {
            "code": code,
            "client_id": self.app_id,
            "client_secret": self.app_secret,
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

    def use_token_for_webhooks(self, token: str, repository: str):
        secret = db.token_hex(20)

        successful = self.storage.add_secret(repository, secret)

        if not successful:
            raise DuplicationError

        data = {
            "name": "web",
            "active": True,
            "events": ["*"],
            "config": {
                "url": f"https://{self.base_url}/github/events",
                "content_type": "json",
                "secret": secret,
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
            sentry_sdk.capture_message(f"Failed during webhook creation\n"
                                       f"Status code: {response.status_code}\n"
                                       f"Content: {response.content}")
            raise WebhookCreationError


class AuthenticationError(Exception):
    pass


class DuplicationError(Exception):
    pass


class WebhookCreationError(Exception):
    pass
