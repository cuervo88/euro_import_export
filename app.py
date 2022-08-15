import json
from pydoc import classname
import numpy as np
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from matplotlib.pyplot import title
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
#from EU_sunburst import *
import eurostat
import re
import base64
from PIL import Image
#from plot_1_copy import *
#from plot_2 import *
#from plot_3 import *
from plots import *
from plotly.subplots import make_subplots
from dash_extensions.enrich import Dash, ServersideOutput
import time
pyLogo = Image.open("eurostat_logo.png")

external_stylesheets = ['https://use.fontawesome.com/releases/v5.8.1/css/all.css','https://codepen.io/chriddyp/pen/bWLwgP.css','https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css']
app = Dash(__name__, external_stylesheets = external_stylesheets )

app.config.suppress_callback_exceptions = True

# Home
head_site = html.Div([
    html.Div([
        html.Header("Euro-transfer")
        ]),
    html.Div([
        dbc.Nav([
            html.A([
                html.H2("Data obtained from"),
                html.Img(src=pyLogo)
                ],href="https://ec.europa.eu/info/departments/eurostat-european-statistics_en",className="logo"),
            html.A([
                html.I(className="fas fa-bars"),
                html.Ul([
                    html.Li(
                        html.A(
                            ["HOME"],href="#head")
                            ),
                    html.Li([html.A(["ABOUT"],href="#plot1")]),
                    html.Li([html.A(["CONTENT"],href="#plot2")])
                    ])
                ]),
            html.I(className="fas fa-plus-square")
            ]),
        html.Div([
            html.H1("Import and Export in Europe"),
            html.P("A small data analysis from the Import and Export data provided by Eurostat using SQL and Python to make a dashboard."),
            html.A(["See the code on Github", html.Img(src="https://www.muckibu.de/wp-content/uploads/2018/10/Octocat.png",className="git-logo")
            ],href="",className="btn-github"),
            html.A(["Check out other projects"
            ],href="https://cuervo88.github.io/Ignacio_Cuervo/",className="btn-github")
            ],className="text-box")
            
        ],className="header", id="head")
])

#About



end = html.Div([html.H2("Authors", style={'text-align':'center'}),
    dcc.Markdown('''#### Ignacio Cuervo (@cuervo88) and Daniel Rodriguez Gutierrez (@Dannyovi).''',style={'text-align':'center'})],className="container-fluid footer bg-dark")
app.layout = html.Div([head_site,plots,end])

#Callback-----------------------------------------------------------------------------------------------------------------



@app.callback(Output(component_id="trading_map", component_property="figure"), [Input(component_id='Year',component_property='value'), Input(component_id="ImpExp",component_property= "value"),
    Input(component_id='ranking_chart',component_property='selectedData')])
