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
df2.rename({r'geo\time': 'iso2'}, axis='columns', inplace=True)
df2.iloc[:,5].replace({"UK":"GB","EL":"GR"}, inplace=True)
df2 = df2[df2.iloc[:,5]!="XK"]
df2['ISO3'] = df2.iloc[:,5].map(iso_to_iso)
df2['name'] = df2.iloc[:,5].map(iso_to_name)

data = eurostat.get_data_df('ext_tec03', flags=False)
data.rename({r'geo\time': 'iso2'}, axis='columns', inplace=True)
data['iso2'].replace({"UK":"GB","EL":"GR"}, inplace=True)
data['partner'].replace({"UK":"GB","EL":"GR"}, inplace=True)
data = data[data['iso2']!="XK"]
data['ISO3'] = data['iso2'].map(iso_to_iso)
data['name'] = data['iso2'].map(iso_to_name)
data['ISO3_partner'] = data['partner'].map(iso_to_iso)
data['name_partner'] = data['partner'].map(iso_to_name)
data = data[(data['partner']!="WORLD")&(data['partner']!="EXT_EU")&(data['partner']!="INT_EU")&(data['partner']!="EUR_OTH")&(data['partner']!="INT_EU_NAL")&(data['partner']!="EXT_EU_NAL")]
#Lists-----------------------------------------------------------------------------------------------------------------
Countries=[]
for i in df2.iloc[:,5].unique():
    Countries.append(iso_to_name[i])
#Chart size-----------------------------------------------------------------------------------------------------------------
Width= 1000
Height= 800
#DATA-----------------------------------------------------------------------------------------------------------------

app = dash.Dash(external_stylesheets=[dbc.themes.JOURNAL])

#Tabs Style-----------------------------------------------------------------------------------------------------------------
tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold',
    'font-size': '25px',
    'color':'grey',
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'fontWeight': 'bold',
    'font-size': '25px',
    'color': 'white',
    'padding': '6px'
}
#App layout-----------------------------------------------------------------------------------------------------------------
app.layout = html.Div([ html.Div([
    html.H1("EU Trading Dashboard", style={'text-align':'center'})]),
    html.H4("Data obtained from Eurostat", style={'text-align':'left','color':"#1d00bf"}),
    html.Img(
                    src="https://upload.wikimedia.org/wikipedia/commons/f/f6/Eurostat_Newlogo.png",
                    className='two columns',
                ),
    html.Br(),
dcc.Tabs([
        dcc.Tab(label='EU-country View',style=tab_style, selected_style=tab_selected_style, children=[
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
                    options = [{'label':'Import', 'value':'IMP'},{'label':'Export','value':'EXP'}, {'label':'Revenue','value':'REV'}], 
                    value= 'IMP'),
            html.Br(),
            html.Div(children=[html.Div([  
                            dcc.Graph(id='trading_map', figure={})]),
                            dcc.Graph(id='ranking_chart', figure={})],
                        style={'display': 'flex', 'flex-direction': 'row','align':'center'}),
            html.Br(),
            html.Div([
            html.Pre(children="Main trading target countries", style={"fontSize":"150%"}),
            dcc.Dropdown(id="Country",
                            options=[
                            {"label":x,"value":x} for x in Countries],
                            multi=False,
                            value="Austria",
                            style={'width': '40%'},
                            persistence=True),
            dcc.Dropdown(id="Year2",
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
                            dcc.Graph(id='IMP_chart', figure={}),
                            dcc.Graph(id='EXP_chart', figure={})],
                        style={'display': 'flex', 'flex-direction': 'row','align':'center'})]),
        ]),
        dcc.Tab(label='Trading Product View',style=tab_style, selected_style=tab_selected_style, children=[]),
    ]),
html.Br(),
html.Br(),
html.H2("Authors", style={'text-align':'center'}),
dcc.Markdown('''#### Ignacio Cuervo Torre (@Cuervi) and Daniel Rodriguez gutierrez (@Dannyovi).''',style={'text-align':'center'}),
html.Br(),
])

#Callback-----------------------------------------------------------------------------------------------------------------
@app.callback(
    [Output(component_id='trading_map', component_property='figure'),
    Output(component_id='ranking_chart', component_property='figure'),
    Output(component_id='IMP_chart', component_property='figure'),
    Output(component_id='EXP_chart', component_property='figure')],

    [Input(component_id='Year',component_property='value'),
    Input(component_id='Country',component_property='value'),
    Input(component_id='ImpExp',component_property='value'),
    Input(component_id='Year2',component_property='value')]
)

