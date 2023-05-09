# -*- coding: utf-8 -*-
"""
Vancouver crime dashboard (using Plotly)

Data source (and columns description): https://www.kaggle.com/datasets/wosaku/crime-in-vancouver
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

df = pd.read_csv('crime.csv')
df['date'] = pd.to_datetime(dict(year=df.YEAR, month=df.MONTH, day=df.DAY)).dt.date

# Create app
app = dash.Dash(__name__, assets_folder='assets')
server = app.server

# Define layout
app.layout = html.Div([
    html.H1('Vancouver crime dashboard'),
    html.H3(
        'Please select the crime (or multiple/all crimes) to see the statistics per year and their location on the map.'),
    html.Div([
        dcc.Dropdown(
            id='type-dropdown',
            options=[{'label': t, 'value': t} for t in ['Select all'] + list(df['TYPE'].unique())],
            value=['Select all'],  # Default to 'Select all'
            multi=True,
            placeholder='Select a type'
        )
    ]),
    html.Div([
        dcc.Graph(id='year-histplot')
    ]),
    html.Div([
        dcc.Graph(id='map')
    ])
])


# Define callbacks
@app.callback(
    [dash.dependencies.Output('year-histplot', 'figure'),
     dash.dependencies.Output('map', 'figure')],
    [dash.dependencies.Input('type-dropdown', 'value')]
)
def update_graphs(selected_types):
    if 'Select all' in selected_types:
        # Include all values of the 'type' column in the filter
        filtered_df = df
    else:
        # Filter the DataFrame by the selected values of the 'type' column
        filtered_df = df[df['TYPE'].isin(selected_types)]

    # Create the histogram figure
    year_histplot = px.histogram(filtered_df, x='YEAR', nbins=len(df.YEAR.unique()))
    year_histplot.update_layout(
        title='Number of crimes per year',
        xaxis_title_text='Year',
        plot_bgcolor="white",
        bargap=0.05,
        xaxis=dict(
            tickmode='linear'
        )
    )

    # Create the map figure
    map_fig = px.scatter_mapbox(filtered_df,
                                lat='Latitude',
                                lon='Longitude',
                                color='TYPE',
                                text=df['date'])
    map_fig.update_layout(mapbox_style='open-street-map')
    map_fig.update_layout(
        mapbox={
            'center': {'lat': 49.246292, 'lon': -123.116226},
            'zoom': 10
        },
    )

    return year_histplot, map_fig


# Run app
if __name__ == '__main__':
    app.run_server(debug=True)
