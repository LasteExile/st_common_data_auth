import httpx
import json
import datetime
import logging
from typing import TypedDict

import requests

from st_common_data_auth.interfaces import IAsyncCacheClient, IToken
from st_common_data_auth.exceptions import BadAuth0RequestError


logger = logging.getLogger(__name__)


__all__ = ("AbstractServiceAuth0Token",)


class TokenType(TypedDict):
    expires_in: int
    access_token: str


class AbstractServiceAuth0Token(IToken):
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
        cache_client: IAsyncCacheClient,
    ) -> None:
        self.grant_type = grant_type
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = services_token_url
        self.cache_client = cache_client

    async def get_token(self) -> str:
        raw_data = await self.cache_client.aget(self.token_name)

        if raw_data:
            data = json.loads(raw_data)
            token = data['token']
            expiration_str = data['expiration_time']
            expiration = datetime.datetime.fromisoformat(expiration_str)

            if expiration < datetime.datetime.now(tz=datetime.timezone.utc):
                return await self._update_token()
            return token
        else:
            return await self._update_token()

    async def _update_token(self) -> str:
        token_data = await self._generate_token()
        token = token_data['access_token']

        logger.info(f'{self.token_name} token was created!')

        now = datetime.datetime.now(tz=datetime.timezone.utc)
        expiration = now + datetime.timedelta(seconds=token_data['expires_in'] - 10 * 60)

        data = {
            'token': token,
            'expiration_time': expiration.isoformat()
        }

        await self.cache_client.aset(
            self.token_name,
            json.dumps(data),
        )

        return token

    async def _generate_token(self, retry: int = 2) -> TokenType:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=self.token_url,
                data={
                    'audience': self.audience,
                    'grant_type': self.grant_type,
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=2,
            )
        if response.status_code == 200:
            return response.json()
        else:
            while retry > 0:
                await self._generate_token(retry=retry - 1)

            try:
                details = response.json()
            except requests.exceptions.JSONDecodeError:
                details = response.text
            raise BadAuth0RequestError(
                f'Unable to get token, status code: {response.status_code}. '
                f'Server returned: {details}'
            )

    def __str__(self):
        return self.token

