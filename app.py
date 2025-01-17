from dash import Dash, html, dcc, callback, Output, Input
import dash_leaflet as dl
import plotly.express as px
import pandas as pd
import os

# Load data
file_dir = os.path.dirname(__file__)

# Processed data from https://data.gov.il/dataset/2023-puf
df = pd.read_csv(os.path.join(file_dir, 'accidents_2023_processed.csv'))


# Process Data
cols_to_labels = {
    'HODESH_TEUNA': 'Month', 'SUG_DEREH': 'Road Type', 'SUG_YOM': 'Day Type',
    'YOM_LAYLA': 'Day or Night', 'YOM_BASHAVUA': 'Day of the week', 'HUMRAT_TEUNA': 'Savirity of Accident', 'PNE_KVISH': 'Road Condition'
}
labels_to_cols = dict(zip(cols_to_labels.values(), cols_to_labels.keys()))
non_numerical_columns = df.select_dtypes(exclude=['number']).columns.tolist()
non_numerical_labels = [cols_to_labels[col] for col in non_numerical_columns]
columns_for_graph = non_numerical_columns.copy()
columns_for_graph.append('HODESH_TEUNA')
labels_for_graph = non_numerical_labels.copy()
labels_for_graph.append('Month')

col_unique_values_dict = {}
labels_unique_values_dict = {}
for col in non_numerical_columns:
    col_unique_values_dict[col] = df[col].unique().tolist()
    labels_unique_values_dict[cols_to_labels[col]
                              ] = col_unique_values_dict[col]
    

monthly_accidents = df.groupby(
    ['HODESH_TEUNA', 'HUMRAT_TEUNA']).size().reset_index(name='count')

# Function to generate bar graph
def graph_generator(df, x_col, color_stack_col):
    """
    Generates a bar graph using Plotly based on the provided DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame containing the data to be plotted.
    x_col : str
        The column name in the DataFrame to be used for the x-axis.
    color_stack_col : str
        The column name in the DataFrame to be used for stacking colors in the bar graph.

    Returns
    -------
    plotly.graph_objs._figure.Figure
        A Plotly Figure object representing the generated bar graph.

    Notes
    -----
    - The function groups the DataFrame by `x_col` and `color_stack_col` and counts the occurrences.
    - The x-axis and y-axis titles are updated based on the `cols_to_labels` dictionary.
    - The legend title is also updated based on the `cols_to_labels` dictionary.
    - The layout of the figure is customized to have no margins and a fixed height of 400.
    """
    gb_df = df.groupby([x_col, color_stack_col]).size().reset_index(name='count')
    fig = px.bar(gb_df, x=x_col, y='count', color=color_stack_col, template='plotly_white')
    fig.update_layout(xaxis={'tickmode': 'linear'}, margin={'l': 0, 'r': 0, 't': 25, 'b': 25}, height=400)
    fig.update_xaxes(title_text=cols_to_labels[x_col])
    fig.update_yaxes(title_text='Number of Accidents')
    fig.update_layout(legend_title_text=cols_to_labels[color_stack_col])
    return fig


# Function to generate an empty graph with a message
def empty_graph():
    """
    Create an empty scatter plot with an annotation.

    This function generates an empty scatter plot using Plotly Express and adds an annotation
    in the center of the plot indicating that a graph cannot be produced. The plot has no visible
    axes and a transparent background.

    Returns
    -------
    plotly.graph_objs._figure.Figure
        A Plotly Figure object representing the empty scatter plot with the annotation.
    """
    fig = px.scatter()
    fig.add_annotation(
        text="Cannot produce a graph",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font={'size': 20, 'color': "red"}
    )
    fig.update_layout(
        xaxis={'visible': False},
        yaxis={'visible': False},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin={'l': 0, 'r': 0, 't': 40, 'b': 0},
        height=300
    )
    return fig
fig = graph_generator(df, x_col='HODESH_TEUNA', color_stack_col='HUMRAT_TEUNA')

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

# Populate filter divs
list_filter_divs = []
for i, title in enumerate(non_numerical_labels):
    new_filter_div = html.Div([
        html.B(title),
        dcc.Checklist(labels_unique_values_dict[title], labels_unique_values_dict[title], id=f'filter_{i+1}_checklist')
    ])
    list_filter_divs.append(new_filter_div)
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
            list_filter_divs,
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
                            dcc.Dropdown(labels_for_graph,labels_for_graph[-1], id='x_axis_dropdown'),
                            style={'flex': '1', 'textAlign': 'left'}
                        ),
                        html.Div(
                            dcc.Dropdown(labels_for_graph, labels_for_graph[-3], id='color_stack_dropdown'),
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



# Callback to update the contextual graph and map based on user inputs
"""
Update the contextual graph and map based on the provided filters and map bounds.

Parameters
----------
x_axis : str
    The value selected in the x-axis dropdown.
color_stack : str
    The value selected in the color stack dropdown.
filter_1_values : list
    The values selected in the first filter checklist.
filter_2_values : list
    The values selected in the second filter checklist.
filter_3_values : list
    The values selected in the third filter checklist.
filter_4_values : list
    The values selected in the fourth filter checklist.
filter_5_values : list
    The values selected in the fifth filter checklist.
filter_6_values : list
    The values selected in the sixth filter checklist.



Returns
-------
fig : plotly.graph_objs._figure.Figure
    The updated figure for the contextual graph.
points_geojson : dict
    The GeoJSON data for the points to be displayed on the map.
points_geojson : dict
    The GeoJSON data for the environmental map.
hideout : dict
    The updated hideout parameters.
"""
@app.callback(
    Output('contextual_graph', 'figure'),
    Input('x_axis_dropdown', 'value'),
    Input('color_stack_dropdown', 'value'),
    Input('filter_1_checklist', 'value'),
    Input('filter_2_checklist', 'value'),
    Input('filter_3_checklist', 'value'),
    Input('filter_4_checklist', 'value'),
    Input('filter_5_checklist', 'value'),
    Input('filter_6_checklist', 'value'),
)
    
def update_contextual_graph_map(x_axis, color_stack, filter_1_values, filter_2_values, filter_3_values, filter_4_values, filter_5_values, filter_6_values):
    df_filtered = df.copy()
    filter_q = []
    for i, title in enumerate(non_numerical_labels):
        filter_col = labels_to_cols[title]
        filter_values = eval(f'filter_{i+1}_values')
        if i == 0:
            filter_q = df_filtered[filter_col].isin(filter_values).values
        else:
            filter_q = filter_q & df_filtered[filter_col].isin(filter_values).values
    df_filtered = df_filtered[filter_q]
    if x_axis != color_stack:
        fig = graph_generator(df_filtered, x_col=labels_to_cols[x_axis], color_stack_col=labels_to_cols[color_stack])
    else:
        fig = empty_graph()
    return fig


if __name__ == "__main__":
    app.run(debug=True)