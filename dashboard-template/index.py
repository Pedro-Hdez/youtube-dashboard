from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import json
from dash import dcc

# Connect to main app.py file
from app import app
from app import server

from apps import general,videos,comentarios, detalles_tecnicos

with open(f'./datasets/general_data.json') as json_file:
    general_data = json.load(json_file)
    
navBarColor = "rgba(45,45,48,255)"
navBarLinksColor = "white"

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink('General', href="/general", id="link-general", style={'color':navBarLinksColor})),
            dbc.NavItem(dbc.NavLink('Videos', href="/videos", id="link-videos", style={'color':navBarLinksColor})),
            dbc.NavItem(dbc.NavLink('Comentarios', href="/comentarios", id="link-comentarios", style={'color':navBarLinksColor})),
            dbc.NavItem(dbc.NavLink('Detalles técnicos', href="/detalles_tecnicos", id="link-detalles-tecnicos", style={'color':navBarLinksColor}))
        ],
        brand=f"Canal '{general_data['title']}'",
        brand_href="/general",
        color=navBarColor,
        style={'height':'3.8em', 'background-color':navBarColor, 'navbar-brand':'white'},
        id='navbar'
    ),
    html.Div([

    ], id='main-div')
])  

@app.callback(
    [Output('main-div', 'children'),
     Output('link-general', 'children'), Output('link-videos', 'children'),
     Output('link-comentarios', 'children'), Output('link-detalles-tecnicos', 'children')],
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname in ['/', '/general']:
        return [general.layout, dcc.Markdown('''**General**'''), 'Videos', 'Comentarios', 'Detalles técnicos']
    if pathname == "/videos":
        return [videos.layout, 'General', dcc.Markdown('''**Videos**'''), 'Comentarios', 'Detalles técnicos']
    if pathname == '/comentarios':
        return [comentarios.layout, 'General', 'Videos', dcc.Markdown('''**Comentarios**'''), 'Detalles técnicos']
    if pathname == '/detalles_tecnicos':
        return [detalles_tecnicos.layout, 'General', 'Videos', 'Comentarios', dcc.Markdown('''**Detalles técnicos**''')]
    

if __name__ == '__main__':
    app.run_server(debug=False, dev_tools_ui=False, dev_tools_props_check=False)        
