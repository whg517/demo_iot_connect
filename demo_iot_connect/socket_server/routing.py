import asyncio
import typing

from demo_iot_connect.socket_server.utils import (ASGIApp, Receive, Scope,
                                                  Send, run_in_thread)


def request_response(func: typing.Callable) -> ASGIApp:
    """
    Takes a function or coroutine `func(request) -> response`,
    and returns an ASGI application.
    """
    is_coroutine = asyncio.iscoroutinefunction(func)

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        # 注意：这里并没有将接收到的数据转换成 request 对象
        request = await receive()
        if is_coroutine:
            response = await func(request)
        else:
            response = await run_in_thread(func, request)
        # 注意：这里也没有封装 response 对象
        await send(response)

    return app


class Route:

    def __init__(self, path, endpoint):
        self.path = path
        self.endpoint = endpoint

        self.app = request_response(endpoint)

    async def handle(self, scope: Scope, receive: Receive, send: Send):
        await self.app(scope, receive, send)


class Router:

    def __init__(self):
        self.routes = []

    def add_route(self, route: Route):
        self.routes.append(route)

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        # path = scope['path']
        for route in self.routes:
            await route.handle(scope, receive, send)
