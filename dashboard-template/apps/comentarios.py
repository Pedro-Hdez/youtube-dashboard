import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import pathlib
from dash.exceptions import PreventUpdate
import pickle
import bz2


from app import app

plotBgColor = 'rgba(35,36,64,255)'
paperBgColor = 'rgba(35,36,64,255)'
bgcolor = "rgba(23,22,46,255)"
subsByDayLineColor = "rgba(131,33,254,255)"
barsColor = "rgba(0,225,135,255)"
pieChartLikesColor = "rgba(1,227,132,255)"
pieChartDislikesColor = "rgba(230,50,66,255)"
positiveCommentsColor = "rgba(1,227,132,255)"
neutralCommentsColor = "rgba(210,212,216,255)"
negativeCommentsColor = "rgba(230,50,66,255)"
cardBodyColor = "rgba(35,36,64,255)"
cardFooterColor = "rgba(35,36,64,255)"
hoverBgColor = "rgba(170,185,193, .8)"
nonActiveButtonColor = {'background-color': 'rgba(57,83,129,255)'}
activeButtonColor = {'background-color': "rgba(49,172,247,255)"}

# Building the path to the datasets
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath(f"../datasets").resolve()
months = {1:"Enero", 2:"Febrero", 3:"Marzo", 4:"Abril", 5:"Mayo", 6:"Junio", 
          7:"Julio", 8:"Agosto", 9:"Septiembre", 10:"Octubre", 11:"Noviembre", 12:"Diciembre"}

plotsFile = bz2.BZ2File(f"{DATA_PATH}/wordClouds.pbz2", 'rb')
wordClouds = pickle.load(plotsFile)

df_comments = pd.read_csv(f"{DATA_PATH}/comments_classified.csv", lineterminator='\n', quotechar='"')
df_comments.publishedAt = pd.to_datetime(df_comments.publishedAt)
df_clean = df_comments[~df_comments.textNormalized.isna()]

df_sentimentByYearAndMonth = df_clean.groupby([df_clean.publishedAt.dt.year, df_clean.publishedAt.dt.month])['prediction'].value_counts().unstack().fillna(0)
df_sentimentByYearAndMonth = df_sentimentByYearAndMonth.reset_index(level=1)
df_sentimentByYearAndMonth.columns = [str(c) for c in df_sentimentByYearAndMonth.columns]
df_sentimentByYearAndMonth.rename(columns={'publishedAt':'Mes', '-1':'Comentarios negativos', '0':'Comentarios neutrales', '1':'Comentarios positivos'}, inplace=True)
df_sentimentByYearAndMonth.reset_index(inplace=True)
df_sentimentByYearAndMonth.rename(columns={'publishedAt':'year'}, inplace=True)
df_sentimentByYearAndMonth.Mes = df_sentimentByYearAndMonth.Mes.map(months)

slider_word_clouds = dcc.Slider(
    id="slider-nube",
    min = 10,
    max = 100,
    value = 10,
    marks={str(n): str(n) for n in range(10,110,10)},
    step=None,
    updatemode='drag'
)

word_cloud_buttons = dbc.ButtonGroup(
    [
        dbc.Button("Todas", id="todas"),
        dbc.Button("Positivas", id="positivas"),
        dbc.Button("Neutras", id="neutras"),
        dbc.Button("Negativas", id="negativas"),
    ]
)

slider_line_plots = dcc.Slider(
    id="slider-lineas",
    min = df_clean.publishedAt.dt.year.min(),
    max = df_clean.publishedAt.dt.year.max(),
    value = df_clean.publishedAt.dt.year.min(),
    marks={str(year): str(year) for year in df_clean.publishedAt.dt.year.unique()},
    step=None,
    updatemode='drag'
)


layout = html.Div([
    dbc.Row([
        dbc.Col([
        ], style={'width':'33%'}),

        dbc.Col([
            html.H4('Nube de palabras más utlizadas', style={'text-align':'center'})
        ], style={'width':'33%'}),

        dbc.Col([
        ], style={'width':'33%'}),
        
    ]),

    dbc.Row([
        dbc.Col([
        ], style={'width':'33%'}),

        dbc.Col([
            word_cloud_buttons,
            slider_word_clouds,
        ], className='text-center'),

        dbc.Col([
        ], style={'width':'33%'}),

    ], className="pt-3"),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='nube-palabras', figure=wordClouds["all"][str(10)], config = {'displayModeBar': False}),
        ])
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='grafica-lineas', config = {'displayModeBar': False}),
            slider_line_plots
        ], style={'padding-right':'3em', 'padding-left':'3em'})
    ])
], style={'background-color':bgcolor})

