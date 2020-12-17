import multiprocessing
import socket

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import plotly.io as pio

from senserv.sensor_wrapper import *

location="Arbeitszimmer"
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

    test_list_sensors = SensorWrapper(
        TestSensor(), ["temperature", "pressure"]), SensorWrapper(TestSensor2(),
                                                                  ["temperature",
                                                                   "humidity"])
    test_sensors = SensorWrapper(
        TestSensor(), ["temperature", "pressure"]), SensorWrapper(TestSensor2(),
                                                                  ["temperature", "humidity"])

    sl = SensorsSystem(test_sensors)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

# def create_plot():
#     df = pd.read_csv(sl._log_file, sep="\t")[-100:]
#     # df = pd.read_csv("/home/jb/git/senserv/senserv/2020-12-15_19:17:44_measurement.log", sep="\t")
#     for cls in df.columns:
#         if cls != "timestamp":
#             df[cls] = df[cls].map(lambda x: sum([float(y) for y in x[1:-1].split(',')]) / len(x[1:-1].split(',')))
#
#     df = df[["timestamp", "temperature", "relative_humidity"]]
#     df1 = df.melt(id_vars=['timestamp'], value_vars= ["temperature", "relative_humidity"], var_name='a')
#     fig = px.line(df1, x='timestamp', y='value', color='a')
#     # fig = px.line(df, x="timestamp", y="temperature")
#     # fig.add_trace(x=df[["timestamp"]], y=df[["relative_humidity"]])
#     return fig

#
# def get_temperature_plot():
#     df = pd.read_csv(sl._log_file, sep="\t")[-100:]
#     for cls in df.columns:
#         if cls != "timestamp":
#             df[cls] = df[cls].map(lambda x: sum([float(y) for y in x[1:-1].split(',')]) / len(x[1:-1].split(',')))
#     fig = px.line(df, x="timestamp", y="temperature")
#     # fig.add_scatter(df, x="timestamp", y="temperature")
#     return fig
#
def get(*args, **kwargs):
    store = Store(keys=sl.sl._keys, location=location)
    return store.read(*args, **kwargs)

def getspark(w="relative_humidity"):
    df = get(w)[-200:]
    return spark(df["timestamp"].tolist(), df[w].tolist())

import plotly.graph_objects as go
def spark(x,y):
    avg= sum(y)/ len(y)

    fig = px.line(x=x, y=y, height=60, width=100)
    fig.add_trace(go.Scatter(x=x, y=[avg for _ in y]))#, color="firebrick", dash='dash')
    fig.add_trace(go.Scatter(x=x, y=y, fill='tonexty', mode="none"))

    # hide and lock down axes
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    # fig.update_layout(
    #     yaxis=dict(
    #         tick0=round(,2),
    #         nticks=1
    #     )
    # )
    # remove facet/subplot labels
    fig.update_layout(annotations=[], overwrite=True)

    # strip down the rest of the plot
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        margin=dict(t=10, l=10, b=10, r=10)
    )
    return fig


def format(x):
    return f"{round(x, 1)}"

def get_current():
    r = sl.all()

    return [
        html.Div([
            html.Div(f"Temperature:\t{format(r['temperature'])}°C"),
                  dcc.Graph(id='temperature',figure=getspark("temperature"),  style={"height" : "25%", "width" : "100%"}, config={'displayModeBar': False})]),
        html.Br(),
        html.Div(children=f"Humidity:\t{format(r['relative_humidity'])}%"),
        dcc.Graph(id='humidity', figure=getspark("relative_humidity"), style={"height": "25%", "width": "100%"},
                config={'displayModeBar': False}),
        html.Br(),
        html.Div(children=f"Pressure:\t{format(r['pressure'])} mbar"),
        dcc.Graph(id='pressure', figure=getspark("pressure"), style={"height": "25%", "width": "100%"},
                config={'displayModeBar': False}),
        html.Br()

    ]

def get_layout():
    return html.Div(children=[
        html.Title("Roomba"),
        html.H2(children='Hello, this is ROOMBA!'),
        html.H3(children=location),

        html.Div(children=get_current()),

    ])


app.layout = get_layout

if __name__ == '__main__':
    sl.run()
    app.run_server(debug=False, host='0.0.0.0', port=8050)
