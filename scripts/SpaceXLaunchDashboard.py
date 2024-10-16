# -*- coding: utf-8 -*-

__author__ = "Przemyslaw Marcowski"
__email__ = "p.marcowski@gmail.com"
__license__ = "MIT"

"""
SpaceX Launch Data Dashboard

This module creates a Dash application for visualizing SpaceX launch data.
It provides interactive components to analyze launch success rates, payload
correlations, and site-specific statistics.

Features:
- Interactive dropdown for selecting launch sites
- Pie chart visualization of launch success rates
- Range slider for selecting payload mass
- Scatter plot showing correlation between payload mass and launch success
- Dynamic updates based on user input
"""

import requests
import io
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Fetch data
URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
response = requests.get(URL)
data = io.StringIO(response.text)
df = pd.read_csv(data)

# Rename columns to make them easier to work with
df.rename(columns={'Payload Mass (kg)': 'PayloadMass'}, inplace=True)
max_payload = df['PayloadMass'].max()
min_payload = df['PayloadMass'].min()

# Initialize Dash app
app = dash.Dash(__name__)

# Define app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40, 'fontFamily': 'Segoe UI'}),
    
    # Add dropdown list to enable launch site selection
    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': 'All Sites', 'value': 'ALL'},
                     {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                     {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                     {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                     {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                 ],
                 value='ALL',
                 placeholder="Select a Launch Site here",
                 searchable=True
    ),
    html.Br(),

    # Add pie chart to show total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # Add slider to select payload range
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                    value=[min_payload, max_payload]),

    # Add scatter chart to show correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
], style={'fontFamily': 'Segoe UI'})

# Success rate by launch site
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(df, values='class', names='Launch Site', 
                     title='Total Success Launches By Site')
    else:
        filtered_df = df[df['Launch Site'] == entered_site]
        filtered_df = filtered_df.groupby(['Launch Site', 'class']).size().reset_index(name='class count')
        fig = px.pie(filtered_df, values='class count', names='class', 
                     title=f'Total Success Launches for site {entered_site}')
    fig.update_layout(font_family="Segoe UI")
    return fig

# Payload vs. launch outcome scatter plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), 
     Input(component_id="payload-slider", component_property="value")]
)
def get_scatter_chart(entered_site, payload_range):
    filtered_df = df[(df['PayloadMass'] >= payload_range[0]) & 
                     (df['PayloadMass'] <= payload_range[1])]
    
    if entered_site == 'ALL':
        fig = px.scatter(filtered_df, x='PayloadMass', y='class', 
                         color="Booster Version Category",
                         title='Payload vs. Launch Outcome for All Sites')
    else:
        fig = px.scatter(filtered_df[filtered_df['Launch Site'] == entered_site], 
                         x='PayloadMass', y='class', 
                         color="Booster Version Category",
                         title=f'Payload vs. Launch Outcome for {entered_site}')
    fig.update_layout(font_family="Segoe UI")
    return fig

# Run app
if __name__ == '__main__':
    app.run_server(debug=True)
