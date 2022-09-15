import configparser
import pprint
import re
import subprocess

# home = "/home/valuamba/TelegramBots/vpn-dion/vpn_server_rest_api/tests"
# p = subprocess.Popen("bash ../scripts/some.sh", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
# out, err = p.communicate()
#
# print(out)
# print(err)

c = '''
Bash line: bash /home/valuamba/TelegramBots/vpn-dion/vpn_server_rest_api/scripts/wireguard.sh add --name 21312
CONFIG: 
  [CheckOS]
  OS=ubuntu
  
Check Dot existance
Check ipv4 existance

  [Does_ipv4_exit]
  CLIENT_WG_IPV4=10.66.66.2
  
Check IPv6 existance

  [Does_ipv6_exit]
  CLIENT_WG_IPV6=10.66.66.2
  
INFO: Client was checked.
Generating client name
Client name: 21312_21
Check client existance

  [NewClient]
  ConfigPath=/home/valuamba/wg0-client-21312_21.conf
'''

config_path = re.search("(?<=ConfigPath=).*", c)
m = config_path.group()
pass
# config = configparser.ConfigParser()
# config.read('/home/valuamba/wg0-client-21312_2.conf')
# s = config['Interface']['PrivateKey']
# pprint.pprint(config['Interface']['PrivateKey'])
# pprint.pprint(config['Interface']['Address'])
# pprint.pprint(config['Interface']['DNS'])
# pprint.pprint(config['Peer']['PublicKey'])
# pprint.pprint(config['Peer']['PresharedKey'])
# pprint.pprint(config['Peer']['Endpoint'])
# pprint.pprint(config['Peer']['AllowedIPs'])

    # return ClientConfigDto(
    #     private_key=config['Interface']['PrivateKey'],
    #     address=config['Interface']['Address'],
    #     dns=config['Interface']['DNS'],
    #     public_key=config['Peer']['PublicKey'],
    #     preshared_key=config['Peer']['PresharedKey'],
    #     endpoint=config['Peer']['Endpoint'],
    #     allowed_ips=config['Peer']['AllowedIPs']
    # )