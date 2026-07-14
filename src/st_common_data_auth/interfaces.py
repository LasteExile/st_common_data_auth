from typing import Protocol


__all__ = ("IToken", "ICacheClient",)


class IToken(Protocol):
    @property
    def token(self) -> str: ...


class ICacheClient(Protocol):
    def get(self, key: str) -> bytes: ...

    def set(self, key: str, value: bytes) -> None: ...
