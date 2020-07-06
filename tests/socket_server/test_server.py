import asyncio
from asyncio.base_events import Server as AioServer

import pytest

from demo_iot_connect.socket_server.server import Config, Server, run
from tests.conftest import AsyncMock


@pytest.mark.parametrize(
    ('loop', 'called'),
    [
        (None, True),
        (asyncio.get_event_loop(), False)
    ]
)
def test_config(mocker, loop, called):
    get_event_loop_mocker = mocker.patch.object(asyncio, 'get_event_loop')
    Config(mocker.MagicMock(), loop)
    assert get_event_loop_mocker.called == called


class TestServer:

    @pytest.mark.asyncio
    async def test_start_up(self, mocker, caplog):
        server = Server(mocker.MagicMock(), loop=AsyncMock())
        await server.start_up()
        assert server.loop.create_server.called
        assert 'Server bind:' in caplog.text

    @pytest.mark.asyncio
    async def test_run(self, mocker, caplog):
        server = Server(mocker.MagicMock(), )
        socket_server_mocker = mocker.patch.object(AioServer, 'serve_forever', new_callable=AsyncMock)
        await server.run()
        assert socket_server_mocker.called
        assert 'Server started.' in caplog.text


def test_run(mocker, ):
    loop_mocker = mocker.MagicMock()
    get_event_loop_mocker = mocker.patch.object(asyncio, 'get_event_loop', return_value=loop_mocker)
    run(mocker.MagicMock())
    assert get_event_loop_mocker.called
    assert loop_mocker.create_task_called
    assert loop_mocker.run_forever.aclled
