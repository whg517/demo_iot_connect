import os

from dynaconf import Dynaconf

base_dir = os.path.dirname(os.path.dirname(__file__))

settings_files = [os.path.join(os.path.dirname(__file__), 'settings.yaml')]  # 指定绝对路径加载默认配置

settings = Dynaconf(
    envvar_prefix="DEMO_IOT_CONNECT",  # 环境变量前缀。设置`DEMO_IOT_CONNECT_FOO='bar'`，使用`settings.FOO`
    settings_files=settings_files,
    environments=True,  # 启用多层次日志，支持 dev, pro
    load_dotenv=True,  # 加载 .env
    env_switcher="DEMO_IOT_CONNECT_ENV",  # 用于切换模式的环境变量名称 DEMO_IOT_CONNECT_ENV=production
    lowercase_read=False,  # 禁用小写访问， settings.name 是不允许的
    # includes=['/etc/demo_iot_content/settings.yml'],  # 自定义配置覆盖默认配置
    base_dir=base_dir,  # 编码传入配置
)
