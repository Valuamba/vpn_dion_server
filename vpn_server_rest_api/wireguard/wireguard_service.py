import enum
import os.path
import re
import sys
import configparser
import pexpect

from config import Config
from wireguard.models import Options, ClientConfigDto


def add_client_config(client_name: str):
    if os.path.exists(os.path.join(Config.HOME_DIRECTORY, Config.TEMPLATE_WIREGUARD % client_name)):
        raise Exception(f'Wireguard config for client name {client_name} already exists.')

    select_option = "Select an option [1-4]: "
    client_name_text = "Client name:"
    wireguard_ipv4 = "Client's WireGuard IPv4:"
    wireguard_ipv6 = "Client's WireGuard IPv6:"

    child = pexpect.spawn(Config.WIREGUARD_SCRIPT_PATH, encoding='utf-8')
    child.logfile = sys.stdout
    child.expect(f'.*{re.escape(select_option)}.*', timeout=1)
    child.send(f"{Options.AddNewUser}\n")
    child.expect(client_name_text, timeout=1)
    child.send(f'{client_name}\n')
    child.expect(wireguard_ipv4, timeout=1)
    child.send('\n')
    child.expect(wireguard_ipv6, timeout=1)
    child.send('\n')

    return child.read()


def remove_client(client_name: str):
    if not os.path.exists(os.path.join(Config.HOME_DIRECTORY, Config.TEMPLATE_WIREGUARD % client_name)):
        raise Exception(f'Wireguard config for client name {client_name} was not find.')

    select_option = "Select an option [1-4]: "
    child = pexpect.spawn(Config.WIREGUARD_SCRIPT_PATH, encoding='utf-8')
    # child.logfile = sys.stdout
    child.logfile = None
    child.expect(f'.*{re.escape(select_option)}.*', timeout=1)
    child.send(f"{Options.RevokeExistingUser}\n")
    s = child.expect(client_name)
    users_sh_text = child.read()

    pass


def build_path_to_wireguard_config(client_name):
    return os.path.join(Config.HOME_DIRECTORY, f'wg0-client-{client_name}.conf')


def parse_wireguard_config(client_name: str) -> ClientConfigDto:
    config = configparser.ConfigParser()
    config.read(build_path_to_wireguard_config(client_name))

    return ClientConfigDto(
        private_key=config['Interface']['PrivateKey'],
        address=config['Interface']['Address'],
        dns=config['Interface']['DNS'],
        public_key=config['Peer']['PublicKey'],
        preshared_key=config['Peer']['PresharedKey'],
        endpoint=config['Peer']['Endpoint'],
        allowed_ips=config['Peer']['AllowedIPs']
    )