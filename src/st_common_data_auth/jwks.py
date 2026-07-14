import requests

from st_common_data_auth.singleton import SingletonMeta


__all__ = ("JWKS",)


class JWKS(metaclass=SingletonMeta):
    """
    Auth0 json web keys set for local token verification
    """

    def __init__(self, auth0_domain: str, auth_exception: Type[Exception]):
        self.auth0_domain: str = auth0_domain
        self.auth_exception = auth_exception
        self._jwks_keys: dict = dict()

        self._update_jwks()

    def get_rsa_key(self, kid: str) -> Optional[dict]:
        try:
            return self._jwks_keys[kid]
        except KeyError:
            self._update_jwks()
            if kid not in self._jwks_keys:
                raise self.auth_exception('Unable to find appropriate key')
            return self._jwks_keys[kid]

    def _update_jwks(self):
        jsonurl = requests.get(f"https://{self.auth0_domain}/.well-known/jwks.json")
        self._jwks_keys = dict()
        for key in json.loads(jsonurl.read())['keys']:
            self._jwks_keys[key['kid']] = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]}
