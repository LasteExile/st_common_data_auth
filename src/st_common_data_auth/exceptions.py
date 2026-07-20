class BaseException(Exception):
    pass


class BadAuth0RequestError(BaseException):
    pass


class AuthenticationError(BaseException):
    pass


class AuthenticationHeaderError(AuthenticationError):
    pass


class UnauthorizedError(AuthenticationError):
    pass


class PermissionDeniedError(AuthenticationError):
    pass


