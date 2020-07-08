import asyncio
import logging
from asyncio import BaseTransport
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from demo_iot_connect.socket_server.server import Config

logger = logging.getLogger(__name__)


class SocketProtocol(asyncio.Protocol):

    def __init__(self, config: 'Config'):
        self.config = config

        self.transport: Optional[BaseTransport] = None

    def data_received(self, data: bytes) -> None:
        super().data_received(data)

    def eof_received(self) -> Optional[bool]:
        return super().eof_received()

    def connection_made(self, transport: BaseTransport) -> None:
        self.transport = transport
        client = transport.get_extra_info('peername')
        logger.debug(f'client: {client} made connection.')

    def connection_lost(self, exc: Optional[Exception]) -> None:
        self.transport = None
        super().connection_lost(exc)

    def pause_writing(self) -> None:
        super().pause_writing()

    def resume_writing(self) -> None:
        super().resume_writing()
