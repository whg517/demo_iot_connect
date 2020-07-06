from unittest.mock import MagicMock


class AsyncMock(MagicMock):
    """
    AsyncMock
    ref: https://stackoverflow.com/a/32498408/11722440
    """

    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)

    def __await__(self, *args, **kwargs):
        return self
