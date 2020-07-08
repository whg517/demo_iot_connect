from pydantic import BaseModel


class RemoteAddress(BaseModel):
    host: str
    port: int
