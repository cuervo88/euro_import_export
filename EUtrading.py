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

#DATA-----------------------------------------------------------------------------------------------------------------

app = dash.Dash(external_stylesheets=[dbc.themes.JOURNAL])

# with urllib.request.urlopen("https://ec.europa.eu/eurostat/databrowser/bookmark/7ef1358a-648b-440f-bd2a-2aa8da316abf?lang=en") as url:
# data = json.loads(url.read())


df = pd.read_excel("ext_tec.xlsx")
df.drop(['DATAFLOW','LAST UPDATE','freq','unit','sizeclas','nace_r2','OBS_FLAG'], axis=1, inplace=True)
df.rename(columns={'geo':'Country','TIME_PERIOD':'Year'}, inplace=True)
df =df.groupby(['Country','Year'])[['OBS_VALUE']].sum()
df.reset_index(inplace=True)

ISO3= pd.read_excel('G:\My Drive\Python\ISO conversion.xlsx')

df_map = ISO3.merge(df, left_on="ISO2", right_on="Country", how="outer")
df_map.sort_values(by=['OBS_VALUE'], axis=0, ascending=False, inplace=True)

df_map.to_csv(path_or_buf='df_map.csv',)

#Lists-----------------------------------------------------------------------------------------------------------------
Countries=['GERMANY','FRANCE','NETHERLANDS','ITALY','BELGIUM','SPAIN','SWITZERLAND','POLAND','AUSTRIA','SWEDEN',
'IRELAND','CZECH REPUBLIC','HUNGARY','DENMARK','TURKEY','ROMANIA','SLOVAKIA','FINLAND','PORTUGAL','NORWAY','SLOVENIA',
'BULGARIA','LITHUANIA','CROATIA','LUXEMBOURG','ESTONIA','LATVIA','BOSNIA AND HERZEGOVINA','CYPRUS','MALTA','ICELAND']

#Chart size-----------------------------------------------------------------------------------------------------------------
Width= 1000
Height= 800

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
    Input(component_id='Country',component_property='value')],
)

def update_graph(year_slctd,country_slctd):
        
    dff=df_map.copy()
    dff=dff[dff['Year'] == year_slctd]
    
    dff2=df_map.copy()
    dff2=dff2[dff2['Country'] == country_slctd]
      
    # choropleth figure----------------------------------------------
    fig= px.choropleth(
        data_frame=dff,
        width=Width,
        height=Height,
        locationmode='ISO-3',
        locations='ISO3',
        title= 'Trading amount (thousand Euro)',
        scope='europe',
        color='OBS_VALUE',
        basemap_visible=True,
        hover_data=['NAME','OBS_VALUE'],
        color_continuous_scale=px.colors.sequential.Greens,
        labels={'OBS_VALUE':'Thousands Euro'},
        template='seaborn'
    )

    # Bar figures--------------------------------------------------------
    fig2 = px.histogram(
        dff, 
        width=Width,
        height=Height,
        x='NAME', 
        y='OBS_VALUE',
        labels={'OBS_VALUE':'Thousands Euro'}, 
        color_discrete_sequence=['green'], 
        title= 'Ranking (thousand Euro)',
        template='plotly_white')

    fig3 = px.histogram(
        dff2, 
        width=Width,
        height=Height,
        x='NAME', 
        y='OBS_VALUE',
        labels={'OBS_VALUE':'Thousands Euro'}, 
        color_discrete_sequence=['green'], 
        title= 'Exporting countries',
        template='plotly_white')

    fig4 = px.histogram(
        dff2, 
        width=Width,
        height=Height,
        x='NAME', 
        y='OBS_VALUE',
        labels={'OBS_VALUE':'Thousands Euro'}, 
        color_discrete_sequence=['green'], 
        title= 'Importing countries ',
        template='plotly_white')


    return fig,fig2,fig3,fig4

#-----------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)