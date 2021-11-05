import dash
import dash_bootstrap_components as dbc

external_stylesheets = [dbc.themes.DARKLY]

# meta_tags are required for the app layout to be mobile responsive
app = dash.Dash(__name__, suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'},
                ],
                external_stylesheets = external_stylesheets,
                title="Luisito comunica - Tablero de desempeño"
                )
server = app.server