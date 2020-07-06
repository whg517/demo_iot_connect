from demo_iot_connect.socket_server.app import Application
from demo_iot_connect.socket_server.routing import Route


async def index(req):
    print(req)

# 增加路由
routes = [Route('/', index)]

# 初始化 app 对象
app = Application(
    routes=routes,
)
