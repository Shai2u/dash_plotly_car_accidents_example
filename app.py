from dash import Dash, html, dcc, callback, Output, Input
from dash_extensions.javascript import assign
import dash_leaflet as dl
import geopandas as gpd
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

# Convert DataFrame to GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat))
gdf['active_col'] = 'HUMRAT_TEUNA'
points_geojson = gdf.__geo_interface__
# JavaScript function to assign tooltip to each feature
def assign_on_each_feature():
    """
    Creates a JavaScript function to bind a tooltip to each feature in a map layer.

    The tooltip displays the `HODESH_TEUNA` property and the value of the property
    specified by `active_col` for each feature.

    Returns
    -------
    on_each_feature : str
        A string containing the JavaScript function to be used for binding tooltips.
    """
    on_each_feature = assign("""function(feature, layer, context){
        layer.bindTooltip(`${feature.properties.HODESH_TEUNA} (${feature.properties[feature.properties.active_col]})`)
    }""")
    return on_each_feature

# JavaScript function to assign point to layer with specific color
def assign_point_to_layer():
    """
    Creates a JavaScript function to assign a point to a layer with a specific color.

    The function uses the `active_col` property and the `color_dict` from the context's hideout
    to determine the fill color of the circle marker.

    Returns
    -------
    str
        A string containing the JavaScript function to be used for assigning points to layers.
    """
    point_to_layer = assign("""function(feature, latlng, context){
        const {active_col, circleOptions, color_dict} = context.hideout;
        const active_col_val  = feature.properties[active_col];
        circleOptions.fillColor = color_dict[active_col][active_col_val];
        return L.circleMarker(latlng, circleOptions);  // render a simple circle marker
    }""")
    return point_to_layer

# Hide points that are out of the range in the search clsuter (env_map)
point_to_layer_hide = assign("""function(feature, latlng, context){
    circleOptions = {fillOpacity: 0, stroke: false, radius: 0};
    return L.circleMarker(latlng, circleOptions);  // render a simple circle marker
}""")
# Function to generate bar graph
def graph_generator(df, x_col, color_stack_col, **kwargs):
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
    if 'col_values_color' in kwargs:
        col_values_color_dict = kwargs['col_values_color']
        fig = px.bar(gb_df, x=x_col, y='count', color=color_stack_col,color_discrete_map = col_values_color_dict[color_stack_col], template='plotly_white')
    else:
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
# Initialize color-discrete-map for graphs
col_values_color = {}
for col in columns_for_graph:
    if col != 'HODESH_TEUNA':
        fig = graph_generator(df, x_col='HODESH_TEUNA', color_stack_col=col)
        col_values_color[col] = {item['name']: item['marker']['color'] for item in fig.to_dict()['data']}


fig = graph_generator(df, x_col='HODESH_TEUNA', color_stack_col='HUMRAT_TEUNA', col_values_color=col_values_color)
# Hideout dictionary for map
hide_out_dict = {
    'active_col': 'HUMRAT_TEUNA', 
    'circleOptions': {'fillOpacity': 1, 'stroke': False, 'radius': 3.5},
    'color_dict': col_values_color
}
dah_main_map = dl.Map([
                    dl.TileLayer(
                        url='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'),
                     dl.GeoJSON(
                        id='lines_geojson', data=points_geojson,
                        pointToLayer=assign_point_to_layer(),  # how to draw points
                        onEachFeature=assign_on_each_feature(),  # add (custom) tooltip
                        hideout=hide_out_dict,
                     ),
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
                        url='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'),
                    dl.GeoJSON(id='lines_env_geojson', data=points_geojson, cluster=True, superClusterOptions={'radius': 125}, pointToLayer=point_to_layer_hide),  # hide remaining  points

                    dl.Polygon(positions=[], id='env_map_bb_polygon', color='red', fillOpacity=0)

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

# Function to generate bounding box from bounds
generate_bounds = lambda b: [[b[0][0], b[0][1]], [b[1][0], b[0][1]], [b[1][0], b[1][1]], [b[0][0], b[1][1]]]

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
filter_boudns : list
    The value selected in the filter map view.
map_bounds : list
    The bounds of the main map.
hideout : dict
    The hideout data from the lines_geojson.

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
    Output('lines_geojson', 'data'),
    Output('lines_env_geojson', 'data'),
    Output('lines_geojson', 'hideout'),
    Input('x_axis_dropdown', 'value'),
    Input('color_stack_dropdown', 'value'),
    Input('filter_1_checklist', 'value'),
    Input('filter_2_checklist', 'value'),
    Input('filter_3_checklist', 'value'),
    Input('filter_4_checklist', 'value'),
    Input('filter_5_checklist', 'value'),
    Input('filter_6_checklist', 'value'),
    Input('main_map', 'bounds'),
    Input('lines_geojson', 'hideout'),
)
    
def update_contextual_graph_map(x_axis, color_stack, filter_1_values, filter_2_values, filter_3_values, filter_4_values, filter_5_values, filter_6_values, map_bounds, hideout):
    df_filtered = df.copy()
    filter_q = []
    for i in range(len(non_numerical_labels)):
        filter_col = labels_to_cols[non_numerical_labels[i]]
        filter_values = eval(f'filter_{i+1}_values')
        if i == 0:
            filter_q = df_filtered[filter_col].isin(filter_values).values
        else:
            filter_q = filter_q & df_filtered[filter_col].isin(filter_values).values
    df_filtered = df_filtered[filter_q]
    gdf_copy = gdf.loc[gdf['pk_teuna_fikt'].isin(df_filtered['pk_teuna_fikt'])].copy()
    gdf_copy['active_col'] = labels_to_cols[color_stack]
    points_geojson = gdf_copy.__geo_interface__
    hideout['active_col'] = labels_to_cols[color_stack]
    if x_axis != color_stack:
        fig = graph_generator(df_filtered, x_col=labels_to_cols[x_axis], color_stack_col=labels_to_cols[color_stack], col_values_color = col_values_color)
    else:
        fig = empty_graph()
    return fig, points_geojson, points_geojson, hideout


"""
Updates the positions of the bounding box polygon on the environmental map.

Parameters
----------
bounds : list of list of float
    The bounds of the main map in the format [[southwest_lat, southwest_lng], [northeast_lat, northeast_lng]].

Returns
-------
list of list of float
    The positions of the bounding box polygon in the format [[lat1, lng1], [lat2, lng2], [lat3, lng3], [lat4, lng4]].
    If bounds is None, returns an empty list.
"""
@app.callback(
    Output('env_map_bb_polygon', 'positions'),
     Input('main_map', 'bounds')
)
def update_env_map_center(bounds ):
    if bounds is None:
        return generate_bounds([[31.857, 34.652], [32.142, 35.148]])
    return generate_bounds(bounds)


if __name__ == "__main__":
    app.run(debug=True)