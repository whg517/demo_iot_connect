import pytest

from demo_iot_connect.socket_server.app import Application
from tests.conftest import AsyncMock


class TestApplication:

    @pytest.mark.asyncio
    async def test_call(self):
        app = Application([AsyncMock()])
        app.router = AsyncMock()
        await app(AsyncMock(), AsyncMock(), AsyncMock())

        assert app.router.called
