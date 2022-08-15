import json
import dash
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
#from sql_functions import *
import pandas as pd
import re
import numpy as np
Width= 1000
Height= 800
iso_to_iso = json.load(open("iso_to_iso.json","r"))
iso_eu = json.load(open("iso_eu.json","r"))
euro_map = json.load(open("europe.json","r"))
iso_to_name = json.load(open("iso_to_name.json","r"))
prod = json.load(open("products_100.json","r"))
iso2 = json.load(open("iso2.json","r"))
external_stylesheets = ['https://use.fontawesome.com/releases/v5.8.1/css/all.css']
name_list = ["Country","Import","Export"]
df = pd.read_csv("data/df_trade_full.csv")
df2 = pd.read_csv("data/imp_exp_new.csv")
df3 = pd.read_csv("data/product_per_country.csv")
df4 = pd.read_csv("data/import_exp_intra_extra_eu.csv")
iso_eu = json.load(open("iso_eu.json","r"))
def generate_rgb(impexp,nums):
    a = []
    start=[210, 34, 45]
    end = [35, 136, 35]
    middle1=[219, 158, 162]
    middle2=[160, 217, 160]
    max_num = nums.max()
    min_num = nums.min()
    if impexp ==2:
        for i in nums:
            p =(i-min_num)/(max_num-min_num)
            a1 = str(int(np.around(middle2[0]+((end[0]-middle2[0])*p))))
            a2 = str(int(np.around(middle2[1]+((end[1]-middle2[1])*p))))
            a3 = str(int(np.around(middle2[2]+((end[2]-middle2[2])*p))))
            a.append("rgb("+a1+","+a2+","+a3+")")
    if impexp == 1:
        for i in nums:
            p =(i-min_num)/(max_num-min_num)
            a1 = str(int(np.around(middle1[0]+((start[0]-middle1[0])*p))))
            a2 = str(int(np.around(middle1[1]+((start[1]-middle1[1])*p))))
            a3 = str(int(np.around(middle1[2]+((start[2]-middle1[2])*p))))
            a.append("rgb("+a1+","+a2+","+a3+")")
    if impexp == "REV":
        for i in nums:
            if i >= 0:
                p =i/max_num
                a1 = str(int(np.around(middle2[0]+((end[0]-middle2[0])*p))))
                a2 = str(int(np.around(middle2[1]+((end[1]-middle2[1])*p))))
                a3 = str(int(np.around(middle2[2]+((end[2]-middle2[2])*p))))
                a.append("rgb("+a1+","+a2+","+a3+")")
            elif i < 0:
                p =i/min_num
                a1 = str(int(np.around(middle1[0]+((start[0]-middle1[0])*p))))
                a2 = str(int(np.around(middle1[1]+((start[1]-middle1[1])*p))))
                a3 = str(int(np.around(middle1[2]+((start[2]-middle1[2])*p))))
                a.append("rgb("+a1+","+a2+","+a3+")")
    return a
plots = html.Div([ 
            html.Div([
                html.H3(children="EU trading by year", style={"fontSize":"150%"}),
                dcc.Dropdown(
                    id="Year",
                    options=[
                    {"label":"2016","value":"2016"},                
                    {"label":"2017","value":"2017"},
                    {"label":"2018","value":"2018"},
                    {"label":"2019","value":"2019"},
                    {"label":"2020","value":"2020"}],
                    multi=False,
                    value="2019",
                    style={'width': '40%'},
                    className=""),
                dcc.RadioItems(
                    id="ImpExp",
                    options = [{'label':'Import', 'value':1},{'label':'Export','value':2}, {'label':'Revenue','value':'REV'}], 
                    value= 1,inline=False, className="ImpExp"),
                html.Br(),
                html.Br(),
                html.Div([
                    dcc.Loading(id="ls-loading-1", children=[
                        html.Div([
                            html.Div([
                                html.Div([dcc.Graph(id='trading_map',config={'displayModeBar': False,'scrollZoom':False},className="graph")],className="col-6"),
                                html.Div([
                                    dcc.Graph(id='ranking_chart',config={'displayModeBar': False},className="graph col-md-12 "),
                                    dcc.Graph(id='imp-exp-perc',className="graph col-md-12")],className="col-6")],className="row"),
                            html.Div([
                                html.Div([dcc.Dropdown(id="Country-2",
                                    options = [{"label":iso_to_name[i],"value":i} for i in iso2], 
                                    value= 'AT')], className="col-6"),
                                html.Div([dcc.Dropdown(
                                    id="product",
                                    options = [{"label":j,"value":i} for i,j in prod.items()], 
                                    value= '10')], className="col-6")],
                                    className="d-flex row"),
                            html.Div([html.Div([
                                html.Div([dcc.Graph(id='imp-pie')],className="col-md-12"),
                                html.Div([dcc.Graph(id='exp-pie')],className="col-md-12")],className="col-6"),
                            html.Div([dcc.Graph(id="imp-exp-prod")],className="col-6")],className="row"),
                        ],className="graph-plot")
                    ])
                ]),
                html.Br(),
                dcc.Loading([dcc.Store(id="year_rev_selected")]),
                dcc.Loading(dcc.Store(id="store"), fullscreen=True, type="dot")
            ])
        ],className="plot1 container-fluid")
