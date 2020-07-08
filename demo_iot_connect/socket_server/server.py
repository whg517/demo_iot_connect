import asyncio
import logging
from asyncio import AbstractEventLoop, AbstractServer
from typing import Optional

from demo_iot_connect.config import settings
from demo_iot_connect.socket_server.app import Application
from demo_iot_connect.socket_server.protocols import SocketProtocol as Protocol

logger = logging.getLogger('socket_server')


class Config:

    def __init__(
            self,
            app: Application,
            loop: Optional[AbstractEventLoop] = None
    ) -> None:
        self.loop = loop
        if self.loop is None:
            self.loop = asyncio.get_event_loop()
        self.app = app


class Server:

    def __init__(
            self,
            app: Application,
            host: Optional[str] = None,
            port: Optional[int] = None,
            loop: Optional[AbstractEventLoop] = None
    ) -> None:
        """
        :param app:
        :param host:
        :param port:
        :param loop:
        """
        self.config = Config(app, loop)
        self.loop = self.config.loop
        self.host = host or settings.HOST  # settings default 127.0.0.1
        self.port = port or settings.PORT  # settings default 8000

    async def start_up(self) -> AbstractServer:
        server = await self.loop.create_server(
            protocol_factory=lambda: Protocol(config=self.config),
            host=self.host,
            port=self.port
        )
        logger.info(f'Server bind: {self.host}:{self.port}')
        return server

    async def run(self) -> None:
        server = await self.start_up()
        async with server:
            await server.serve_forever()
        logger.info(f'Server started.')


def run(
        app: Application,
        *,
        host: str = None,
        port: int = None,
) -> None:
    loop = asyncio.get_event_loop()
    server = Server(app, host, port)
    loop.create_task(server.run())
    loop.run_forever()
