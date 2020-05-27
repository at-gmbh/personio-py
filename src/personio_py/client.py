import logging
import os
from typing import Any, Dict
from urllib.parse import urljoin

import requests

from personio_py.errors import MissingCredentialsError, PersonioApiError, PersonioError

logger = logging.getLogger('personio_py')


class Personio:

    BASE_URL = "https://api.personio.de/v1/"

    def __init__(self, base_url: str = None, client_id: str = None, client_secret: str = None):
        self.base_url = base_url or self.BASE_URL
        self.client_id = client_id or os.getenv('CLIENT_ID')
        self.client_secret = client_secret or os.getenv('CLIENT_SECRET')
        self.headers = {'accept': 'application/json'}
        self.authenticated = False

    def authenticate(self):
        if not (self.client_id and self.client_secret):
            raise MissingCredentialsError(
                "both client_id and client_secret must be provided in order to authenticate")
        url = urljoin(self.base_url, 'auth')
        logger.debug(f"authenticating to {url} with client_id {self.client_id}")
        params = {"client_id": self.client_id, "client_secret": self.client_secret}
        response = requests.request("POST", url, headers=self.headers, params=params)
        if response.ok:
            token = response.json()['data']['token']
            self.headers['Authorization'] = f"Bearer {token}"
            self.authenticated = True
        else:
            raise PersonioApiError.from_response(response)

    def request(self, path: str, method='GET', params: Dict[str, Any] = None):
        # check if we are already authenticated
        if not self.authenticated:
            self.authenticate()
        # make the request
        url = urljoin(self.base_url, path)
        response = requests.request(method, url, headers=self.headers, params=params)
        # re-new the authorization header
        authorization = response.headers.get('Authorization')
        if authorization:
            self.headers['Authorization'] = authorization
        else:
            raise PersonioError("Missing Authorization Header in response")
        # handle the response
        if response.ok:
            try:
                data = response.json()
                return data
            except ValueError as e:
                raise PersonioError(f"Failed to parse response as json: {response.text}")
        else:
            raise PersonioApiError.from_response(response)