def graph1(year,impexp,select):
    df2_pivot = df2.pivot(index=['ISO3',"name"], columns="flow", values="sum_"+year)
    df2_pivot["REV"] = df2_pivot.iloc[:,1]-df2_pivot.iloc[:,0]
    df2_pivot.reset_index(inplace=True)
    df2_pivot.sort_values(by=[impexp], axis=0, ascending=False, inplace=True)
    a = generate_rgb(impexp,df2_pivot[impexp])
    

    a.reverse()
    fig_map= px.choropleth_mapbox(
        height=Height,
        data_frame=df2_pivot,
        geojson=euro_map,
        locations='ISO3',
        title= 'Trading amount (thousand Euro)',
        center={"lat": 56, "lon": 10},
        zoom=2.8,
        opacity=0.9,
        color=impexp,
        mapbox_style="carto-positron",
        hover_data=['name',impexp],
        color_continuous_scale=a,
    )

    if select is not None:
        click_data = select["points"][0]["pointIndex"]
        fig_map.data[0].update(selectedpoints=[click_data])
    else:
        fig_map.data[0].update(selectedpoints=False)
        
    impexpval = np.around(df2_pivot[impexp].values/1000000)
    customdata  = np.stack((df2_pivot['name'],impexpval), axis=-1)

 
    fig_map.update_traces(hovertemplate='Country: %{customdata[0]} <br>Amount: %{customdata[1]} Million €')
    fig_map.update_layout(hoverlabel=dict(
        bgcolor="black",
        font_size=16,
        font_family="Arial"),autosize=True,paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',title_font_color="black",font_color="black",clickmode='event+select')
    return fig_map 
@app.callback(Output(component_id='ranking_chart', component_property='figure'),
    [Input(component_id='ImpExp',component_property='value'),
    Input(component_id='Year',component_property='value'),
    Input(component_id='trading_map', component_property='selectedData')])
def graph2(impexp, year,click):
    df2_pivot = df2.pivot(index=['ISO3',"name"], columns="flow", values="sum_"+year)
    df2_pivot["REV"] = df2_pivot.iloc[:,1]-df2_pivot.iloc[:,0]
    df2_pivot.reset_index(inplace=True)
    df2_pivot.sort_values(by=[impexp], axis=0, ascending=False, inplace=True)
    df2_pivot["color"] = np.zeros(len(df2_pivot))
    a = generate_rgb(impexp,df2_pivot[impexp])
    fig2 = go.Figure(go.Bar(x=df2_pivot["name"],
                    y=df2_pivot[impexp],
                    marker=dict(color=a),
                    hoverlabel=dict(bgcolor="black",
                    font_size=16,
                    font_family="Arial")
    ))

   

    fig2.update_layout(autosize=True,paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',title_font_color="black", font_color="black",clickmode='event+select',showlegend=False,
    xaxis ={'showgrid': False},yaxis = {'showgrid': False})
    if click is not None:
        click_data = click['points'][0]["customdata"][0]
#        res = re.sub('""','',click_data)
        for c in range(len(fig2["data"][0]["x"])):
            if fig2["data"][0]["x"][c] != click_data:
                tuple1 = list(fig2["data"][0]["marker"]["color"])
                tuple1[c] = 'rgb(255,255,255)'
                fig2["data"][0]["marker"]["color"] = tuple(tuple1)



    return fig2

@app.callback([Output(component_id='imp-pie', component_property='figure'),
Output(component_id='exp-pie', component_property='figure')],
    [Input(component_id='Year',component_property='value'),
    Input(component_id='Country-2',component_property='value')])
def pie_country(year,country):
    df_pie_imp = df[(df["iso2"]==country) &( df["flow"]==1)].sort_values(by="sum"+year,ascending=False)
    df_pie_exp = df[(df["iso2"]==country) &( df["flow"]==2)].sort_values(by="sum"+year,ascending=False)
    df_pie_imp = df_pie_imp.reset_index(drop=True)
    df_pie_exp = df_pie_exp.reset_index(drop=True)
    df_new_imp = df_pie_imp.loc[:4, ["partner_iso2","sum"+year]].copy()
    df_new_exp = df_pie_exp.loc[:4, ["partner_iso2","sum"+year]].copy()
    df_new_imp["partner_iso2"] = df_new_imp["partner_iso2"].map(lambda x: iso_to_name[x])
    df_new_exp["partner_iso2"] = df_new_exp["partner_iso2"].map(lambda x: iso_to_name[x])
    df_new_imp = df_new_imp.append({"partner_iso2":"Other","sum"+year:df_pie_imp["sum"+year][5:].sum()},ignore_index=True)
    df_new_exp = df_new_exp.append({"partner_iso2":"Other","sum"+year:df_pie_exp["sum"+year][5:].sum()},ignore_index=True)
    fig1 = px.pie(df_new_imp, values='sum'+year, names='partner_iso2', title='Countries improting from '+iso_to_name[country]+" in "+year)
    fig2 = px.pie(df_new_exp, values='sum'+year, names='partner_iso2', title='Countries exporting to '+iso_to_name[country]+" in "+year)
    fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',title_font_color="black",font_color="black",clickmode='event+select')
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',title_font_color="black",font_color="black",clickmode='event+select')
    return fig1, fig2

@app.callback(
    Output(component_id='imp-exp-prod', component_property='figure'),
    [Input(component_id='product',component_property='value'),
    Input(component_id='Year',component_property='value')]
)
def table_and_fig(prod1,year):
    df3 = pd.read_csv("data/product_per_country.csv")
    df3 = df3.fillna(0)
    df_pivot = df3[df3["nc_2"]==prod1].pivot_table(columns="flow",index="name",values="sum_"+year)
    df_pivot.reset_index(inplace=True)
    df4 = df3[df3["nc_2"]==prod1]
    df4 = df4.sort_values(by="name")
    df4_pivot = df4.pivot_table(index="name",columns="flow",values="sum_"+year)
    df4_pivot=df4_pivot.reset_index()
    df4_pivot[3] = df4_pivot[2]-df4_pivot[1]
    #fig1 = px.bar(df4[df4["flow"]==1], y="name", x="sum_"+year,orientation='h')
    fig = make_subplots(rows=1, cols=2, specs=[[{}, {}]], shared_xaxes=True,
                        shared_yaxes=True, vertical_spacing=0.1,horizontal_spacing=0.16)
    fig.append_trace(go.Bar(y=df4_pivot["name"], x=df4_pivot[1],orientation="h",name="Import",marker=dict(
            color='rgba(210, 34, 45, 0.6)',
            line=dict(
                color='rgba(210, 34, 45, 1.0)',
                width=1),
        )),1,1)
    fig.append_trace(go.Bar(y=df4_pivot["name"], x=df4_pivot[2],orientation="h",name="Export",marker=dict(
            color='rgba(35, 136, 35, 0.6)',
            line=dict(
                color='rgba(35, 136, 35, 1.0)',
                width=1),
        )),1,2)
    annotations = []
    y_data = list(df4_pivot["name"].values)
    x_data = [df4_pivot[1].values,df4_pivot[2].values]

    for j in range(len(y_data)):
        for i in range(2):
            annotations.append(dict(xref='paper', yref='y',
                            x=0.5, y=y_data[j],
                            xanchor='center',
                            text=str(y_data[j]+ ": "+ str(np.around((x_data[1][j]-x_data[0][j])/1000000)))+"M",
                            font=dict(family='Arial', size=14,
                                      color='rgb(67, 67, 67)'),
                            showarrow=False, align='right'))
            if i == 0:
                annotations.append(dict(xref='x1', yref='y1',
                                x=x_data[i][j]+550000000, y=y_data[j],
                                text=str(np.absolute(np.around(x_data[i][j]/1000000))) + 'M',
                                font=dict(family='Arial', size=14,
                                          color='rgb(210, 34, 45)'),
                                showarrow=False))
            if i == 1:
                annotations.append(dict(xref='x2', yref='y2',
                                x=x_data[i][j]+590000000, y=y_data[j],
                                text=str(np.around(x_data[i][j]/1000000)) + 'M',
                                font=dict(family='Arial', size=14,
                                          color='rgb(35, 136, 35)'),
                                showarrow=False))
    fig.update_layout(title='Import and exports of {} in the EU in {}'.format(prod[prod1].capitalize(),year),
        yaxis=dict(
            autorange="reversed",
            categoryarray=list(df4_pivot.sort_values(by=3,ascending=False)["name"]),
            showgrid=False,
            showline=False,
            showticklabels=True,
            domain=[0, 0.85],
        ),
        yaxis1=dict(
            showgrid=False,
            showline=True,
            showticklabels=False,
            linecolor='rgba(102, 102, 102, 0.8)',
            linewidth=2,
            domain=[0, 0.85],
        ),
        yaxis2=dict(
            showgrid=False,
            showline=True,
            showticklabels=False,
            side="left",
            linecolor='rgba(102, 102, 102, 0.8)',
            linewidth=2,
            domain=[0, 0.85]
        ),xaxis2=dict(domain=[0.6,1]),
        xaxis1=dict(autorange="reversed",domain=[0,0.4]),
        legend=dict(x=0.029, y=1.038, font_size=10),
        margin=dict(l=10, r=20, t=70, b=70),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',annotations=annotations
    )

    return fig 
@app.callback(Output(component_id='imp-exp-perc', component_property='figure'),
    Input(component_id='Year',component_property='value'))
def plot_imp_exp(year):
    year = str(year)
    df_3 = df4[["iso2","partner_iso2","flow","sum_"+year,"ISO3","name"]]
    tot_in_eu_imp = df_3[(df_3["flow"]==1)&(df_3["partner_iso2"].isin(iso_eu))]
    tot_out_eu_imp= df_3[(df_3["flow"]==1)&(~df_3["partner_iso2"].isin(iso_eu))]
    tot_in_eu_exp = df_3[(df_3["flow"]==2)&(df_3["partner_iso2"].isin(iso_eu))]
    tot_out_eu_exp= df_3[(df_3["flow"]==2)&(~df_3["partner_iso2"].isin(iso_eu))]
    eu_imp = tot_in_eu_imp.groupby("name").sum("sum_"+year)
    not_eu_imp = tot_out_eu_imp.groupby("name").sum("sum_"+year)
    eu_exp = tot_in_eu_exp.groupby("name").sum("sum_"+year)
    not_eu_exp = tot_out_eu_exp.groupby("name").sum("sum_"+year)
    eu_imp["out"] = not_eu_imp["sum_"+year]
    eu_exp["out"] = not_eu_exp["sum_"+year]
    eu_imp["perc"] = eu_imp["sum_"+year] / (eu_imp["out"] + eu_imp["sum_"+year])
    eu_exp["perc"] = eu_exp["sum_"+year] / (eu_exp["out"] + eu_exp["sum_"+year])
    fig1 = px.scatter(x=eu_imp["perc"],y=eu_exp["perc"],color=eu_imp.index,trendline="ols",hover_name=eu_imp.index,text=eu_imp.index)
    fig1.update_traces(hovertemplate='Import: %{x} <br>Export: %{y}',textposition='top center',marker=dict(size=12)) 
    fig2 = px.line(x=np.arange(0,1,0.1),y=10*[0.5],line_dash=[1,0,2,0,3,0,4,0,5,0])
    fig3 = px.line(y=np.arange(0,1,0.1),x=10*[0.5],line_dash=[1,0,2,0,3,0,4,0,5,0])
    fig4 = go.Figure(data=fig1.data + fig2.data + fig3.data)

    fig4.update_layout(title="Comparison of import and export percentage between EU countries and other countries",
    xaxis_title="Import EU country vs non-EU contry",
    yaxis_title="Export EU country vs non-EU contry",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    title_font_color="black",
    font_color="black",
    clickmode='event+select')
    return fig4


if __name__ == '__main__':
    app.run_server(debug=True)