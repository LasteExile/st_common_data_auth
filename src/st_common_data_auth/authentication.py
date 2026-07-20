from typing import Union
from functools import lru_cache

import requests
from jose import jwt
from jose.exceptions import JWTError

from st_common_data_auth.exceptions import AuthenticationHeaderError, UnauthorizedError



@lru_cache
def get_jwks(auth0_domain: str) -> dict:
    response  = requests.get(f"https://{auth0_domain}/.well-known/jwks.json")
    response.raise_for_status()
    return response.json()


class Auth0Authentication:
    def __init__(self, *, auth0_domain: str, audience: str) -> None:
        self.auth0_domain = auth0_domain
        self.audience = audience

    def authenticate_request(
        self,
        invocation_metadata,
    ) -> dict:
        header = self.get_header(invocation_metadata)
        if header is None:
            raise AuthenticationHeaderError('No authorization header')

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            raise AuthenticationHeaderError('Empty authorization header')

        return self.authenticate(raw_token)

    def authenticate(self, raw_token: str) -> dict:
        """
        Validation of token, if token is invalid - exception would be raised

        :param raw_token: Token from header
        :param audience: auth0 api audience
        :return: payload of token
        """
        try:
            unverified_header = jwt.get_unverified_header(raw_token)
        except JWTError:
            raise AuthenticationHeaderError('Error decoding token headers')

        try:
            payload = jwt.decode(
                raw_token,
                get_jwks(self.auth0_domain),
                algorithms=["RS256"],
                audience=self.audience,
                issuer=f'https://{self.auth0_domain}/',
            )
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError('Token is expired')
        except jwt.JWTClaimsError as e:
            raise UnauthorizedError('Incorrect claims, please check the audience and issuer')
        except Exception:
            raise UnauthorizedError('Unable to parse authentication header')

        return payload

    def get_header(self, metadata) -> Union[str, None]:
        for u in metadata:
            if u.key.lower() == 'authorization':
                return u.value
        return None

    def get_raw_token(self, header: str) -> str:
        """
        Extracts an unvalidated JSON web token from the given "Authorization"
        header value.

        :param header: raw Authorization header
        :return: raw token
        """
        parts = header.split()

        if len(parts) == 0:
            raise AuthenticationHeaderError('Empty authorization header')

        if len(parts) != 2:
            raise AuthenticationHeaderError(
                'Authorization header must contain two space-delimited values')

        return parts[1]