# this callback uses dash.callback_context to figure out which button
# was clicked most recently. it then updates the "active" style of the
# buttons appropriately, and sets some output. it could be split into
# multiple callbacks if you prefer.
@app.callback(
    [
        Output("todas", "active"),
        Output("positivas", "active"),
        Output("neutras", "active"),
        Output("negativas", "active"),
        Output("todas", "style"),
        Output("positivas", "style"),
        Output("neutras", "style"),
        Output("negativas", "style"),
    ],
    [
        Input("todas", "n_clicks"),
        Input("positivas", "n_clicks"),
        Input("neutras", "n_clicks"),
        Input("negativas", "n_clicks")
        
    ]
)
def toggle_buttons(click_todas, click_pos, click_neu, click_neg):
    ctx = dash.callback_context

    if not ctx.triggered:
        return True, False, False, False, activeButtonColor, nonActiveButtonColor, nonActiveButtonColor, nonActiveButtonColor
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if not any([click_todas, click_pos, click_neu, click_neg]):
        b_todas,b_pos,b_neu,b_neg, col_todas,col_pos,col_neu,col_neg = False, False, False, False, nonActiveButtonColor, nonActiveButtonColor, nonActiveButtonColor, nonActiveButtonColor 
    elif button_id == "todas":
        b_todas,b_pos,b_neu,b_neg, col_todas,col_pos,col_neu,col_neg = True, False, False, False, activeButtonColor, nonActiveButtonColor, nonActiveButtonColor, nonActiveButtonColor
    elif button_id == "positivas":
        b_todas,b_pos,b_neu,b_neg, col_todas,col_pos,col_neu,col_neg = False, True, False, False, nonActiveButtonColor, activeButtonColor, nonActiveButtonColor, nonActiveButtonColor
    elif button_id == "neutras":
        b_todas,b_pos,b_neu,b_neg, col_todas,col_pos,col_neu,col_neg = False, False, True, False, nonActiveButtonColor, nonActiveButtonColor, activeButtonColor, nonActiveButtonColor
    elif button_id == "negativas":
        b_todas,b_pos,b_neu,b_neg, col_todas,col_pos,col_neu,col_neg = False, False, False, True, nonActiveButtonColor, nonActiveButtonColor, nonActiveButtonColor, activeButtonColor
    
    return b_todas,b_pos,b_neu,b_neg, col_todas,col_pos,col_neu,col_neg

@app.callback(
    Output('nube-palabras', 'figure'),
    [
        Input("todas", "n_clicks"),
        Input("positivas", "n_clicks"),
        Input("neutras", "n_clicks"),
        Input("negativas", "n_clicks"),
        Input('slider-nube', 'value')
    ],
    [
        State("todas", "active"),
        State("positivas", "active"),
        State("neutras", "active"),
        State("negativas", "active"),
        State('slider-nube', 'value')
    ]
)
def updateWordCloud(
    btn_todas_input,btn_pos_input,btn_neu_input,btn_neg_input,slider_input,
    btn_todas_state,btn_pos_state,btn_neu_state,btn_neg_state,slider_state,
):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'todas':
        sentiment = 'all'
    elif button_id == 'positivas':
        sentiment = 'positives'
    elif button_id == 'neutras':
        sentiment = 'neutrals'
    elif button_id == 'negativas':
        sentiment = 'negatives'
    else:
        if btn_todas_state:
            sentiment = 'all'
        elif btn_pos_state:
            sentiment = 'positives'
        elif btn_neu_state:
            sentiment = 'neutrals'
        else:
            sentiment = 'negatives'
    
    return wordClouds[sentiment][str(slider_state)]
    

@app.callback(
    Output('grafica-lineas', 'figure'),
    [Input('slider-lineas', 'value')]
    
)
def updateLinePlot(year): 
    df = df_sentimentByYearAndMonth[df_sentimentByYearAndMonth.year == year]
    n_rows = len(df)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df.Mes,
            y=df['Comentarios positivos'],
            text=['Comentarios positivos' for _ in range(n_rows)],
            customdata=[str(x)[:4] for x in 100*(df['Comentarios positivos'] / (df['Comentarios positivos']+df['Comentarios neutrales']+df['Comentarios negativos']))],
            line_color=positiveCommentsColor
            
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.Mes,
            y=df['Comentarios neutrales'],
            text=['Comentarios neutrales' for _ in range(n_rows)],
            customdata=[str(x)[:4] for x in 100*(df['Comentarios neutrales'] / (df['Comentarios positivos']+df['Comentarios neutrales']+df['Comentarios negativos']))],
            line_color=neutralCommentsColor,
            
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.Mes,
            y=df['Comentarios negativos'],
            text=['Comentarios negativos' for _ in range(n_rows)],
            customdata=[str(x)[:4] for x in 100*(df['Comentarios negativos'] / (df['Comentarios positivos']+df['Comentarios neutrales']+df['Comentarios negativos']))],
            line_color=negativeCommentsColor,
            
        )
    )

    hover_template = "<b>%{text}</b><br><br>"+"Número de comentarios: %{y}<br>"+"Porcentaje: %{customdata}%<br>"+"<extra></extra>"

    fig.update_traces(
        hovertemplate=hover_template
    )

    # Editing title
    fig.update_layout(
        title={
            'text': "Comentarios por mes",
            'x':.5,
            'xanchor':'center',
            'yanchor':'top',
            'font_size':18
        },
        xaxis_title="",
        yaxis_title="",
        xaxis={
            'showgrid': False, # thin lines in the background
            'zeroline': False, # thick line at x=0
        },
        # yaxis={
        #     'showgrid': True, # thin lines in the background
        #     'zeroline': False, # thick line at x=0
        #     'visible': True,  # numbers below
        # },
        hoverlabel=dict(
            bgcolor=hoverBgColor,
            font_size=14,
            font_color="black"
        ),
        hovermode="x unified",
        showlegend=False,
        paper_bgcolor=paperBgColor,
        plot_bgcolor=plotBgColor,
        font_color='white'
    )

    fig.update_yaxes(
        gridwidth=0,
        domain=[0.0, 1.0],
        gridcolor='#283442'
    )
    return fig

