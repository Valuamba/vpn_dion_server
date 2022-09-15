from config import Config
from statistics.collect_statistics import get_ram, get_network_statistics, get_cpu
from statistics.models import ServerStatistic
from wireguard.wireguard_shell_script import add_client_wireguard, remove_wireguard, health_check
from logging.config import dictConfig
from flask import Flask, send_file
from getmac import get_mac_address as gma

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


app = Flask(__name__)


@app.route("/device-configuration")
def device_configuration():
    return {
        'MAC': gma()
    }


@app.route("/addClient/<client_name>")
def add_client(client_name: str):
    app.logger.info(f'Add client with name {client_name}')
    response = add_client_wireguard(client_name)
    return response.__dict__


@app.route("/removeClient/<client_name>")
def remove_client_post(client_name: str):
    response = remove_wireguard(client_name)
    return response.__dict__


@app.route("/health")
def check():
    response = health_check()
    return response.__dict__


@app.route("/collect-statistics")
def collect_statistic():
    app.logger.info(f'Collect statistics')
    ram = get_ram()
    cpu = get_cpu()
    upload, download, total, upload_speed, down_speed = get_network_statistics()
    server_statistic = ServerStatistic(network_upload=upload,
                                       network_download=download,
                                        total=total,
                                        network_upload_speed=upload_speed,
                                        network_download_speed=down_speed,
                                        ram=ram,
                                        cpu=cpu)

    return server_statistic.__dict__


if __name__ == "__main__":
    port = Config.VPN_SERVER_PORT
    app.run(debug=True, host='0.0.0.0', port=port)