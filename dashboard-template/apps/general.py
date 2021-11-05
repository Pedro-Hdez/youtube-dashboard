from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import pathlib
from app import app

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath(f"../datasets").resolve()

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
hoverBgColor = "rgba(168,185,195,255)"
hoverBgColorLikesDislikes = "rgba(168,185,195,255)"

xTicksFontSize = 14
yTicksFontSize = 14
titlesFontSize = 20

# Getting general channel data
with open(f'{DATA_PATH}/general_data.json') as json_file:
    general_data = json.load(json_file)

# Loading dataframes
df_views_by_day = pd.read_csv(f'{DATA_PATH}/views_by_day.csv')
df_subs_by_day = pd.read_csv(f'{DATA_PATH}/subs_by_day.csv')
df_videos = pd.read_csv(f'{DATA_PATH}/videos.csv')

months = {1:"Ene", 2:"Feb", 3:"Mar", 4:"Abr", 5:"May", 6:"Jun", 
          7:"Jul", 8:"Ago", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dic"}

def addMonthToDate(date):
    date = str(date).split('-')
    date[1] = months[int(date[1])]
    return '-'.join(date)



df_views_by_day.date = pd.to_datetime(df_views_by_day.date)
df_views_by_day['stringDate'] = df_views_by_day.date.dt.strftime("%d-%m-%y").apply(addMonthToDate)
df_subs_by_day.date = pd.to_datetime(df_subs_by_day.date)
df_subs_by_day['stringDate'] = df_subs_by_day.date.dt.strftime("%d-%m-%y").apply(addMonthToDate)

df_videos.publishedAt = pd.to_datetime(df_videos.publishedAt)

# Reading df of comments to get sentiment proportions
df_comments = pd.read_csv(f'{DATA_PATH}/comments_classified.csv', lineterminator='\n', quotechar='"', usecols=['prediction'])
n_positive = len(df_comments[df_comments.prediction == 1])
n_neutral = len(df_comments[df_comments.prediction == 0])
n_negative = len(df_comments[df_comments.prediction == -1])
sentiment_total = n_positive+n_neutral+n_negative

positive_proportion = (n_positive/sentiment_total)*100
neutral_proportion =  (n_neutral/sentiment_total)*100
negative_proportion = (n_negative/sentiment_total)*100

# ---------- CARDS ----------
# styles
card_body_style = {"height":"3.5em", 'background-color':cardBodyColor}
card_footer_style = {"height":"3em", 'background-color':cardFooterColor}
cards_columns_style={'width':'100%'}

# Views card
views = dbc.Card([
        dbc.CardBody(
            html.H4(f"{general_data['total_views']:,}", className='card-title text-center'), style=card_body_style
        ),
        dbc.CardFooter([
            html.H5("Reproducciones", className="text-center"),
        ], style=card_footer_style)
    ], style=cards_columns_style
)

# Subs card
subs = dbc.Card([
        dbc.CardBody(
            html.H4(f"{general_data['total_subs']:,}", className='card-title text-center'), style=card_body_style
        ),
        dbc.CardFooter(
            html.H5("Suscriptores", className="text-center"), style=card_footer_style
        )
    ], style=cards_columns_style
)

# Videos count card
videos_count = dbc.Card([
        dbc.CardBody(
            html.H4(f"{general_data['published_videos']:,}", className='card-title text-center'), style=card_body_style
        ),
        dbc.CardFooter(
            html.H5("Videos", className="text-center"), style=card_footer_style
        )
    ], style=cards_columns_style
)

# Channel visits card
visits = dbc.Card([
        dbc.CardBody(
            html.H4(f"{general_data['visits']:,}", className='card-title text-center'), style=card_body_style
        ),
        dbc.CardFooter(
            html.H5("Visitas al canal", className="text-center"), style=card_footer_style
        )
    ], style=cards_columns_style
)


# ---------- SLIDER FOR VIEWS BY DAY PLOT ----------
slider_views = dcc.Slider(
    id="month-slider-videos",
    min = df_views_by_day.date.dt.month.min(),
    max = df_videos.publishedAt.dt.month.max(),
    value = df_views_by_day.date.dt.month.min(),
    marks={str(m): months[m] for m in df_views_by_day.date.dt.month.unique()},
    step=None,
    updatemode='drag'
)

# ---------- SUBS BY DAY PLOT ----------
# Hover data
hover_data_subs = {
    'date':False,
    'newSubs':False,
    'subs':False,
    'Fecha':df_subs_by_day.stringDate,
    'Total de suscriptores':[f"{v:,}" for v in df_subs_by_day.subs.values],
}

# line chart
subs_by_day = px.line(
    df_subs_by_day,
    x="date",
    y="subs",
    markers=True,
    template="plotly_dark",
    hover_data=hover_data_subs,
    color_discrete_sequence=[subsByDayLineColor]
)
# Changing x label type
# subs_by_day.update_xaxes(
#     tickformat="%d-%m-%y", 
# )
# Editing title
subs_by_day.update_layout(
    title={
        'text': "Suscripciones por día",
        'x':.5,
        'xanchor':'center',
        'yanchor':'top',
        'font_size':titlesFontSize
    },
    xaxis_title="",
    yaxis_title="",
    xaxis={
        'showgrid': False, # thin lines in the background
        'zeroline': False, # thick line at x=0
        'visible': False
    },
    yaxis={
        'tickfont':{'size':yTicksFontSize}
    },
    hoverlabel=dict(
        bgcolor=hoverBgColor,
        font_size=14
    ),
    paper_bgcolor=paperBgColor,
    plot_bgcolor=plotBgColor
)

# ---------- VIDEOS BY YEAR AND MONTH PLOT ----------
# grouping data
df_by_year_and_month = df_videos.groupby([df_videos.publishedAt.dt.year, df_videos.publishedAt.dt.month])
# Getting num of videos by month
num_videos_by_month = []
for g in df_by_year_and_month.groups.keys():
    num_videos_by_month.append(len(df_by_year_and_month.get_group(g)))
# Getting the max number of videos by month to set the y axis of the plot so the 
# changes in the number of published videos will be clearer
max_videos_by_month = max(num_videos_by_month)

# ---------- SLIDER FOR VIDEOS BY YEAR AND MONTH PLOT ----------
slider_videos = dcc.Slider(
    id="year-slider-videos",
    min = df_videos.publishedAt.dt.year.min(),
    max = df_videos.publishedAt.dt.year.max(),
    value = df_videos.publishedAt.dt.year.min(),
    marks={str(year): str(year) for year in df_videos.publishedAt.dt.year.unique()},
    step=None,
    updatemode='drag'
)

# ---------- LIKES AND DISLIKES PLOT ----------
# Getting number of likes, dislikes, sum of likes+dislikes and proportion of likes
n_likes = df_videos.likeCount.sum()
n_dislikes = df_videos.dislikeCount.sum()
total = n_likes + n_dislikes
prop_likes = str(100*(n_likes/total))[:5]+"%"
prop_dislikes = str(100*(n_dislikes/total))[:5]+"%"
types=['Likes', 'Dislikes']
# Build a new dataframe with this info
df_likes = pd.DataFrame({'type':types, 'value':[n_likes, n_dislikes], 'proportion':[prop_likes, prop_dislikes]})

# Hover info 
hover_template_likes_dislikes = "<b>%{label} (%{value})</b><br><br>Proporción: %{customdata}<br>Total de reacciones: "+f"{total:,}"

# Donut chart
likes_dislikes_chart = px.pie(
    df_likes,
    values="value", 
    names='type',
    template="plotly_dark",
    color_discrete_sequence=[pieChartLikesColor, pieChartDislikesColor],
    hole=.5,
    custom_data=['proportion'],
    labels={'proportion':"Proporción"},
    opacity=.8
)

likes_dislikes_chart.update_traces(
    textposition="outside",
    textinfo="label",
    hovertemplate=hover_template_likes_dislikes,
    insidetextorientation='auto',
    textfont_size=18
    
)

likes_dislikes_chart.update_layout(
    title={
        'text': "Proporción de likes",
        'x':.5,
        'y':.98,
        'xanchor':'center',
        'yanchor':'top',
        'font_size':titlesFontSize
    },
    showlegend=False,
    paper_bgcolor=paperBgColor,
    plot_bgcolor=plotBgColor,
    hoverlabel=dict(
        bgcolor=hoverBgColorLikesDislikes,
        font_size=14
    ),

)

# ---------- COMMENTS POSITIVITY PLOT ----------
hover_template="<b>%{y} (%{x})</b><br><br>"+f"Tamaño de la muestra de comentarios: {sentiment_total:,}<br>"+"<extra></extra>"

comments_plot = go.Figure(
    go.Bar(
        x=[n_positive, n_neutral, n_negative],
        customdata=[f"{str(positive_proportion)[:5]}%", f"{str(neutral_proportion)[:5]}%", f"{str(negative_proportion)[:6]}%"],
        y=['Comentarios positivos', 'Comentarios neutros', 'Comentarios negativos'],
        orientation='h',
        hovertemplate = hover_template,
        textposition='inside'
    )
)

comments_plot.update_layout(
    title={
        'text': "Sentimientos en los comentarios",
        'x':.5,
        'y':.98,
        'xanchor':'center',
        'yanchor':'top',
        'font_size':titlesFontSize,
        'font_color':'white'
    },
    showlegend=False,
    hoverlabel=dict(
        bgcolor=hoverBgColor,
        font_size=14
    ),
    yaxis={
        'color':'white',
        'tickfont':{'size':yTicksFontSize}
    },
    xaxis={
        'showgrid': False, # thin lines in the background
        'zeroline': False, # thick line at x=0
        'visible': False,  # numbers below
    },
    paper_bgcolor=paperBgColor,
    plot_bgcolor=plotBgColor,
)

comments_plot.update_traces(
    marker_color=[positiveCommentsColor, neutralCommentsColor, negativeCommentsColor], 
    texttemplate = "%{customdata}", 
    textposition = "inside",
    insidetextanchor='middle',
    textfont_size=18
    
)

cols_style={'height':'30em', 'min-width':'50%'}
cols_style_2={'height':'25em', 'min-width':'70%'}
layout = html.Div([
    dbc.Row(
            [
                dbc.Col(views, style={'padding-left':'1.5em'}),
                dbc.Col(subs),
                dbc.Col(videos_count),
                dbc.Col(visits, style={'padding-right':'1.5em'}),
            ], className="pt-2 pl-3 pr-3 mh-30"
        ),

        dbc.Row([
            dbc.Col([
                dcc.Graph(id='views-by-day-plot', style={"height":'27.8em'}),
                slider_views
            ], style={'width':'33%', 'padding-left':'1.5em'}),

            dbc.Col([
                dcc.Graph(figure=subs_by_day, style={"height":'27.8em'})
            ], style={'width':'33%'}),

            dbc.Col([
                dcc.Graph(id="videos-graph", style={"height":'27.8em'}),
                slider_videos,
            ], style={'width':'33%', 'padding-right':'1.5em'}),

        ], className="pt-3 h-25 pl-3 pr-3"
        ),

        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=likes_dislikes_chart, style=cols_style_2)
            ], style={'width':'50%', 'padding-left':'1.5em'}),

            dbc.Col([
                dcc.Graph(figure=comments_plot, style=cols_style_2)
            ], style={'width':'50%', 'padding-right':'1.5em'}),

        ], className="pt-3 h-25 pl-3 pr-3")
], style={'background-color':bgcolor})


