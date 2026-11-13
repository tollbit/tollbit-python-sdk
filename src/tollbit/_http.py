from __future__ import annotations

from contextlib import AsyncExitStack, ExitStack, asynccontextmanager
from http.cookiejar import CookieJar, DefaultCookiePolicy
from types import TracebackType
from typing import AsyncIterator, Awaitable, Callable, TypeVar

import anyio
import httpx
from anyio.from_thread import BlockingPortal, start_blocking_portal

from tollbit._environment import Environment

T = TypeVar("T")
SyncClientT = TypeVar("SyncClientT", bound="SyncClientContext")
AsyncClientT = TypeVar("AsyncClientT", bound="AsyncClientContext")


class HTTPTransport:
    def __init__(self, env: Environment):
        self.env = env
        self.portal: BlockingPortal | None = None
        self._client: httpx.AsyncClient | None = None

    @asynccontextmanager
    async def pool(self) -> AsyncIterator[None]:
        if self._client is not None:
            raise RuntimeError("The TollBit connection pool is already open")
        # Pool sockets without persisting response cookies across requests.
        cookies = CookieJar(policy=DefaultCookiePolicy(allowed_domains=[]))
        async with httpx.AsyncClient(timeout=self.env.timeout, cookies=cookies) as client:
            self._client = client
            try:
                yield
            finally:
                self._client = None

    @asynccontextmanager
    async def session(self) -> AsyncIterator[httpx.AsyncClient]:
        if self._client is not None:
            yield self._client
        else:
            async with httpx.AsyncClient(timeout=self.env.timeout) as client:
                yield client

    def run(self, func: Callable[..., Awaitable[T]], *args: object) -> T:
        if self.portal is not None:
            return self.portal.call(func, *args)
        return anyio.run(func, *args, backend=self.env.anyio_backend)


class AsyncClientContext:
    def __init__(self, http: HTTPTransport | None):
        self._http = http
        self._pool: AsyncExitStack | None = None

    async def __aenter__(self: AsyncClientT) -> AsyncClientT:
        if self._http is None:
            raise RuntimeError("Use create_async_client() to enable connection pooling")
        if self._pool is not None:
            raise RuntimeError("The TollBit connection pool is already open")
        stack = AsyncExitStack()
        await stack.enter_async_context(self._http.pool())
        self._pool = stack
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._pool is not None:
            try:
                await self._pool.__aexit__(exc_type, exc, traceback)
            finally:
                self._pool = None


class SyncClientContext:
    def __init__(self, http: HTTPTransport | None):
        self._http = http
        self._pool: ExitStack | None = None

    def __enter__(self: SyncClientT) -> SyncClientT:
        if self._http is None:
            raise RuntimeError("Use create_client() to enable connection pooling")
        if self._pool is not None:
            raise RuntimeError("The TollBit connection pool is already open")
        with ExitStack() as stack:
            portal = stack.enter_context(
                start_blocking_portal(backend=self._http.env.anyio_backend)
            )
            stack.enter_context(portal.wrap_async_context_manager(self._http.pool()))
            self._http.portal = portal
            self._pool = stack.pop_all()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._pool is not None and self._http is not None:
            self._http.portal = None
            try:
                self._pool.__exit__(exc_type, exc, traceback)
            finally:
                self._pool = None
