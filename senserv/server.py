import multiprocessing
import socket
import dash_bootstrap_components as dbc

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from .pages.page_status import PageStatus
from dash.dependencies import Input, Output
from senserv.sensor_wrapper import *
from .locatino import Location

location=Location()
template="simple_white"


print(socket.gethostname())
if socket.gethostname() == "roomba":
    import board
    import busio
    import adafruit_ahtx0
    import adafruit_bmp280

    sensor = AHT(adafruit_ahtx0.AHTx0(board.I2C()))
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor2 = BMP(adafruit_bmp280.Adafruit_BMP280_I2C(i2c))
    sl = SensorsSystem([sensor, sensor2], location=location, interval=30)
else:

    test_sensors = SensorWrapper(
        TestSensor(), ["temperature", "pressure"]), SensorWrapper(TestSensor2(),
                                                                  ["temperature", "humidity"])

    sl = SensorsSystem(test_sensors)

external_stylesheets = [dbc.themes.BOOTSTRAP, 'https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)




@app.callback(Output("output", "children"), [Input("new-location-button", "n_clicks")])
def on_button_click(n):
    if n is None:
        return None
    else:
        return dbc.Input(id="text-field", debounce=True, placeholder="Type something...", type="text")

@app.callback([Output("success", "children"),
               Output("location_drop-down", "options")], [Input("text-field", "value")])
def output_text(value):
    if value is not None:
        if not(""== value or "Type something..."==value):
            location.set(value)
            s = Store(location=location, keys=sl.sl._keys)
            return dbc.Alert(value + " created!"), s.tables()


@app.callback(Output("content", "children"),
    [dash.dependencies.Input('location-drop-down', 'value')])
def update_output(value):
    print("selector says:", value)
    location.set(value)
    return PageStatus(location=location, sl=sl).get_layout()



from .pages.navbar import navbar
app.layout = html.Div(children=[
        html.Title("Roomba"),
        navbar(),
        html.Div(id="selector", children=dbc.Row([
                dbc.Col(dbc.Select(options=[{"label":x, "value":x} for x in Store(keys=[]).tables()],
                                   value=location.get(),
                                         id="location-drop-down",
                                         ),width=4),
            dbc.Col(dbc.Button("new", outline=True, id="new-location-button", className="mr-2", size="sm"), width=2)]
        )),
        html.Div(id="content", children=None)
        ])



if __name__ == '__main__':
    try:
        sl.run()
    except:
        pass
    app.run_server(debug=False, host='0.0.0.0', port=8050)
