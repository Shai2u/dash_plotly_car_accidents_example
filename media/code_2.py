from dash import Dash, html, dcc, callback, Output, Input
import dash_leaflet as dl
import plotly.express as px
import pandas as pd
import os

##### Load data

# get the absolute dir location of the working file
file_dir = os.path.dirname(__file__)


# Processed data from https://data.gov.il/dataset/2023-puf
df = pd.read_csv(os.path.join(file_dir, 'accidents_2023_processed.csv'))

# At this step the dataframe will only be used to generate a static figure that is not yet linked to the other parts of the dashbaord

# Generate monthly accidents counts grouped by accident severity, this will be used in creating the figure in next part 
monthly_accidents = df.groupby(
    ['HODESH_TEUNA', 'HUMRAT_TEUNA']).size().reset_index(name='count')

# Inital plot placeholder for dashbaord, we used the accidents count calculated above
fig = px.bar(monthly_accidents, x='HODESH_TEUNA', y='count', color='HUMRAT_TEUNA',
             title='Number of Accidents per Month', template='plotly_white')
fig.update_layout(xaxis=dict(tickmode='linear'),
                  margin=dict(l=0, r=0, t=25, b=25), height=400)

# Main Map Component
dah_main_map = dl.Map([
                    dl.TileLayer(
                        url='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'),

                    dl.LocateControl(
                        locateOptions={'enableHighAccuracy': True})
                ],
                    center=[32, 34.9],
                    zoom=12,
                    style={'height': '100%'},
                    id='main_map',
                    dragging=True,
                    zoomControl=True,
                    scrollWheelZoom=True,
                    doubleClickZoom=True,
                    boxZoom=True,
                )

# Environmental Map Component
dash_env_map = dl.Map([
                    dl.TileLayer(
                        url='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png')
                ],
                    center=[32, 34.9],
                    zoom=8,
                    style={'height': '100%'},
                    id='env_map',
                    dragging=False,
                    zoomControl=False,
                    scrollWheelZoom=False,
                    doubleClickZoom=False,
                    boxZoom=False,
                )
app = Dash()


cell_style = {'padding': '20px'}
# Set the layout right the first time!
app.layout = html.Div(
    style={
        'display': 'grid',
        'gridTemplateColumns': '33% 33% 33%',
        'gridTemplateRows': '26% 37% 37%',
        'gap': '10px',
        'height': '100vh',
        'width': '100vw'
    },
    children=[
        # Main Title
        html.Div(
            html.H1('Car Accidents in Israel 2023'),
            style={**cell_style}
        ),
        # Filters Section
        html.Div(
            [
                html.Div(
                    [
                        html.B('Filter 1'),
                        dcc.Checklist(
                            ['New York City', 'Montréal', 'San Francisco'],
                            ['Montréal', 'San Francisco']
                        )
                    ]
                ),
                html.Div(
                    [
                        html.B('Filter 2'),
                        dcc.Checklist(
                            ['New York City', 'Montréal', 'San Francisco'],
                            ['Montréal', 'San Francisco']
                        )
                    ]
                ),
                html.Div(
                    [
                        html.B('Filter 3'),
                        dcc.Checklist(
                            ['New York City', 'Montréal', 'San Francisco'],
                            ['Montréal', 'San Francisco']
                        )
                    ]
                ),
                html.Div(
                    [
                        html.B('Filter 4'),
                        dcc.Checklist(
                            ['New York City', 'Montréal', 'San Francisco'],
                            ['Montréal', 'San Francisco']
                        )
                    ]
                ),
                html.Div(
                    [
                        html.B('Filter 5'),
                        dcc.Checklist(
                            ['New York City', 'Montréal', 'San Francisco'],
                            ['Montréal', 'San Francisco']
                        )
                    ]
                ),
                html.Div(
                    [
                        html.B('Filter 6'),
                        dcc.Checklist(
                            ['New York City', 'Montréal', 'San Francisco'],
                            ['Montréal', 'San Francisco']
                        )
                    ]
                ),
            ],
            style={'gridColumn': 'span 2', 'display': 'flex', **cell_style}
        ),
        # Main Map Div
        html.Div(
            dah_main_map,
            style={'gridColumn': 'span 2', 'gridRow': 'span 2'}
        ),
        # Contextual Graph Div
        html.Div(
            [
                dcc.Graph(figure=fig, id='contextual_graph'),
                html.Div(
                    [
                        html.Div(
                            dcc.Dropdown(
                                ['New York City', 'Montréal', 'San Francisco'],
                                'Montréal'
                            ),
                            style={'flex': '1', 'textAlign': 'left'}
                        ),
                        html.Div(
                            dcc.Dropdown(
                                ['New York City', 'Montréal', 'San Francisco'],
                                'Montréal'
                            ),
                            style={'flex': '1', 'textAlign': 'left'}
                        )
                    ],
                    style={'display': 'flex'}
                ),
                dcc.Checklist(['Filter Map-view']),
            ]
        ),
        # Environmental Map Div
        html.Div(dash_env_map)
    ]
)

if __name__ == "__main__":
    app.run(debug=True)