@app.callback(
    Output('views-by-day-plot', 'figure'),
    Input('month-slider-videos', 'value'),
    State('month-slider-videos', 'value')
)
def updateViewsByDayPlot(slider_val_input, slider_val_state):
    df = df_views_by_day[df_views_by_day.date.dt.month == int(slider_val_state)]
    # ---------- NEW VIEWS BY DAY PLOT ----------
    # Hover data
    hover_data_views = {
        'date':False,
        'newViews':False,
        'Fecha':df.iloc[1:,:].stringDate,
        'Reproducciones totales':[f"{v:,}" for v in df.iloc[1:,:].views.values],
        'Nuevas reproducciones':[f"{v:,}" for v in df.iloc[1:,:].newViews.values]
    }

    # bar chart
    views_by_day = px.bar(
        df.iloc[1:,:], 
        x="date", 
        y="newViews", 
        template="plotly_dark",
        hover_data=hover_data_views
    )
    # Changing x label type
    views_by_day.update_xaxes(
        tickformat="%d-%m-%y", 
    )
    # Adding title
    views_by_day.update_layout(
        title={
            'text': "Nuevas reproducciones por día",
            'x':.5,
            'xanchor':'center',
            'yanchor':'top',
            'font_size':titlesFontSize
        },
        xaxis_title="",
        xaxis={
            'showgrid': False, # thin lines in the background
            'zeroline': False, # thick line at x=0
            'visible':False
        },
        yaxis_title="",
        yaxis = dict(
            tickfont = dict(size=yTicksFontSize)
        ),
        hoverlabel=dict(
            bgcolor=hoverBgColor,
            font_size=14
        ),
        paper_bgcolor=paperBgColor,
        plot_bgcolor=plotBgColor,
    )
    # Changing bars color
    views_by_day.update_traces(
        marker_color=barsColor
    )

    return views_by_day

