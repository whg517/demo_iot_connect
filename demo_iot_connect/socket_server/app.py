from typing import List

from demo_iot_connect.socket_server.routing import Route, Router
from demo_iot_connect.socket_server.utils import Receive, Scope, Send


class Application:
    def __init__(self, routes: List[Route]):
        self.routes = routes

        self.router = Router()

        for route in self.routes:
            self.router.add_route(route)

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        await self.router(scope, receive, send)
