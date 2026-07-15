from typing import Protocol


__all__ = ("IToken", "IAsyncCacheClient",)


class IToken(Protocol):
    async def get_token(self) -> str: ...


class IAsyncCacheClient(Protocol):
    async def aget(self, key: str) -> bytes: ...

    async def aset(self, key: str, value: bytes) -> None: ...
