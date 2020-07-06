import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from demo_iot_connect.socket_server.server import Config


class CustomsSocketProtocol(asyncio.Protocol):

    def __init__(self, config: 'Config'):
        self.app = config.app
        self.loop = config.loop
        self.reader = asyncio.StreamReader(20 * 1024, config.loop)

        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        super().connection_made(transport)

    def data_received(self, data: bytes) -> None:
        print(data)
        scope = {
            'type': 'socket',
        }

        # self.reader.feed_data(data)
        # self.cycle = RequestResponseCycle(
        #     self.transport,
        #     scope
        # )
        #
        # self.loop.create_task(self.cycle.run_asgi(self.app))


class RequestResponseCycle:

    def __init__(self, transport, scope, body=b''):
        self.transport = transport
        self.scope = scope
        self.body = body

    async def run_asgi(self, app):
        result = await app(self.scope, self.receive, self.send)

    async def send(self, message):
        self.transport.send(message)

    async def receive(self):
        return {
            'type': 'socket.erquest',
            'body': self.body
        }
