from typing import Optional

import click

from demo_iot_connect.api import app
from demo_iot_connect.config import settings
from demo_iot_connect.socket_server.server import run


@click.command()
@click.option('-h', '--host', default='127.0.0.1', help='Set server host')
@click.option('-p', '--port', default=8000, help='Set server port')
def main(
        host: Optional[str] = settings.HOST,
        port: Optional[int] = settings.PORT,
):
    """

    :param host:    settings default host: 127.0.0.1
    :param port:    settings default port: 8000
    :return:
    """
    run(
        app=app,
        host=host,
        port=port
    )


if __name__ == '__main__':
    main()
