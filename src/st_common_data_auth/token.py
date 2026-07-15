from st_common_data_auth.abstract_token import AbstractServiceAuth0Token


__all__ = ("ServiceOAAuth0Token", "ServiceCAPAuth0Token", "ManagementAuth0Token",)


class ManagementAuth0Token(AbstractServiceAuth0Token):
    """
    Auth0 token from management app for communication with auth0 API
    """
    audience = 'https://pine-trading-suite.us.auth0.com/api/v2/'
    token_name = 'management_token'


class ServiceCAPAuth0Token(AbstractServiceAuth0Token):
    """
    Auth0 CAP token
    """
    audience = 'cap_api'
    token_name = 'cap_service_token'


class ServiceOAAuth0Token(AbstractServiceAuth0Token):
    """
    Auth0 CAP token
    """
    audience = 'oa_api'
    token_name = 'service_token'
