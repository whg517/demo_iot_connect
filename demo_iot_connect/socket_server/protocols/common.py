import asyncio
import collections
import logging
import sys
from typing import Optional, Deque, Any, Dict, Union, Iterator, AsyncIterable
from asyncio import AbstractEventLoop, Transport

from demo_iot_connect.socket_server.protocols.schemas import RemoteAddress
from demo_iot_connect.socket_server.typing import MessageData
from demo_iot_connect.socket_server.utils import Message

logger = logging.getLogger(__name__)


class Connections:
    """
    保存连接对象
    """

    def __ini__(self):
        self.connections = Dict[str, CommonProtocol] = dict()

    def register(self, protocol: 'CommonProtocol'):
        remote = protocol.remote_address
        self.connections.update({str(remote): protocol})

    def un_register(self, protocol: 'CommonProtocol'):
        self.connections.pop(str(protocol.remote_address))


class FlowControlMixin:

    def __init__(self, loop):
        self.loop = loop
        self._drain_lock = asyncio.Lock(
            loop=loop if sys.version_info[:2] < (3, 8) else None
        )

        super(FlowControlMixin, self).__init__()

    # Copied from asyncio.FlowControlMixin
    async def _drain_helper(self) -> None:  # pragma: no cover
        if self.connection_lost_waiter.done():
            raise ConnectionResetError("Connection lost")
        if not self._paused:
            return
        waiter = self._drain_waiter
        assert waiter is None or waiter.cancelled()
        waiter = self.loop.create_future()
        self._drain_waiter = waiter
        await waiter

    # Copied from asyncio.StreamWriter
    async def _drain(self) -> None:  # pragma: no cover
        if self.reader is not None:
            exc = self.reader.exception()
            if exc is not None:
                raise exc
        if self.transport is not None:
            if self.transport.is_closing():
                # Yield to the event loop so connection_lost() may be
                # called.  Without this, _drain_helper() would return
                # immediately, and code that calls
                #     write(...); yield from drain()
                # in a loop would never call connection_lost(), so it
                # would not see an error when the socket is closed.
                await asyncio.sleep(
                    0, loop=self.loop if sys.version_info[:2] < (3, 8) else None
                )
        await self._drain_helper()


class CommonProtocol(asyncio.Protocol, FlowControlMixin):
    """
    公共协议
    实现功能：
        1. 提供一个异步IO流读对象 `reader`，在接收数据后会不断写入该对象中。后续使用直接从该流中获取即可
        2. 提供一个用于传输数据的异步任务 `transfer_data`，该任务应该用于从 `reader` 中读取数据并处理，
            并使用数据帧协议解析数据对象，将处理的对象写入 `messages` 队列中，由 `handle_request` 使用。
        ~~ 3. 提供一个用于检测远程是否在线的异步任务 `keepalive_ping` ，该任务应 ~~

    """

    def __init__(self, loop: Optional[AbstractEventLoop] = None):
        self.loop = loop

        self.max_size = None

        self.messages: Deque[Any] = collections.deque()
        self._pop_message_waiter: Optional[asyncio.Future[None]] = None
        self._put_message_waiter: Optional[asyncio.Future[None]] = None

        self.reader = asyncio.StreamReader(1024, loop)

        self.transport: Optional[Transport] = None

        self.connections = Connections()

        self._fragmented_writer = Optional[asyncio.Task[None]] = None

        # Task running the data transfer.
        self.transfer_data_task: Optional[asyncio.Task[None]] = None
        self.keepalive_ping_task: Optional[asyncio.Task[None]] = None

        # Completed when the connection state becomes CLOSED. Translates the
        # :meth:`connection_lost` callback to a :class:`~asyncio.Future`
        # that can be awaited. (Other :class:`~asyncio.Protocol` callbacks are
        # translated by ``self.stream_reader``).
        self.connection_lost_waiter: asyncio.Future[None] = loop.create_future()

        super(CommonProtocol, self).__init__(loop)

    @property
    def remote_address(self) -> Optional[RemoteAddress]:
        try:
            transport = self.transport
        except AttributeError:
            return None
        else:
            host, port = transport.get_extra_info("peername")
            return RemoteAddress(host=host, port=port)

    def connection_made(self, transport: Transport) -> None:
        """
        建立连接后初始化任务
        :param transport:
        :return:
        """
        self.transport = transport
        client = transport.get_extra_info('peername')
        logger.debug(f'client: {client} made connection.')

        self.connections.register(self)

        # 增加异步任务
        self.transfer_data_task = self.loop.create_task(self.transfer_data())
        self.keepalive_ping_task = self.loop.create_task(self.keepalive_ping())

        self.loop.create_task(self.handle_request())

    def data_received(self, data: bytes) -> None:
        """
        接收数据病持续写入
        :param data:
        :return:
        """
        logger.debug(f'{self.remote_address} send data {len(data)} bytes')
        self.reader.feed_data(data)

    def eof_received(self) -> None:
        logger.debug(f'{self.remote_address} - event = eof_received()')
        self.reader.feed_eof()

    def connection_lost(self, exc: Optional[Exception]) -> None:
        self.connections.un_register(self)

    def fail_connection(self):
        pass

    async def ensure_open(self):
        pass

    async def transfer_data(self, max_size: Optional[int] = None) -> None:
        """
        持续接受数据帧，并将数据帧合并成一个完整的消息
        :return:
        """
        while True:
            frame = await self.read_message()

    async def keepalive_ping(self):
        """
        ping-pong
        检测发送端是否存活
        :return:
        """
        raise NotImplementedError

    async def send(self, message: Union[MessageData, Iterator[MessageData], AsyncIterable[MessageData]]) -> None:
        while self._fragmented_writer is not None:
            await asyncio.shield(self._fragmented_writer)

        self._fragmented_writer = asyncio.Future()

        try:
            msg = Message(self)
            msg.write(message)
        finally:
            self._fragmented_writer.set_result(None)
            self._fragmented_writer = None

    async def read_message(self) -> Optional[MessageData]:
        """
        :return:
        """
        message = Message(self.remote_address)
        message_data = await message.read(self.reader.readexactly, self.max_size)
        return message_data

    async def receive(self):
        raise NotImplementedError

    async def handle_request(self) -> None:
        """
        实现上层处理
        :return:
        """
        raise NotImplementedError
