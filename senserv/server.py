from senserv.sensor_wrapper import *

from sanic import Sanic, response
import numpy as np
import pathlib
from datetime import datetime

import multiprocessing
# import board
# import adafruit_ahtx0
import time
# import adafruit_bmp280
# import busio



class TestSensor:
    def __init__(self):
        self.temperature = 40
        self.pressure = 1000
class TestSensor2:
    def __init__(self):
        self.temperature = 20
        self.humidity = 234

test_list_sensors= SensorWrapper(TestSensor(), ["temperature", "pressure"]),  SensorWrapper(TestSensor2(), ["temperature","humidity"])


app = Sanic(name="senserv")
app.static('/','./index.html')
sensors= SensorWrapper(TestSensor(), ["temperature", "pressure"]),  SensorWrapper(TestSensor2(), ["temperature","humidity"])
sl = SensorList(sensors)



def start_server(host="0.0.0.0", port="8000", cert=None, key=None):
    # Start the Server
    if cert is not None and key is not None:
        import ssl
        context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=cert,
                            keyfile=key)

        app.run(host=host, port=int(port), ssl=context)
    else:
        app.run(host=host, port=int(port))


###### Directives
import json
import pandas as pd
@app.route("/data", methods=["GET"])
def data(request):
    return response.json(pd.read_csv(sl._log_file).to_json())


import plotly
import plotly.graph_objs as go
import json
@app.route("/vis", methods=["GET"])
def vis(request):
    df = pd.read_csv(sl._log_file, sep="\t")
    for cls in df.columns:
        if cls != "timestamp":
            df[cls] = df[cls].map(lambda x: sum([float(y) for y in  x[1:-1].split(',')])/len( x[1:-1].split(',')))
    trace = go.Scatter(
        x=df[["timestamp"]],
        y=df[["pressure"]]
    )
    data = [trace]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return response.json(graphJSON)

# ToDo:
# - interactive visualization
# - possibility for named logs
# - possibility to start a new measure series from frontend


def main():
    import argparse
    parser = argparse.ArgumentParser("Run the logs!")
    parser.add_argument("--interval", dest="interval", type=int, help="Distance between two measurements.")
    parser.add_argument("--file", dest="file", type=str, help="log file.")
    parser.add_argument('--host', default="0.0.0.0", metavar='host', type=str, help='host ip ')
    parser.add_argument('--port', default=4321, dest='port', type=str, help='Port for the server')
    parser.add_argument('--cert', default=None, dest='cert', help='Path to the ssl-certificate')
    parser.add_argument('--key', default=None, dest="key", help='Path to the ssl-key')
    args = parser.parse_args()
    # sensor = adafruit_ahtx0.AHTx0(board.I2C())
    # i2c = busio.I2C(board.SCL, board.SDA)
    # sensor2 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

    global sl
    daemonLoop = multiprocessing.Process(name='Daemon', target=sl.run)
    daemonLoop.start()
    start_server(host=args.host, port=args.port, cert=args.cert, key=args.key)

main()