def update_graph(year_slctd,country_slctd, impexp,year_slctd2):
         
    # choropleth figure----------------------------------------------
    unit = "THS_EUR"
    sizeclas = "TOTAL"
    stk_flow = 'EXP'
    nace_r2 = "TOTAL"
    partner = "WORLD"
    df2_2 = df2[(df2['unit']==unit)&(df2["sizeclas"] ==sizeclas)&(df2['partner'] ==partner)&(df2['nace_r2'] ==nace_r2)]
    if impexp == "REV":
        df2_2.sort_values(by=["iso2","stk_flow"], axis=0, ascending=False, inplace=True)
        df2_2_imp = df2_2[df2_2["stk_flow"]=="IMP"]
        df2_2_exp = df2_2[df2_2["stk_flow"]=="EXP"]
        d3_4 = []
        for i in range(34):
            dict4 = {"unit":"THS_EUR","sizeclas":"TOTAL","stk_flow":"REV","nace_r2":"TOTAL","partner":"WORLD"}
            dict4['iso2'] = df2_2_exp.iloc[i,5]
            dict5  = dict(df2_2_exp.iloc[i,6:15] - df2_2_imp.iloc[i,6:15])
            dict4 = dict4 | dict5
            dict4["ISO3"] = df2_2_exp.iloc[i,15]
            dict4["name"] = df2_2_exp.iloc[i,16]
            d3_4.append(dict4)
        df3_3 = pd.DataFrame.from_dict(d3_4)
        fig_map= px.choropleth(df3_3,
            width=Width,
            height=Height,
            locationmode='ISO-3',
            locations='ISO3',
            title= 'Trading amount (thousand Euro)',
            scope='europe',
            color=year_slctd,
            basemap_visible=True,
            hover_data=['name',year_slctd],
            color_continuous_scale=px.colors.diverging.PRGn,
            color_continuous_midpoint=0,
            #labels={'Name':'Thousands Euro'},
            template='seaborn'
        )
    elif impexp == "EXP":
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
            color_continuous_scale=px.colors.sequential.BuGn,
            #labels={'Name':'Thousands Euro'},
            template='seaborn'
        )
    else:
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
            color_continuous_scale=px.colors.sequential.BuPu,
            #labels={'Name':'Thousands Euro'},
            template='seaborn'
        )

    # Bar figures--------------------------------------------------------
    if impexp == "REV":
        df2_2.sort_values(by=[year_slctd], axis=0, ascending=False, inplace=True)
        df2_2_imp = df2_2[df2_2["stk_flow"]=="IMP"]
        df2_2_exp = df2_2[df2_2["stk_flow"]=="EXP"]
        d3_4 = []
        for i in range(34):
            dict4 = {"unit":"THS_EUR","sizeclas":"TOTAL","stk_flow":"REV","nace_r2":"TOTAL","partner":"WORLD"}
            dict4['iso2'] = df2_2_exp.iloc[i,5]
            dict5  = dict(df2_2_exp.iloc[i,6:15] - df2_2_imp.iloc[i,6:15])
            dict4 = dict4 | dict5
            dict4["ISO3"] = df2_2_exp.iloc[i,15]
            dict4["name"] = df2_2_exp.iloc[i,16]
            d3_4.append(dict4)
        df3_3 = pd.DataFrame.from_dict(d3_4)
        fig2 = px.bar(
        df3_3[df3_3["stk_flow"]==impexp],
        width=Width,
        height=Height,
        x='name', 
        y=year_slctd,
        color=year_slctd,
        labels={year_slctd:'Thousands Euro'}, 
        color_continuous_scale=px.colors.diverging.PRGn,
        color_continuous_midpoint=0,
        title= 'Ranking (thousand Euro)',
        template='plotly_white'
        )

    elif impexp == "EXP":

        df2_2.sort_values(by=[year_slctd], axis=0, ascending=False, inplace=True)
        
        fig2 = px.histogram(
        df2_2[df2_2['stk_flow'] ==impexp],
        width=Width,
        height=Height,
        x='name', 
        y=year_slctd,
        labels={year_slctd:'Thousands Euro'}, 
        color_discrete_sequence=['green'], 
        title= 'Exporting countries',
        template='plotly_white')
    else:
        df2_2.sort_values(by=[year_slctd], axis=0, ascending=False, inplace=True)

        fig2 = px.histogram(
        df2_2[df2_2['stk_flow'] ==impexp], 
        width=Width,
        height=Height,
        x='name', 
        y=year_slctd,
        labels={year_slctd:'Thousands Euro'}, 
        color_discrete_sequence=['purple'], 
        title= 'Importing countries',
        template='plotly_white')
            
    data2=data[data['name']==country_slctd]    
    data2.sort_values(by=[year_slctd2], axis=0, ascending=False, inplace=True)

    fig3 = px.histogram(
    data2[data2["stk_flow"]=='EXP'],
    width=Width,
    height=Height,
    x='name_partner', 
    y=year_slctd2,
    labels={'2012':'exports (Euros)'}, 
    color_discrete_sequence=['green'], 
    title= 'Exporting countries',
    template='plotly_white')

    fig4 = px.histogram(
    data2[data2["stk_flow"]=='IMP'], 
    width=Width,
    height=Height,
    x='name_partner', 
    y=year_slctd2,
    labels={'2012':'imports (Euros)'}, 
    color_discrete_sequence=['purple'], 
    title= 'Importing countries ',
    template='plotly_white')

    return fig_map,fig2,fig3,fig4

#-----------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
