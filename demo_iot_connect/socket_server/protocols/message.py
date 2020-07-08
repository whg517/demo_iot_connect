import codecs
import logging
from typing import (TYPE_CHECKING, AsyncIterable, Awaitable, Callable,
                    Iterator, Optional, Tuple, Union)

from demo_iot_connect.socket_server import constants
from demo_iot_connect.socket_server.protocols.framing import Frame, OpCode
from demo_iot_connect.socket_server.typing import MessageData

if TYPE_CHECKING:
    from demo_iot_connect.socket_server.protocols.common import CommonProtocol

logger = logging.getLogger(__name__)


class Message:
    """
    将消息和数据帧相互转换
    """

    def __init__(self, protocol: 'CommonProtocol'):
        self.protocol = protocol

    async def read_frame(
            self, reader: Callable[[int], Awaitable[bytes]],
            max_size: Optional[int]
    ) -> Frame:
        frame = await Frame.read(reader, max_size=max_size)
        logger.debug(f'Read from {self.protocol.remote_address} frame: <{frame}>')
        return frame

    async def read(self, reader: Callable[[int], Awaitable[bytes]], max_size: Optional[int]) -> MessageData:
        frame = await self.read_frame(reader, max_size)

        message = MessageJoiner(op_code=frame.op_code, final=frame.final, data=frame.data, max_size=max_size)

        while frame.final:
            frame = await self.read_frame(reader, max_size)
            message.append(frame.data)
        return message.data

    async def write_frame(
            self,
            final: bool,
            op_code: OpCode,
            data: MessageData
    ):
        """
        发送数据
        :param data: 单条 message
        :param op_code:
        :param final: 标记该帧消息是否为最后一帧
        :return:
        """

        if isinstance(data, str):
            data = data.encode(constants.CHARACTER)
        elif isinstance(data, bytes):
            pass
        else:
            raise TypeError(f'Send message type error, expectation type: <bytes, str>, actually is <{type(data)}>')

        frame = Frame(final=final, op_code=op_code, data=data)
        frame.write(self.protocol.transport.write)

        try:
            # drain() cannot be called concurrently by multiple coroutines:
            # http://bugs.python.org/issue29930. Remove this lock when no
            # version of Python where this bugs exists is supported anymore.
            async with self.protocol._drain_lock:
                # Handle flow control automatically.
                await self.protocol._drain()
        except ConnectionError:
            # Terminate the connection if the socket died.
            self.protocol.fail_connection()
            # Wait until the connection is closed to raise ConnectionClosed
            # with the correct code and reason.
            await self.protocol.ensure_open()

    def write(
            self,
            data: Union[MessageData, Iterator[MessageData], AsyncIterable[MessageData]]
    ):
        # 单条 data 发送一个数据帧
        if isinstance(data, MessageData):
            op_code, data = prepare_data(data=data)
            self.write_frame(final=True, op_code=op_code, data=data)

        # 多条数据，循环发送数据帧
        elif isinstance(data, Iterator):
            iter_data = iter(data)
            try:
                data_chunk = next(iter_data)
            except Iterator:
                return
            op_code, data = prepare_data(data_chunk)

            # First fragment.
            await self.write_frame(False, op_code, data)

            # Other fragments.
            for data_chunk in iter_data:
                confirm_op_code, data = prepare_data(data_chunk)
                if confirm_op_code != op_code:
                    raise TypeError("data contains inconsistent types")
                await self.write_frame(False, confirm_op_code, data)

            # Final fragment.
            await self.write_frame(True, OpCode.FINAL, b"")


def prepare_data(data: MessageData) -> Tuple[OpCode, bytes]:
    if isinstance(data, str):
        return OpCode.STR, data.encode(constants.CHARACTER)
    elif isinstance(data, (bytes, bytearray)):
        return OpCode.BYTES, data
    else:
        raise TypeError("data must be bytes-like or str")


class MessageJoiner:

    def __init__(
            self,
            op_code: OpCode,
            final: bool,
            data: Optional[bytes],
            max_size: Optional[int] = None
    ):
        self.__message_data = []
        self.op_code = op_code
        self.final = final
        self.max_size = max_size
        if data:
            self.append(data)

    @property
    def decoder(self):
        decoder = None
        character = constants.CHARACTER
        if self.op_code == OpCode.STR:
            decoder_factory = codecs.getincrementaldecoder(character)
            decoder = decoder_factory(errors="strict")
        return decoder

    def append(self, data):
        assert self.max_size is int, f'Max size type must be <int>'
        if self.decoder:
            self.__message_data.append(self.decoder.decode(data, self.final))
        else:
            self.__message_data.append(data)

    @property
    def data(self):
        connector = ''
        if self.op_code == OpCode.STR:
            connector = ''
        elif self.op_code == OpCode.BYTES:
            connector = b''
        return connector.join(self.__message_data)
