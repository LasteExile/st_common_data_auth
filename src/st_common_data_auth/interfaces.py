from typing import Protocol

from st_common_data_auth.enums import CachePrefix

__all__ = ("IToken", "IAsyncCacheClient",)


class IToken(Protocol):
    async def get_token(self) -> str: ...

class ICache(Protocol):
    async def set(
        self,
        prefix: CachePrefix,
        key: str,
        value: str,
        expires: int | None = None,
    ) -> None: ...

    async def get(
        self,
        prefix: CachePrefix,
        key: str,
    ) -> str | None: ...

    async def close(self) -> None: ...
