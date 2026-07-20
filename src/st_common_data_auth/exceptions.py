class BaseException(Exception):
    pass


class BadAuth0RequestError(BaseException):
    pass


class JWKSError(BaseException):
    pass


class AuthenticationHeaderError(BaseException):
    pass


class UnauthorizedError(BaseException):
    pass


class PermissionDeniedError(BaseException):
    pass


