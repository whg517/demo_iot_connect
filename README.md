# demo iot connect

本项目基于 Python 3 开发，推荐安装 Python 3.7

本项目是为了收发终端数据而开发的基于 [ASGI](https://asgi.readthedocs.io/en/latest/) 规范而实现的 Server。仅用于测试。

## Usage:

1. git clone

```
git clone https://github.com/whg517/demo_iot_connect.git
```

2. 初始化环境

项目使用 [pipenv](https://pipenv-fork.readthedocs.io/en/latest/) 做环境管理，请先安装最版本的 pipenv

```
cd demo_iot_connect
pip install -U pipenv
pipenv install -d
```

3. 运行项目

```
python demo_iot_connect/cmdline.py
```

使用 `python demo_iot_connect/cmdline.py --help` 查看帮助命令

如果需要直接使用命令，可以先将项目安装到环境即可直接使用 `server --help`