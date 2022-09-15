from config import Config
from flask import Flask, send_file

app = Flask(__name__)
import server

if __name__ == "__main__":
    port = Config.VPN_SERVER_PORT
    app.run(debug=True, host='0.0.0.0', port=port)