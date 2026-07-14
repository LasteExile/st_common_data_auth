import json
import datetime
import logging
from typing import TypedDict

import requests

from st_common_data_auth.singleton import SingletonMeta
from st_common_data_auth.interfaces import ICacheClient, IToken
from st_common_data_auth.exceptions import BadAuth0RequestError


logger = logging.getLogger(__name__)


__all__ = ("AbstractServiceAuth0Token",)


class TokenType(TypedDict):
    expires_in: int
    access_token: str


class AbstractServiceAuth0Token(IToken, metaclass=SingletonMeta):
    """
    Auth0 token from service app for machine-to-machine communication (between services)
    """
    audience: str
    token_name: str

    def __init__(
        self,
        grant_type: str,
        client_id: str,
        client_secret: str,
        services_token_url: str,
        cache_client: ICacheClient,
    ) -> None:
        self.grant_type = grant_type
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = services_token_url
        self.cache_client = cache_client

    @property
    def token(self) -> str:
        raw_data = self.cache_client.get(self.token_name)

        if raw_data:
            data = json.loads(raw_data)
            token = data['token']
            expiration_str = data['expiration_time']
            expiration = datetime.datetime.fromisoformat(expiration_str)

            if expiration < datetime.datetime.utcnow():
                return self._update_token()
            return token
        else:
            return self._update_token()

    def _update_token(self) -> str:
        token_data = self._get_token()
        token = token_data['access_token']

        logger.info(f'{self.token_name} token was created!')

        expiration = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
            seconds=token_data['expires_in'] - 10 * 60)

        data = {
            'token': token,
            'expiration_time': expiration.isoformat()
        }

        self.cache_client.set(self.token_name, json.dumps(data))

        return token

    def _get_token(self, retry: int = 2) -> TokenType:
        response = requests.post(
            url=self.token_url,
            data={
                'audience': self.audience,
                'grant_type': self.grant_type,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=2)
        if response.status_code == 200:
            return response.json()
        else:
            while retry > 0:
                self._get_token(retry=retry - 1)

            try:
                details = response.json()
            except requests.exceptions.JSONDecodeError as e:
                details = response.text
            raise BadAuth0RequestError(f'Unable to get token, status code: {response.status_code}. Server returned: {details}')

    def __str__(self):
        return self.token


class ManagementAuth0Token(ServiceAuth0Token):
    """
    Auth0 token from management app for communication with auth0 API
    """
    token_name = 'management_token'


class ServiceCAPAuth0Token(ServiceAuth0Token):
    """
    Auth0 CAP token
    """
    token_name = 'cap_service_token'

