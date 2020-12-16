import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from senserv.sensor_wrapper import *
import multiprocessing



class TestSensor:
    def __init__(self):
        self.temperature = 40
        self.pressure = 1000
class TestSensor2:
    def __init__(self):
        self.temperature = 20
        self.humidity = 234

test_list_sensors= SensorWrapper(TestSensor(), ["temperature", "pressure"]),  SensorWrapper(TestSensor2(), ["temperature","humidity"])
sensors= SensorWrapper(TestSensor(), ["temperature", "pressure"]),  SensorWrapper(TestSensor2(), ["temperature","humidity"])
sl = SensorList(sensors)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

def create_plot():
    df = pd.read_csv(sl._log_file, sep="\t")[-100:]
    # df = pd.read_csv("/home/jb/git/senserv/senserv/2020-12-15_19:17:44_measurement.log", sep="\t")
    for cls in df.columns:
        if cls != "timestamp":
            df[cls] = df[cls].map(lambda x: sum([float(y) for y in x[1:-1].split(',')]) / len(x[1:-1].split(',')))
    fig = px.scatter(df, x="timestamp", y="temperature")
    return fig



def get_layout():
    return html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=create_plot()
    )
])

app.layout = get_layout

if __name__ == '__main__':
    daemonLoop = multiprocessing.Process(name='Daemon', target=sl.run)
    daemonLoop.start()
    app.run_server(debug=True)