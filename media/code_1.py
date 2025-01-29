from dash import Dash, html
import plotly.express as px

app = Dash()


cell_style = {'padding': '20px',
              'text-align': 'center'}

# Set the layout right the first time!
app.layout = html.Div(
    style={
        'display': 'grid',
        'gridTemplateColumns': '33% 33% 33%',
        'gridTemplateRows': '20% 40% 40%',
        'gap': '10px',
        'height': '100vh',
        'width': '100vw',
    },
    children=[
        html.Div('Title', style={
                 'backgroundColor': 'lightblue', **cell_style}),
        html.Div('Filters', style={
                 'backgroundColor': 'lightgreen', 'gridColumn': 'span 2', **cell_style}),
        html.Div('Main Map', style={'backgroundColor': 'lightcoral',
                 **cell_style, 'gridColumn': 'span 2', 'gridRow': 'span 2'}),
        html.Div(['Graph with Filed Selection'], style={
                 'backgroundColor': 'lightgoldenrodyellow', **cell_style}),
        html.Div(['Env Map'], style={
                 'backgroundColor': 'lightpink', **cell_style})
    ]
)
if __name__ == "__main__":
    app.run(debug=True)