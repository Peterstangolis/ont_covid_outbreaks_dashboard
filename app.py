import numpy as np
import pandas as pd
#import emoji

from datetime import datetime, timedelta

#import seaborn as sns
#import matplotlib.pyplot as plt

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go

##---------------------------------------------------------------##
# Ongoing Outbreaks by Health Unit - ONTARIO

url = "https://data.ontario.ca/dataset/5472ffc1-88e2-48ca-bc9f-4aa249c1298d/resource/36048cc1-3c47-48ff-a49f-8c7840e32cc2/download/ongoing_outbreaks_phu.csv"
df = pd.read_csv(url, parse_dates=True)
df2 = df[df["date"] == max(df["date"])]
df["date"] = pd.to_datetime(df["date"], format = '%Y-%m-%d' )

last_date = max(df["date"]).strftime("%B %d, %Y")

outbreaks_by_healthunit= df2.groupby(["phu_name", "outbreak_group"])["number_ongoing_outbreaks"].sum().reset_index().sort_values(by=["phu_name","number_ongoing_outbreaks"], ascending=True)
o = outbreaks_by_healthunit["outbreak_group"].str.split(" ", 1)
o2 = []
for item in o:
    i = item[1]
    o2.append(i)

outbreaks_by_healthunit["outbreak_group"] = o2
outbreaks_by_healthunit.rename(columns={"number_ongoing_outbreaks" : "Number of Ongoing Outbreaks"}, inplace=True)

health_unit = outbreaks_by_healthunit.phu_name.unique()


###-------------------------------------------------------###
## Dash App

app = dash.Dash(__name__,
                suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport',
                'content': 'width=device-width, initial-scale=1.0'}])
server = app.server

app.title = "ONT COVID-19 Outbreak Dashboard"


app.layout = html.Div([

    html.Div(className="main", children=[

        html.Div(className="graph1", children = [
            html.H1("Current Outbreaks in Ontario Health Units",
                   style = {'border-bottom' : '1px solid #C2B9A5'}),
            html.Label("Select Health Unit to View Outbreaks by Outbreak Group"),
            dcc.Dropdown(
                id="dropdown",
                options=[
                    {"label": x, "value": x} for x in health_unit],
                value = "TORONTO",
                clearable=False,
                #style = {'width': '60%'}
            ),
            dcc.Graph(id="bar-chart"),
                      #figure = fig,
            ], style = {'box-shadow': '5px 5px 5px #DBD1BA', 'border' : '1px solid #DBD1BA',
                       'background-color' : '#F3F1DA'}),


        html.Div(className = "graph2", children =  [
            html.H1("Ongoing Outbreaks in Ontario Groups / Subgroups",
                   style = {'border-bottom' : '1px solid #C2B9A5'}),
            html.Label("Select to view Outbreaks by Group Breakdown"),
            dcc.RadioItems(
                id="radioitem",
                options=[
                    {"label" : "Outbreak Group", "value" : "Outbreak Group"},
                    {"label" : "Outbreak Subgroup", "value" : "Outbreak Subgroup"}],
                value = "Outbreak Group",
                labelStyle = {"display" : "inline-block"}
                         ),
            dcc.Graph(id="hbar-chart",
                      #figure = fig,
                     #style = {'width' : '75%'}
                     )
                ], style = {'box-shadow': '5px 5px 5px #DBD1BA', 'border' : '1px solid #DBD1BA',
                            'background-color' : '#F3F1DA'})
        ]),

    html.Div(className = "foot", children = [
        html.Label(f"Last Update: {last_date}"),
        html.P("Source: Ontario COVID-19 outbreaks data"),
        html.P("https://data.ontario.ca/dataset/ontario-covid-19-outbreaks-data")
        ])

], style={'backgroundColor' : '#CFC5B0', 'color': '#5C584E'})


@app.callback(
    Output("bar-chart", "figure"),
    [Input("dropdown", "value")])
def update_bar_chart(health_unit):
    mask = outbreaks_by_healthunit["phu_name"] == health_unit
    fig = px.bar(outbreaks_by_healthunit[mask], x="outbreak_group", y="Number of Ongoing Outbreaks",
                 color="outbreak_group",
                 #template = 'simple_white',
                 color_discrete_sequence= px.colors.qualitative.Antique,
                 text = 'Number of Ongoing Outbreaks'
#                  {'6 Other/Unknown': 'blue', '1 Congregate Care': 'navyblue', '4 Workplace' : 'lightblue',
#                 '3 Education': 'royalblue', '5 Recreational':'skyblue', '2 Congregate Living': 'skyblue'}
                )
    fig.update_xaxes(title_text = "GROUP",
                     title_font = dict(size= 16, color='#5C584E'))
    fig.update_yaxes(title="NUMBER OF ONGOING<br>OUTBREAKS", showticklabels=False,
                    title_font = dict(size= 16, color='#5C584E'))
    fig.update_layout(plot_bgcolor='#F3F1DA', paper_bgcolor = '#F3F1DA', showlegend=False)

