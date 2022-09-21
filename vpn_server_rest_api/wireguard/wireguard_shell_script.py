import configparser
import json
import os

# from config import Config
import pprint
import re
import subprocess
import subprocess
import re
from config import Config
from response_model import ResponseModel
from flask import current_app as app

from wireguard.models import ClientConfigDto

from wireguard.utils import create_wg_info

from wireguard.models import WgInfoList


class WireguardCommand:
    AddClient = "add"
    RemoveClient = "remove"
    CheckClient = "check"


class WireguardParameter:
    Name = "--name"
    WireguardDirectory = "--wg-dir"
    HomeDirectory = "--home"
    IPv4 = "--ipv4"
    IPv6 = "--ipv6"


def add_client_wireguard(client_name,
                         home_dir=Config.HOME_DIRECTORY,
                         wg_dir=Config.WIREGUARD_DIRECTORY,
                         ipv4=None, ipv6=None) -> ResponseModel:

    # if os.path.exists(os.path.join(Config.HOME_DIRECTORY, Config.TEMPLATE_WIREGUARD % client_name)):
    #     return ResponseModel(is_successful=False, message=f'Wireguard config for client name {client_name} already exists.')

    # Config.WIREGUARD_SCRIPT_PATH = "../scripts/wireguard.sh"
    args = []
    args.append("bash")
    args.append(Config.WIREGUARD_SCRIPT_PATH)
    args.append(WireguardCommand.AddClient)
    args.append(f"{WireguardParameter.Name} {client_name}")
    if ipv4:
        args.append(f"{WireguardParameter.IPv4} {ipv4}")
    elif ipv6:
        args.append(f"{WireguardParameter.IPv6} {ipv4}")
    elif home_dir:
        args.append(f"{WireguardParameter.HomeDirectory} {home_dir}")
    elif wg_dir:
        args.append(f"{WireguardParameter.WireguardDirectory} {wg_dir}")

    bash_line = " ".join(args)
    print(f"Bash line: {bash_line}")

    try:
        p = subprocess.Popen(bash_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.communicate()
        out = out.decode('utf-8')
        err = err.decode('utf-8')

        if p.returncode == 0:
            config_path = re.search("(?<=ConfigPath=).*", out).group()
            config_name = os.path.basename(config_path)
            client_details = parse_wireguard_config(config_path)
            print(f"OUT: {config_name}\n{client_details.__dict__}")
            return ResponseModel(is_successful=True, message=f"Shell output: {out}",
                                 data={
                                     **client_details.__dict__, 'config_name': re.search('(?<=wg0-client-)(.*)(?=.conf)', config_name).group()
                                    }
                                 )
        elif p.returncode >= 1:
            print(f"ERROR: {out}\n{err}")
            return ResponseModel(is_successful=False, message=f"Command line exception: {out}\n{err}")

        raise Exception('Incorrect return code')
    except Exception as e:
        print(str(e))
        return ResponseModel(is_successful=True, message=f"Exception: {str(e)}")


def remove_wireguard(client_name,
                     home_dir=Config.HOME_DIRECTORY,
                     wg_dir=Config.WIREGUARD_DIRECTORY) -> ResponseModel:
    path = os.path.join(Config.HOME_DIRECTORY, Config.TEMPLATE_WIREGUARD % client_name)
    if not os.path.exists(path):
        return ResponseModel(is_successful=False, message=f'Wireguard config for client name {client_name} doesn\'t exist at path {path}.')

    # Config.WIREGUARD_SCRIPT_PATH = "../scripts/wireguard.sh"
    args = []
    args.append("bash")
    args.append(Config.WIREGUARD_SCRIPT_PATH)
    args.append(WireguardCommand.RemoveClient)
    args.append(f"{WireguardParameter.Name} {client_name}")
    if home_dir:
        args.append(f"{WireguardParameter.HomeDirectory} {home_dir}")
    elif wg_dir:
        args.append(f"{WireguardParameter.WireguardDirectory} {wg_dir}")

    bash_line = " ".join(args)
    print(f"Bash line: {bash_line}")

    try:
        p = subprocess.Popen(bash_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.communicate()
        out = out.decode('utf-8')
        err = err.decode('utf-8')

        if p.returncode == 0:
            print(f"OUT: ${out}")
            return ResponseModel(is_successful=True, message=f"Shell output: {out}")
        elif p.returncode >= 1:
            print(f"ERROR: {out}\n{err}")
            return ResponseModel(is_successful=False, message=f"Command line exception: {out}\n{err}")

        raise Exception('Incorrect return code')
    except Exception as e:
        print(str(e))
        return ResponseModel(is_successful=True, message=f"Exception: {str(e)}")


def health_check(home_dir=Config.HOME_DIRECTORY,
                 wg_dir=Config.WIREGUARD_DIRECTORY):
    args = []
    args.append("bash")
    args.append(Config.WIREGUARD_SCRIPT_PATH)
    args.append(WireguardCommand.CheckClient)
    if home_dir:
        args.append(f"{WireguardParameter.HomeDirectory} {home_dir}")
    elif wg_dir:
        args.append(f"{WireguardParameter.WireguardDirectory} {wg_dir}")

    bash_line = " ".join(args)
    print(f"Bash line: {bash_line}")

    try:
        p = subprocess.Popen(bash_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.communicate()
        out = out.decode('utf-8')
        err = err.decode('utf-8')

        if p.returncode == 0:
            print(f"OUT: ${out}")
            return ResponseModel(is_successful=True, message=f"Shell output: {out}")
        elif p.returncode >= 1:
            print(f"ERROR: {out}\n{err}")
            return ResponseModel(is_successful=False, message=f"Command line exception: {out}\n{err}")

        raise Exception('Incorrect return code')
    except Exception as e:
        print(str(e))
        return ResponseModel(is_successful=True, message=f"Exception: {str(e)}")


def parse_wireguard_config(config_path: str) -> ClientConfigDto:
    print(f'CONFIG: {config_path}')
    config = configparser.ConfigParser()
    config.read(config_path)

    return ClientConfigDto(
        private_key=config['Interface']['PrivateKey'],
        address=config['Interface']['Address'],
        dns=config['Interface']['DNS'],
        public_key=config['Peer']['PublicKey'],
        preshared_key=config['Peer']['PresharedKey'],
        endpoint=config['Peer']['Endpoint'],
        allowed_ips=config['Peer']['AllowedIPs']
    )


def collect_wg_infos():
    p = subprocess.Popen('wg show', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    out = out.decode('utf-8')
    err = err.decode('utf-8')
    try:
        if p.returncode >= 1:
            return ResponseModel(is_successful=False, message=f"Command line exception: {out}\n{err}")

        r = re.compile('(?P<key>([a-z]+(\s?))*):\s*(?:"([^"]*)"|(?P<value>.*))')
        matches = [m.groupdict() for m in r.finditer(out)]

        key_value_indexes = [idx for idx, match in enumerate(matches) if match['key'] == 'peer']

        key_value_pair_list = []
        for idx, key_index in enumerate(key_value_indexes):
            if idx == len(key_value_indexes) - 1:
                key_value_pair_list.append(create_wg_info(matches[key_index:]))
            else:
                key_value_pair_list.append(create_wg_info(matches[key_index: key_value_indexes[idx + 1]]))

        # return key_value_pair_list

        wgInfoList = WgInfoList(__root__=key_value_pair_list)

        # return wgInfoList
        return ResponseModel(is_successful=True, data=wgInfoList.json())
    except Exception as e:
        return ResponseModel(is_successful=True, message=f"Exception: {str(e)}")
