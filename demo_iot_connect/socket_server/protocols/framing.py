from enum import IntEnum
from typing import Awaitable, Callable, Optional, Union


class OpCode(IntEnum):
    STR = 1
    BYTES = 2
    FINAL = 3


class Frame:
    default_max_length = 255

    def __init__(
            self,
            final: bool,
            data: bytes,
            op_code: OpCode,
            max_size: Optional[int] = None
    ):
        """
        :param final    定义是不是最后一帧数据
        :param data:    帧中的数据
        :param op_code: 数据操作代码
            OpCode.STR 为字符串
            OpCode.BYTES 为字节
            OpCode.FINAL 为最后帧
        :param max_size:    一帧数据的最大长度
        """
        self.final = final
        self.data = data
        self.op_code = op_code
        self._max_size = max_size or self.default_max_length

    @classmethod
    async def read(
            cls,
            reader: Callable[[int], Awaitable[bytes]],
            max_size: Optional[int] = None
    ) -> 'Frame':
        """
        bytes -> frame bytes
        通过从异步IO流中读取数据，根据数据帧格式返回一个标准数据帧
        :return:
        """
        raise NotImplementedError

    def write(self, writer: Callable[[bytes], None]) -> None:
        """
        :param writer:
        :return:
        """
        raise NotImplementedError

    def check(self) -> None:
        raise NotImplementedError