#     fig.update_layout(legend=dict(
#     orientation="h",
#     yanchor="bottom",
#     y=1.02,
#     x=0.5,
#     xanchor="right",
#     title=""
#     ))
    return fig

@app.callback(
    Output("hbar-chart", "figure"),
    [Input("radioitem", "value")])

def update_hbar_chart(group):

    url = "https://data.ontario.ca/dataset/5472ffc1-88e2-48ca-bc9f-4aa249c1298d/resource/66d15cce-bfee-4f91-9e6e-0ea79ec52b3d/download/ongoing_outbreaks.csv"
    df5 = pd.read_csv(url)
    df5 = df5[df5["date"] == max(df5["date"])]
    df5["date"] = pd.to_datetime(df5["date"], format = '%Y-%m-%d')

    if group == "Outbreak Subgroup":
        outbreaks = df5.groupby("outbreak_subgroup")["number_ongoing_outbreaks"].sum().reset_index().sort_values(by="number_ongoing_outbreaks", ascending=False)
        o = outbreaks["outbreak_subgroup"].str.split(" ", 1)
        o2 = []
        for item in o:
            i = item[1]
            o2.append(i)

        outbreaks["Outbreak Subgroup"] = o2
        outbreaks.rename(columns={"number_ongoing_outbreaks" : "Number of Ongoing Outbreaks"}, inplace=True)

        fig = px.bar(outbreaks, y = "Number of Ongoing Outbreaks", x = "Outbreak Subgroup", #orientation = "h",
                     color= group,
                     #template = 'simple_white',
                     color_discrete_sequence= px.colors.qualitative.Antique,
#                      color_discrete_map={
#                             "Education": "rgb(133, 92, 117)",
#                             "Recreational": "rgb(217, 175, 107",
#                             "Congregate Living": "rgb(175, 100, 88)",
#                             "Workplace": "rgb(115, 111, 76)",
#                             "Congregate Care": "rgb(98, 83, 119)"},
                     text = 'Number of Ongoing Outbreaks')
        fig.update_yaxes(title_text ="NUMBER OF ONGOING<br> OUTBREAKS",
                         title_font = dict(size= 16, color='#5C584E'),
                         dtick = 100,
                         showticklabels=True)
        fig.update_xaxes(title_text = "SUBGROUP",
                         title_font = dict(size= 16, color='#5C584E'))
        fig.update_layout(plot_bgcolor='#F3F1DA', paper_bgcolor = '#F3F1DA', showlegend=False)
        return fig

    if group == "Outbreak Group":
        # Group
        outbreaks_group = df5.groupby("outbreak_group")["number_ongoing_outbreaks"].sum().reset_index().sort_values(by="number_ongoing_outbreaks", ascending=False)
        o = outbreaks_group["outbreak_group"].str.split(" ", 1)
        o2 = []
        for item in o:
            i = item[1]
            o2.append(i)

        outbreaks_group["Outbreak Group"] = o2
        outbreaks_group.rename(columns={"number_ongoing_outbreaks" : "Number of Ongoing Outbreaks"}, inplace=True)

        fig = px.bar(outbreaks_group, y = "Number of Ongoing Outbreaks", x = "Outbreak Group", #orientation = "h",
                    color= group,
                    #template = 'simple_white',
                    color_discrete_sequence= px.colors.qualitative.Antique,
#                     color_discrete_map={
#                             "Education": "rgb(133, 92, 117)",
#                             "Recreational": "rgb(217, 175, 107",
#                             "Congregate Living": "rgb(175, 100, 88)",
#                             "Workplace": "rgb(115, 111, 76)",
#                             "Congregate Care": "rgb(98, 83, 119)"},
                    text = 'Number of Ongoing Outbreaks')
        fig.update_yaxes(title_text ="NUMBER OF ONGOING<br>OUTBREAKS",
                         title_font = dict(size= 16, color='#5C584E'),
                         dtick = 200,
                         showticklabels=True,
                        )
        fig.update_xaxes(title_text = "GROUP",
                         title_font = dict(size= 16, color='#5C584E'))
        fig.update_layout(plot_bgcolor='#F3F1DA', paper_bgcolor = '#F3F1DA', showlegend=False)
        return fig



if __name__ == '__main__':
    app.run_server(debug=True)
