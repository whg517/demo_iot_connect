import pytest

from demo_iot_connect.socket_server.routing import (Route, Router,
                                                    request_response)
from tests.conftest import AsyncMock


def index(request):
    return request


async def async_index(request):
    return request


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('method',),
    [
        (async_index,),
        (index,)
    ]
)
async def test_req_resp(method):
    req = 'foo'
    receive_mocker = AsyncMock(return_value=req)
    send_mocker = AsyncMock(return_value='')
    app = request_response(method)
    args = [AsyncMock(), receive_mocker, send_mocker]
    await app(*args)
    assert receive_mocker.called
    assert send_mocker.called_with(req)


class TestRoute:

    @pytest.mark.asyncio
    async def test_handle(self, mocker):
        req = 'foo'
        receive_mocker = AsyncMock(return_value=req)
        send_mocker = AsyncMock(return_value='')
        route = Route('/', index)
        await route.handle(AsyncMock(), receive_mocker, send_mocker)
        assert send_mocker.called_with(req)


class TestRouter:

    def test_add_route(self, mocker):
        router = Router()
        router.add_route(mocker.MagicMock())
        assert len(router.routes) == 1

    @pytest.mark.asyncio
    async def test_call(self):
        router = Router()
        route_mocker = AsyncMock()
        router.add_route(route_mocker)
        await router(AsyncMock(), AsyncMock(), AsyncMock())
        assert route_mocker.handle.called
