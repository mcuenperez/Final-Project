import plotly
import plotly.graph_objects as go
import dash
from dash.dependencies import Output, Input, State
from dash import dcc
from dash import html, dash_table
from collections import deque
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

import serial
import re

dataset=pd.read_csv('C:/Users/mcuenperez/Downloads/data.csv', header=None)


x = deque(maxlen=1000)
light_list = deque(maxlen=1000)

ser = serial.Serial()
ser.port = 'COM7'
ser.baudrate = 9600

ser.open()

def serialRead(ser):
    light_value = ser.readline() 
    print(light_value)
    data_string = light_value.decode("utf-8") 
    data = re.findall(r'\d+', data_string) 
    if len(data) > 0:
        print(data[0])
        return int(data[0]) 
    else:
        return None 
    
graph= html.Div([
     dcc.Graph(id='live-graph', animate=True),
     dcc.Interval(
         id='graph-update',
         interval=400, 
         n_intervals=0
     ),
 ])


dataset=pd.read_csv('data.csv', header=None)
dataset=dataset[[1, 2]]
dataset=dataset.rename(columns={1: 'Time', 2: 'Light Sensor'})

dataset2=dataset.sort_values('Time', ascending=False)
alarm=dataset2['Time'].iloc[0]
lastalarm=dbc.Alert(f"Last time alarm went off: {alarm}", color="info")



login_form = dbc.Card([
        dbc.CardHeader("User Login"),
        dbc.CardBody([
                dbc.Row([
                        dbc.Label("Username"),
                        dbc.Input(
                            id="username-input", type="text", placeholder="Enter your username"),
                    ]),
                dbc.Row([
                        dbc.Label("Password"),
                        dbc.Input(
                            id="password-input", type="password", placeholder="Enter your password"),
                    ]),
                    html.Br(),
                dbc.Button("Login", id="login-button", color="success"),
            ]),
    ],
    className="mt-3",)

table=dash_table.DataTable(dataset.to_dict('records'), [{"name": i, "id": i} for i in dataset.columns])

dashboard = dbc.Card([
        dbc.CardHeader('User Interface'),
        dbc.CardBody(id='dashboard-body'),
    ],
    className="mt-3",)

tab1 = dbc.Card(
  dbc.CardBody([
      html.H1('Home', style={'font-size': 'large'}),
      html.P('Soteria Security assures the safety and protection of your home whether inside or out. In addition to the door, with this web you will be able to see the last time the alarm went off, the ability to visualize the alarm system history, a real time graph which shows how the system is working and frequently asked questions with statistical analysis. Thank you for trusting us to be there!'),
      html.Br(), 
      lastalarm,
      html.Br(),
      html.H1('Alarm System History', style={'font-size': 'medium'}),
      table,
  ]),
  className="mt-1",)

tab2=dbc.Card(
  dbc.CardBody([
      html.H1('Statistical Analysis', style={'font-size': 'large'}),
      graph,
]),
  className="mt-1",)

tabs=dbc.Container([
    dbc.Row([
    dbc.Col([
      dbc.Tabs([
        dbc.Tab(tab1, label='Home'),
        dbc.Tab(tab2, label='Statistics'),])
      ])
    ])  
  ])

           
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container([
    dbc.Row([
    dbc.Col([
      dbc.NavbarSimple(
        brand="Soteria Security",
        brand_href="#",
        color="success",
        dark=True,
      ),
      html.Br(),
      html.P('"We are there because we care."', style={"font-size": "large", "font-style": "italic", "color": "green"}),
      login_form, dashboard
      ])
    ])  
  ])

@app.callback(
    Output('dashboard-body', 'children'),
    Input('login-button', 'n_clicks'),
    State('username-input', 'value'),
    State('password-input', 'value'),
)
def login(n_clicks, username, password):
    if n_clicks is None:
       
        return

    if username == "mcuenperez" and password == "password1":
        return [
            html.P("Welcome, Macarena Cuen!"),
            tabs,
        ]
@app.callback(Output('live-graph','figure'), 
               [Input('graph-update', 'n_intervals')])
def update_graph_scatter(input_data): 
    light = serialRead(ser)
    x.append(x[-1]+1 if len(x)>0 else 1)
    light_list.append(light)
    data = go.Scatter(
        x=list(x),
        y=list(light_list),
        name='Scatter',
        mode='lines+markers'
    )
    return{'data': [data], 'layout' : go.Layout(xaxis=dict(range=[min(x),max(x)]),
                                                yaxis=dict(range=[0,1000]),
                                                xaxis_title='Time Step (s)',
                                                yaxis_title='Light sensor')}



if __name__ == '__main__':
    app.run_server(debug=False, port=8060)
