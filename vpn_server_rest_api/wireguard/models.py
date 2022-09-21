import enum
from typing import Optional, List

from pydantic import BaseModel


class Options(enum.IntEnum):
    AddNewUser = 1
    RevokeExistingUser = 2
    UninstallWireGuard = 3
    Exit = 4


class ClientConfigDto:
    private_key: str
    address: str
    dbs: str

    public_key: str
    preshared_key: str
    endpoint: str
    allowed_ips: str

    def __init__(self, **kwargs):
        self.private_key = kwargs['private_key']
        self.address = kwargs['address']
        self.dns = kwargs['dns']
        self.public_key = kwargs['public_key']
        self.preshared_key = kwargs['preshared_key']
        self.endpoint = kwargs['endpoint']
        self.allowed_ips = kwargs['allowed_ips']


class WgInfo(BaseModel):
    peer: Optional[str]
    preshared_key: Optional[str]
    endpoint: Optional[str]
    allowed_ips: Optional[str]
    latest_handshake: Optional[str]
    transfer: Optional[str]


class WgInfoList(BaseModel):
    __root__: List[WgInfo]