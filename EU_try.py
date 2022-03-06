from gc import callbacks
from os import path
from turtle import width
import pandas as pd # primary data structure library
import numpy as np  # scientific computing in Python
import matplotlib.pyplot as plt # scientific graph plotting
from matplotlib.pyplot import figure
import plotly.express as px
import urllib
import json

#Trying without geopandas
import geopandas as gpd
from geopandas import GeoDataFrame

#Dashboard libraries
import dash
from dash import html, dcc, Input, Output
#import  dash_core_components as dcc
#import dash_html_components as html
import dash_bootstrap_components as dbc
import eurostat
nace_dict = json.load(open("nace.json","r"))
iso_to_iso = json.load(open("iso_to_iso.json","r"))
iso_to_name = json.load(open("iso_to_name.json","r"))
df2   =eurostat.get_data_df("ext_tec01", flags=False)
df2.iloc[:,5].replace({"UK":"GB","EL":"GR"}, inplace=True)
df2 = df2[df2.iloc[:,5]!="XK"]
df2['ISO3'] = df2.iloc[:,5].map(iso_to_iso)
df2['name'] = df2.iloc[:,5].map(iso_to_name)
#Lists-----------------------------------------------------------------------------------------------------------------
Countries=[]
for i in df2.iloc[:,5].unique():
    Countries.append(iso_to_name[i])
#Chart size-----------------------------------------------------------------------------------------------------------------
Width= 1000
Height= 800
#DATA-----------------------------------------------------------------------------------------------------------------

app = dash.Dash(external_stylesheets=[dbc.themes.JOURNAL])
#App layout-----------------------------------------------------------------------------------------------------------------
app.layout = html.Div([
    html.H1("EU Trading Dashboard", style={'text-align':'center'}),
    html.Br(),
html.Pre(children="EU trading by year", style={"fontSize":"150%"}),

        dcc.Dropdown(id="Year",
                options=[
                {"label":"2012","value":2012},
                {"label":"2013","value":2013},                
                {"label":"2014","value":2014},
                {"label":"2015","value":2015},
                {"label":"2016","value":2016},                
                {"label":"2017","value":2017},
                {"label":"2018","value":2018},
                {"label":"2019","value":2019},
                {"label":"2020","value":2020}],
                multi=False,
                value=2012,
                style={'width': '40%'}),
        dcc.RadioItems(id="ImpExp",
        options = [{'label':'Import', 'value':'IMP'},{'label':'Export','value':'EXP'}], 
        value= 'IMP'),
html.Br(),
html.Div(children=[  
                dcc.Graph(id='trading_map', figure={}),
                dcc.Graph(id='ranking_chart', figure={})],
            style={'display': 'flex', 'flex-direction': 'row','align':'center'}),
html.Br(),
html.Pre(children="Main trading target countries", style={"fontSize":"150%"}),
 dcc.Dropdown(id="Country",
                options=[
                {"label":x,"value":x} for x in Countries],
                multi=False,
                value=2012,
                style={'width': '40%'}),
html.Br(),
html.Div(children=[  
                dcc.Graph(id='IMP_chart', figure={}),
                dcc.Graph(id='EXP_chart', figure={})],
            style={'display': 'flex', 'flex-direction': 'row','align':'center'}),
    ])

#Callback-----------------------------------------------------------------------------------------------------------------
@app.callback(
    [Output(component_id='trading_map', component_property='figure'),
    Output(component_id='ranking_chart', component_property='figure'),
    Output(component_id='IMP_chart', component_property='figure'),
    Output(component_id='EXP_chart', component_property='figure')],

    [Input(component_id='Year',component_property='value'),
    Input(component_id='Country',component_property='value'),
    Input(component_id='ImpExp',component_property='value')]
)

def update_graph(year_slctd,country_slctd, impexp):
        
#    dff=df_map.copy()
#    dff=dff[dff['Year'] == year_slctd]
#   
#   dff2=df_map.copy()
#   dff2=dff2[dff2['Country'] == country_slctd]
      
    # choropleth figure----------------------------------------------
    unit = "THS_EUR"
    sizeclas = "TOTAL"
    stk_flow = 'EXP'
    nace_r2 = "TOTAL"
    partner = "WORLD"
    df2_2 = df2[(df2['unit']==unit)&(df2["sizeclas"] ==sizeclas)&(df2['partner'] ==partner)&(df2['nace_r2'] ==nace_r2)]
    df2_2.sort_values(by=[year_slctd], axis=0, ascending=False, inplace=True)
    fig_map= px.choropleth(
        data_frame=df2_2[df2_2['stk_flow'] ==impexp],
        width=Width,
        height=Height,
        locationmode='ISO-3',
        locations='ISO3',
        title= 'Trading amount (thousand Euro)',
        scope='europe',
        color=year_slctd,
        basemap_visible=True,
        hover_data=['name',year_slctd],
        color_continuous_scale=px.colors.sequential.Greens,
        #labels={'Name':'Thousands Euro'},
        template='seaborn'
    )

    # Bar figures--------------------------------------------------------
    fig2 = px.histogram(
        df2_2[df2_2['stk_flow'] ==impexp],
        width=Width,
        height=Height,
        x='name', 
        y=year_slctd,
        labels={year_slctd:'Thousands Euro'}, 
        color_discrete_sequence=['green'], 
        title= 'Ranking (thousand Euro)',
        template='plotly_white')

    fig3 = px.histogram(
        df2_2[df2_2['stk_flow'] =='EXP'], 
        width=Width,
        height=Height,
        x='name', 
        y=year_slctd,
        labels={'OBS_VALUE':'Thousands Euro'}, 
        color_discrete_sequence=['green'],
        color_discrete_map = {country_slctd: "red"}, 
        title= 'Exporting countries',
        template='plotly_white')

    fig4 = px.histogram(
        df2_2[df2_2['stk_flow'] =='IMP'], 
        width=Width,
        height=Height,
        x='name', 
        y=year_slctd,
        labels={'OBS_VALUE':'Thousands Euro'}, 
        color_discrete_sequence=['green'], 
        color_discrete_map = {country_slctd: "red"},
        title= 'Importing countries ',
        template='plotly_white')


    return fig_map,fig2,fig3,fig4

#-----------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)