"""
    This callback is to update videos graph when the slider is used.
"""
@app.callback(
    Output('videos-graph', 'figure'),
    Input('year-slider-videos', 'value')
)
def update_videos_graph(selected_year):
    df_year = df_videos[df_videos.publishedAt.dt.year == selected_year]
    df_months = df_year.groupby(df_year.publishedAt.dt.month)

    df_months = df_months.size().to_frame()
    df_months.reset_index(inplace=True)
    df_months.columns = ["month", "numVideos"]
    df_months.month = df_months.month.map(months)

    # Hover data
    hover_data_videos = {
        'month':False,
        'numVideos':False,
        'Número de videos':df_months.numVideos
    }

    # bar chart
    videos_by_month = px.bar(
        df_months, 
        x="month", 
        y="numVideos", 
        template="plotly_dark",
        hover_data = hover_data_videos
    )

    # Adding title
    videos_by_month.update_layout(
        title={
            'text': "Número de videos por mes",
            'x':.5,
            'xanchor':'center',
            'yanchor':'top',
            'font_size':titlesFontSize
        },
        xaxis_title="",
        xaxis={
            'showgrid': False, # thin lines in the background
            'zeroline': False, # thick line at x=0
        },
        yaxis_title="",
        yaxis={
            'range':[0, max_videos_by_month],
            'dtick':5,
            'tickfont':{'size':yTicksFontSize}
        },
        hoverlabel=dict(
            bgcolor=hoverBgColor,
            font_size=14
        ),
        paper_bgcolor=paperBgColor,
        plot_bgcolor=plotBgColor,
    )
    # Changing bars color
    videos_by_month.update_traces(
        marker_color=barsColor
    )

    return videos_by_month