import os.path
from os import path
from pathlib import Path
from typing import NamedTuple

from environs import Env


class Config(NamedTuple):
    __env = Env()
    __env.read_env(os.path.join(os.getcwd(), '.env'))

    BASE_DIR = Path(__name__).resolve().parent

    HOME_DIRECTORY = __env.str('HOME_DIRECTORY', os.path.expanduser('~'))
    WIREGUARD_DIRECTORY = __env.str('WIREGUARD_DIRECTORY', '/etc/wireguard/')
    VPN_SERVER_PORT = __env.int('VPN_SERVER_PORT', 5000)

    WIREGUARD_SCRIPT_PATH = path.abspath(os.path.join(BASE_DIR, './scripts/wireguard.sh'))
    TEMPLATE_WIREGUARD = f'wg0-client-%s.conf'