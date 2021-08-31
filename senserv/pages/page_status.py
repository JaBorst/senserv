import dash
import dash_bootstrap_components as dbc

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from .navbar import navbar
from ..sensor_wrapper import Store



class PageStatus:
    def __init__(self, location, sl):
        self.location = location
        self.sl = sl
        self.sl.change_location(self.location)

        self.col_width1= 2
        self.col_width2 = 4

    def get_current(self):
        r = self.sl.all()

        return [
            dbc.Row(
                [
                    dbc.Col(html.Div(f"Temperature:\t{format(r['temperature'])}°C"), width=self.col_width1),
                    dbc.Col(dcc.Graph(id='temperature', figure=self.getspark("temperature"),
                                      style={"height": "25%", "width": "100%"}, config={'displayModeBar': False}), width=self.col_width2)
                ]),
            dbc.Row(
                [
                    dbc.Col(html.Div(children=f"Humidity:\t{format(r['relative_humidity'])}%"), width=self.col_width1),
                    dbc.Col(dcc.Graph(id='humidity', figure=self.getspark("relative_humidity"),
                                      style={"height": "25%", "width": "100%"},
                                      config={'displayModeBar': False}), width=self.col_width2)
                ]),
            dbc.Row(
                [dbc.Col(html.Div(children=f"Pressure:\t{format(r['pressure'])} mbar"), width=self.col_width1),
                 dbc.Col(dcc.Graph(id='pressure', figure=self.getspark("pressure"), style={"height": "25%", "width": "100%"},
                                   config={'displayModeBar': False}), width=self.col_width2)]),
        ]

    def get(self, *args, **kwargs):
        store = Store(keys=self.sl.sl._keys, location=self.location)
        return store.read(*args, **kwargs)

    def tables(self):
        store = Store(keys=self.sl.sl._keys, location=self.location)
        return store.tables()


    def getspark(self, w="relative_humidity"):
        df = self.get(w)[-200:]
        return self.spark(df["timestamp"].tolist(), df[w].tolist())

    def spark(self,x,y):
        avg= sum(y)/ len(y)

        fig = px.line(x=x, y=y, height=60, width=100)
        fig.add_trace(go.Scatter(x=x, y=[avg for _ in y]))#, color="firebrick", dash='dash')
        fig.add_trace(go.Scatter(x=x, y=y, fill='tonexty', mode="none"))

        # hide and lock down axes
        fig.update_xaxes(visible=False, fixedrange=True)
        fig.update_yaxes(visible=False, fixedrange=True)
        fig.update_layout(annotations=[], overwrite=True)

        # strip down the rest of the plot
        fig.update_layout(
            showlegend=False,
            plot_bgcolor="white",
            margin=dict(t=10, l=10, b=10, r=10)
        )
        return fig

    def get_layout(self):
        try:
            return [
                dbc.Row(children=[dbc.Col(id="output", width=4, style={"vertical-align": "middle"}), dbc.Col(id="success", width=2)]),
                html.Div(children=self.get_current())
            ]
        except:
            return ["Error"]


def format(x):
    return f"{round(x, 1)}"


