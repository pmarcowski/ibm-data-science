# -*- coding: utf-8 -*-

__author__ = "Przemyslaw Marcowski"
__email__ = "p.marcowski@gmail.com"
__license__ = "MIT"

"""
Automobile Sales Dashboard

This module creates a Dash application for visualizing automobile sales data.
It provides functionalities to display yearly statistics and recession period
statistics for various metrics such as sales, average vehicle price, unemployment
rate, and GDP.

Features:
- Interactive dropdown for selecting report types (yearly or recession period)
- Dynamic year selection for yearly statistics
- Visualizations for automobile sales trends
- Analysis of vehicle types and their sales performance
- Advertising expenditure insights
- Impact of economic indicators on sales
"""

import requests
import io
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Fetch data
URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv"
response = requests.get(URL)
data = io.StringIO(response.text)
df = pd.read_csv(data)

# Filter years between 1980 and 2013
df = df[(df['Year'] >= 1980) & (df['Year'] <= 2013)]

# Initialize Dash app
app = dash.Dash(__name__)

# Get list of years for year dropdown
year_options = [{'label': str(year), 'value': year} for year in sorted(df['Year'].unique())]

# Define app layout
app.layout = html.Div([
    # Add title to dashboard
    html.H1("Automobile Sales Dashboard",
            style={'textAlign': 'center', 'fontFamily': 'Segoe UI', 'marginBottom': '30px'}),

    # Add dropdowns in centered container
    html.Div([
        html.Div([
            # Dropdown for selecting report type
            dcc.Dropdown(
                id='report-type',
                options=[
                    {'label': 'Yearly Statistics', 'value': 'yearly'},
                    {'label': 'Recession Period Statistics', 'value': 'recession'}
                ],
                value='yearly',
                style={'width': '100%', 'marginBottom': '10px'}
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            # Dropdown for selecting year (enabled/disabled based on report type)
            dcc.Dropdown(
                id='year-dropdown',
                options=year_options,
                value=1980,
                style={'width': '100%'},
                disabled=False
            ),
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
    ], style={'width': '80%', 'margin': 'auto', 'marginBottom': '30px'}),

    # Add division for output display
    html.Div(id='output-container', className='output-container',
             style={'width': '80%', 'margin': 'auto'})
], style={'fontFamily': 'Segoe UI', 'padding': '20px'})

# Callback to enable/disable year dropdown based on report type
@app.callback(
    Output('year-dropdown', 'disabled'),
    [Input('report-type', 'value')]
)
def update_year_dropdown(report_type):
    """
    Enable or disable the year dropdown based on the selected report type.
    """
    if report_type == 'yearly':
        return False  # Enable year dropdown
    else:
        return True   # Disable year dropdown

# Callback to update graphs based on selected report type and year
@app.callback(
    Output('output-container', 'children'),
    [Input('report-type', 'value'),
     Input('year-dropdown', 'value')]
)
def update_output(report_type, selected_year):
    """
    Generate and display graphs based on the selected report type and year.
    The graphs are displayed in a 2x2 grid layout.
    """
    if report_type == 'yearly':
        # Yearly statistics
        # 1. Yearly automobile sales for whole period
        yearly_sales = df.groupby('Year')['Automobile_Sales'].mean().reset_index()
        fig1 = px.line(yearly_sales, x='Year', y='Automobile_Sales',
                       title='Average Automobile Sales per Year (1980-2013)')

        # 2. Total monthly automobile sales
        monthly_sales = df[df['Year'] == selected_year].groupby('Month')['Automobile_Sales'].sum().reset_index()
        fig2 = px.line(monthly_sales, x='Month', y='Automobile_Sales',
                       title=f'Total Monthly Automobile Sales in {selected_year}')

        # 3. Average vehicles sold by vehicle type in selected year
        avg_sales_by_type = df[df['Year'] == selected_year].groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        fig3 = px.bar(avg_sales_by_type, x='Vehicle_Type', y='Automobile_Sales',
                      title=f'Average Vehicles Sold by Vehicle Type in {selected_year}')

        # 4. Total advertisement expenditure for each vehicle
        ad_exp_by_type = df[df['Year'] == selected_year].groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        fig4 = px.pie(ad_exp_by_type, names='Vehicle_Type', values='Advertising_Expenditure',
                      title=f'Total Advertising Expenditure by Vehicle Type in {selected_year}')
    else:
        # Recession period statistics
        recession_df = df[df['Recession'] == 1]

        # 1. Average automobile sales fluctuation over recession period
        recession_sales = recession_df.groupby('Year')['Automobile_Sales'].mean().reset_index()
        fig1 = px.line(recession_sales, x='Year', y='Automobile_Sales',
                       title='Average Automobile Sales During Recession Periods')

        # 2. Average number of vehicles sold by vehicle type
        avg_sales_by_type = recession_df.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        fig2 = px.bar(avg_sales_by_type, x='Vehicle_Type', y='Automobile_Sales',
                      title='Average Vehicles Sold by Vehicle Type During Recessions')

        # 3. Total expenditure share by vehicle type during recessions
        ad_exp_by_type = recession_df.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        fig3 = px.pie(ad_exp_by_type, names='Vehicle_Type', values='Advertising_Expenditure',
                      title='Advertising Expenditure Share by Vehicle Type During Recessions')

        # 4. Effect of unemployment rate on vehicle type and sales
        avg_unemp_sales = recession_df.groupby('Vehicle_Type').agg(
            {'unemployment_rate': 'mean', 'Automobile_Sales': 'mean'}).reset_index()
        fig4 = px.bar(avg_unemp_sales, x='Vehicle_Type', y=['Automobile_Sales', 'unemployment_rate'],
                      barmode='group',
                      title='Effect of Unemployment Rate on Vehicle Sales During Recessions')

    # Update layout for consistent styling
    for fig in [fig1, fig2, fig3, fig4]:
        fig.update_layout(
            font_family="Segoe UI",
            title_font_size=20,
            xaxis_title_font_size=14,
            yaxis_title_font_size=14,
            title_x=0.5
        )

    # Arrange graphs in 2x2 grid
    graph_layout = html.Div([
        html.Div([
            dcc.Graph(figure=fig1)
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(figure=fig2)
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(figure=fig3)
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(figure=fig4)
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
    ])

    return graph_layout

# Run app
if __name__ == '__main__':
    app.run_server(debug=True)
