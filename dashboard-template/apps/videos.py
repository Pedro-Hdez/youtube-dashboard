from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import pathlib
import dash_daq as daq
import requests
from io import BytesIO
import PIL

from app import app

# Building the path to the datasets
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath(f"../datasets").resolve()

plotBgColor = 'rgba(35,36,64,255)'
paperBgColor = 'rgba(35,36,64,255)'
bgcolor = "rgba(23,22,46,255)"
subsByDayLineColor = "rgba(131,33,254,255)"
barsColor = "rgba(0,225,135,255)"
indicatorLikesColor = "rgba(1,227,132,255)"
indicatorDislikesColor = "rgba(230,50,66,255)"
positiveCommentsColor = "rgba(1,227,132,255)"
neutralCommentsColor = "rgba(210,212,216,255)"
negativeCommentsColor = "rgba(230,50,66,255)"
switchTextColor = "rgba(49,172,247,255)"
hoverBgColor = "rgba(168,185,195,255)"

months = {1:"Ene", 2:"Feb", 3:"Mar", 4:"Abr", 5:"May", 6:"Jun", 
          7:"Jul", 8:"Ago", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dic"}

def replaceMonthOnDate(date):
    date = str(date).split('-')
    date[1] = months[int(date[1])]
    return '-'.join(date)

# Getting the dataframe with the videos data
df_videos = pd.read_csv(f'{DATA_PATH}/videos.csv')
df_videos.publishedAt = pd.to_datetime(df_videos.publishedAt)
df_videos['stringDate'] = df_videos.publishedAt.dt.strftime('%d-%m-%y').apply(replaceMonthOnDate)

# Getting the dataframe with the classified comments
df_comments = pd.read_csv(f"{DATA_PATH}/comments_classified.csv", lineterminator='\n', quotechar='"')
df_sentiment_count = df_comments.groupby('videoId')['prediction'].value_counts().unstack().fillna(0)
df_sentiment_count.reset_index(inplace=True)
df_sentiment_count.columns = [str(c) for c in df_sentiment_count.columns]
df_sentiment_count.rename(columns={'-1':'n_negative', '0':'n_neutral', '1':'n_positive'}, inplace=True)

# Inner join to get the sentiment count in each of the 
df_videos = pd.merge(df_videos, df_sentiment_count, left_on='id', right_on='videoId')
df_videos['positiveProportion'] = df_videos.n_positive / (df_videos.n_positive+df_videos.n_negative+df_videos.n_neutral)
df_videos['negativeProportion'] = df_videos.n_negative / (df_videos.n_positive+df_videos.n_negative+df_videos.n_neutral)
df_videos['neutralProportion'] = df_videos.n_neutral / (df_videos.n_positive+df_videos.n_negative+df_videos.n_neutral)
df_videos['totalComments'] = df_videos.n_positive+df_videos.n_negative+df_videos.n_neutral

def getImage(link):
    """
        This method gets an image from an url
    """
    img_bytes = BytesIO(requests.get(link).content)
    img = PIL.Image.open(img_bytes)
    return img

def getThumbnails(df_videos):
    """
        This method gets the thumbnails from the videos contained in the 
        'df_videos' dataframe parameter.
    """
    videosThumbnails = []
    for i in range(len(df_videos)):
        videosThumbnails.append((getImage(df_videos.iloc[i, 5]), df_videos.iloc[i, 1]))
    return videosThumbnails

def buildVideosImagesAndTitles(df_videos, kpi):
    """
        This method builds the images videos and its title. 
    """
    # Empty lists to store images and titles
    images_figs = []
    images_titles = []
    # Getting the thumbnails
    videos_thumbnails = getThumbnails(df_videos)
    # Building the images (incluiding the hover) and titles
    for thumbnail, i in zip(videos_thumbnails, range(len(videos_thumbnails))):
        image_fig = px.imshow(thumbnail[0])
        image_fig.update_layout(
            # title={
            #     'text': f"{thumbnail[1]}",
            #     'x':.5,
            #     'xanchor':'center',
            #     'yanchor':'top',
            #     'font_size':18,
            #     'font_color':'white'

            # },
            margin=dict(l=5, r=5, t=5, b=5),
            paper_bgcolor=bgcolor,
            coloraxis_showscale=False
        )
        image_fig.update_xaxes(showticklabels=False)
        image_fig.update_yaxes(showticklabels=False)
        
        date = df_videos.iloc[i, 8]

        if kpi == 'likes':
            view_count = df_videos.iloc[i, 2]
            positive_comments = df_videos.iloc[i,12]
            neutral_comments = df_videos.iloc[i,11]
            negative_comments = df_videos.iloc[i,10]

            positive_proportion = str(df_videos.iloc[i,13]*100)[:4]+'%'
            neutral_proportion = str(df_videos.iloc[i,15]*100)[:4]+'%'
            negative_proportion = str(df_videos.iloc[i,14]*100)[:4]+'%'
            total_comments = df_videos.iloc[i,16]

            image_fig.update_traces(
                hovertemplate=f"Fecha de publicación: {date}<br>Núm. de reproducciones: {view_count:,}<br>Núm. de comentarios positivos: {positive_comments} <b>({positive_proportion})</b><br>Núm. de comentarios neutrales: {neutral_comments} <b>({neutral_proportion})</b><br>Núm. de comentarios negativos {negative_comments} <b>({negative_proportion})</b><br>Tamaño de la muestra de comentarios: {total_comments}<extra></extra>"
            )
        if kpi == 'views':
            likes = df_videos.iloc[i, 3]
            dislikes = df_videos.iloc[i, 4]
            likes_prop = str(df_videos.iloc[i, 7]*100)[:5]+'%'
            dislikes_prop = str(100 - (df_videos.iloc[i, 7]*100))[:5]+'%'

            positive_comments = df_videos.iloc[i,12]
            neutral_comments = df_videos.iloc[i,11]
            negative_comments = df_videos.iloc[i,10]

            positive_proportion = str(df_videos.iloc[i,13]*100)[:4]+'%'
            neutral_proportion = str(df_videos.iloc[i,15]*100)[:4]+'%'
            negative_proportion = str(df_videos.iloc[i,14]*100)[:4]+'%'
            total_comments = df_videos.iloc[i,16]

            image_fig.update_traces(
                hovertemplate=f"Fecha de publicación: {date}<br>Likes: {likes:,} <b>({likes_prop})</b><br>Dislikes: {dislikes:,} <b>({dislikes_prop})</b><br>Total de reacciones: {likes+dislikes:,}<br>Núm. de comentarios positivos: {positive_comments} <b>({positive_proportion})</b><br>Núm. de comentarios neutrales: {neutral_comments} <b>({neutral_proportion})</b><br>Núm. de comentarios negativos {negative_comments} <b>({negative_proportion})</b><br>Tamaño de la muestra de comentarios: {total_comments}<extra></extra>"
            )
        if kpi == 'comments':
            view_count = df_videos.iloc[i, 2]
            likes = df_videos.iloc[i, 3]
            dislikes = df_videos.iloc[i, 4]
            likes_prop = str(df_videos.iloc[i, 7]*100)[:5]+'%'
            dislikes_prop = str(100 - (df_videos.iloc[i, 7]*100))[:5]+'%'
            image_fig.update_traces(
                hovertemplate=f"Fecha de publicación: {date}<br>Likes: {likes:,} <b>({likes_prop})</b><br>Dislikes: {dislikes:,} <b>({dislikes_prop})</b><br>Total de reacciones {likes+dislikes:,}<br>Núm. de reproducciones: {view_count:,}<extra></extra>"
            )
        
        image_fig.update_layout(
            hoverlabel=dict(
                bgcolor=hoverBgColor,
                font_size=14
            ),
        )

        images_figs.append(image_fig)
        images_titles.append(thumbnail[1])
    return images_figs, images_titles

def buildLikesIndicators(df_videos):
    """
    This method builds the likes indicators
    """
    likesIndicators = []
    for i in range(len(df_videos)):
        fig  = go.Figure()
        # Likes bar
        fig.add_trace(go.Bar(
            y = [""],
            x = [df_videos.iloc[i, 3]],
            width=[.2],
            name='likes',
            orientation='h',
            marker={
                'color':indicatorLikesColor,
                'line':{
                    'color':indicatorLikesColor,
                    'width':1
                }
            },
            hovertemplate = "Núm. de likes: %{x:,}<br>"+f"Total de reacciones: {df_videos.iloc[i,3]+df_videos.iloc[i,4]:,}"+"<extra></extra>"
        ))
        # Dislikes bar
        fig.add_trace(go.Bar(
            y = [""],
            x = [df_videos.iloc[i, 4]],
            width=[.2],
            name='dislikes',
            orientation='h',
            marker={
                'color':indicatorDislikesColor,
                'line':{
                    'color':indicatorDislikesColor,
                    'width':1
                }
            },
            hovertemplate = "Núm. de dislikes: %{x:,}<br>"+f"Total de reacciones: {df_videos.iloc[i,3]+df_videos.iloc[i,4]:,}"+"<extra></extra>"
        ))
        fig.update_layout(barmode='stack', 
            showlegend=False, 
            height=200,
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=0
            ),
            yaxis={
                'showgrid': False, # thin lines in the background
                'zeroline': False, # thick line at x=0
                'visible': False,  # numbers below
            },
            xaxis={
                'showgrid': False, # thin lines in the background
                'zeroline': False, # thick line at x=0
                'visible': False,  # numbers below
            },
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title={
                'text': f"Tasa de Likes: {str(df_videos.iloc[i, 7]*100)[:5]}%",
                'x':.5,
                'y':.8,
                'xanchor':'center',
                'yanchor':'top',
                'font_size':18,
                'font_color':'white'

            },
            hoverlabel=dict(
                bgcolor=hoverBgColor,
                font_size=14
            ),
        )
        likesIndicators.append(fig)
    return likesIndicators

def buildViewsIndicators(df_videos):
    """
        This method builds views indicators.
    """
    indicators = []
    for i in range(len(df_videos)):
        indicators.append([f"{df_videos.iloc[i, 2]:,}", html.Br(), "Reproducciones"])
    
    return indicators

def buildCommentsIndicators(df_videos):
    """
    This method builds the comments indicators
    """
    commentsIndicators = []
    for i in range(len(df_videos)):
        positive_proportion = str(df_videos.iloc[i,13]*100)[:4]+'%'
        neutral_proportion = str(df_videos.iloc[i,15]*100)[:4]+'%'
        negative_proportion = str(df_videos.iloc[i,14]*100)[:4]+'%'
        total_comments = df_videos.iloc[i,16]

        fig  = go.Figure()
        # Positive bar
        fig.add_trace(go.Bar(
            y = [""],
            x = [df_videos.iloc[i, 12]],
            width=[.2],
            name='positivos',
            orientation='h',
            marker={
                'color':positiveCommentsColor,
                'line':{
                    'color':positiveCommentsColor,
                    'width':1
                }
            },
            hovertemplate = "Comentarios positivos: %{x}"+f" <b>({positive_proportion})</b><br>"+f"Tamaño de la muestra de comentarios: {total_comments}"+"<extra></extra>"
        ))
        # neutral bar
        fig.add_trace(go.Bar(
            y = [""],
            x = [df_videos.iloc[i, 11]],
            width=[.2],
            name='neutros',
            orientation='h',
            marker={
                'color':neutralCommentsColor,
                'line':{
                    'color':neutralCommentsColor,
                    'width':1
                }
            },
            hovertemplate = "Comentarios neutros: %{x}"+f" <b>({neutral_proportion})</b><br>"+f"Tamaño de la muestra de comentarios: {total_comments}"+"<extra></extra>"
        ))

        # negative bar
        fig.add_trace(go.Bar(
            y = [""],
            x = [df_videos.iloc[i, 10]],
            width=[.2],
            name='negativos',
            orientation='h',
            marker={
                'color':negativeCommentsColor,
                'line':{
                    'color':negativeCommentsColor,
                    'width':1
                }
            },
            hovertemplate = "Comentarios negativos: %{x}"+f" <b>({negative_proportion})</b><br>"+f"Tamaño de la muestra de comentarios: {total_comments}"+"<extra></extra>"
        ))

        fig.update_layout(barmode='stack', 
            showlegend=False, 
            height=200,
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=0
            ),
            yaxis={
                'showgrid': False, # thin lines in the background
                'zeroline': False, # thick line at x=0
                'visible': False,  # numbers below
            },
            xaxis={
                'showgrid': False, # thin lines in the background
                'zeroline': False, # thick line at x=0
                'visible': False,  # numbers below
            },
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title={
                'text': f"Tasa de comentarios positivos: {str(((df_videos.iloc[i, 12])/(df_videos.iloc[i, 12]+df_videos.iloc[i, 11]+df_videos.iloc[i, 10]))*100)[:5]}%",
                'x':.5,
                'y':.8,
                'xanchor':'center',
                'yanchor':'top',
                'font_size':18,
                'font_color':'white'

            },
            hoverlabel=dict(
                bgcolor=hoverBgColor,
                font_size=14
            ),
        )
        commentsIndicators.append(fig)
    return commentsIndicators


dropdown_items = [
    dbc.DropdownMenuItem("Número de reproducciones"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("a"),
]

dropdown = dcc.Dropdown(
    id='dropdown',
    options=[
        {'label': 'Por tasa de likes', 'value': 'likes'},
        {'label': 'Por número de reproducciones', 'value': 'reproducciones'},
        {'label': 'Por tasa de positividad de los comentarios', 'value': 'comentarios'}
    ],
    value='likes',
    clearable=False,
    optionHeight=65,
    searchable=False,
    style={'color':'black', 'width':'100%'}
)

slider = dcc.Slider(
    id="year-slider",
    min = df_videos.publishedAt.dt.year.min(),
    max = df_videos.publishedAt.dt.year.max(),
    value = df_videos.publishedAt.dt.year.min(),
    marks={str(year): str(year) for year in df_videos.publishedAt.dt.year.unique()},
    step=None,
    updatemode='drag'
)

layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H4("Mejores videos", style={"text-align": "right"}, id='mejores-videos-label')
        ]),

        dbc.Col([
            daq.ToggleSwitch(
                id='switch',
                size=60,
                value=False
            ),
        ]),
        dbc.Col([
            html.H4("Peores videos", id='peores-videos-label')
        ]),

    ], className="pt-3"),

    dbc.Row([
        dbc.Col([

        ], style={'width':'40%'}),
        html.Div([
            dropdown,
        ], className='d-flex justify-content-center', style={'width':'20%'}),
        dbc.Col([

        ], style={'width':'40%'}),
        
    ], className="pt-3 align-items-center", style={'padding-bottom':'3em'}),

    dbc.Row([
        dbc.Col([

        ], style={'width':'10%'}),

        html.Div([
            slider,
        ], style={'width':'50%'}),

        dbc.Col([

        ], style={'width':'10%'})
    ]),

    dbc.Row([
        dbc.Col([
            html.H4(id='titulo-1', style={"text-align": "center"}),
        ]),
        dbc.Col([
            html.H4(id='titulo-2', style={"text-align": "center"}),
        ]),
        dbc.Col([
            html.H4(id='titulo-3', style={"text-align": "center"}),
        ]),
    ],style={'padding-top':'5em'}),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='imagen-1', config = {'displayModeBar': False}),
            html.Div([
                dcc.Graph(id='indicador-1', config = {'displayModeBar': False}),
            ], id='div-indicador-1'),
            html.H3(id='indicador-views-1'),
        ], style={'max-width':'33%', 'padding-left':'1.5em'}),
        
        dbc.Col([
            dcc.Graph(id='imagen-2', config = {'displayModeBar': False}),
            html.Div([
                dcc.Graph(id='indicador-2', config = {'displayModeBar': False}),
            ], id='div-indicador-2'),
            html.H3(id='indicador-views-2'),
        ], style={'max-width':'33%'}),
        
        dbc.Col([
            dcc.Graph(id='imagen-3', config = {'displayModeBar': False}),
            html.Div([
                dcc.Graph(id='indicador-3', config = {'displayModeBar': False}),
            ], id='div-indicador-3'),
            html.H3(id='indicador-views-3'),
        ], style={'max-width':'33%', 'padding-right':'1.5em'}),

    ]),
], style={'background-color':bgcolor})

@app.callback(
    [
        Output('mejores-videos-label', 'style'), Output('peores-videos-label', 'style'),
        Output('titulo-1', 'children'), Output('titulo-2', 'children'), Output('titulo-3', 'children'),
        Output('imagen-1', 'figure'), Output('imagen-2', 'figure'), Output('imagen-3', 'figure'),
        Output('indicador-1', 'figure'), Output('indicador-2', 'figure'), Output('indicador-3', 'figure'),
        Output('div-indicador-1', 'style'), Output('div-indicador-2', 'style'), Output('div-indicador-3', 'style'),
        Output('indicador-views-1', 'children'), Output('indicador-views-2', 'children'), Output('indicador-views-3', 'children'),
        Output('indicador-views-1', 'style'), Output('indicador-views-2', 'style'), Output('indicador-views-3', 'style')
    ],
    [Input('switch', 'value'), Input('dropdown', 'value'), Input('year-slider', 'value')],
    
    [State('switch', 'value'), State('dropdown', 'value'), State('year-slider', 'value'),
     State('mejores-videos-label', 'style'), State('peores-videos-label', 'style')]
)
def switchVideos(switch, dropdown, yearslider, switch_val, dropdown_val, yearslider_val,mejores_videos_label_style, peores_videos_label_style):

    df = df_videos[df_videos.publishedAt.dt.year == yearslider_val]

    # MEJORES
    if switch_val == False:
        mejores_videos_label_style = {"text-align": "right", 'color':switchTextColor}
        peores_videos_label_style = {'color':'white'}

        if dropdown_val == 'likes':
            # Getting three best videos from videos dataframe
            best_by_likes = df.nlargest(3, 'likesProportion')
            # Getting images and titles
            images, titles = buildVideosImagesAndTitles(best_by_likes, 'likes')
            title1,title2,title3 = titles
            image1,image2,image3 = images
            # Getting likes indicators
            indicator1,indicator2,indicator3 = buildLikesIndicators(best_by_likes)
            style_div_indicator1,style_div_indicator2,style_div_indicator3 = {},{},{}
            indicator_views1,indicator_views2,indicator_views3 = None, None, None
            style_indicator_views1,style_indicator_views2,style_indicator_views3 = {'display':'none'},{'display':'none'},{'display':'none'}
        elif dropdown_val == 'reproducciones':
            # Getting three best videos from videos dataframe
            best_by_views = df.nlargest(3, 'viewCount')
            # Getting images and titles
            images, titles = buildVideosImagesAndTitles(best_by_views, 'views')
            title1,title2,title3 = titles
            image1,image2,image3 = images
            dummyFig = go.Figure()
            indicator1,indicator2,indicator3 = dummyFig, dummyFig, dummyFig
            style_div_indicator1,style_div_indicator2,style_div_indicator3 = {'display':'none'},{'display':'none'},{'display':'none'}
            # Getting views indicators
            indicator_views1,indicator_views2,indicator_views3 = buildViewsIndicators(best_by_views)
            style_indicator_views1,style_indicator_views2,style_indicator_views3 = {'text-align':'center'}, {'text-align':'center'},{'text-align':'center'}
        else:
            # Getting three best videos from videos dataframe
            best_by_comments = df.nlargest(3, 'positiveProportion')
            # Getting images and titles
            images, titles = buildVideosImagesAndTitles(best_by_comments, 'comments')
            title1,title2,title3 = titles
            image1,image2,image3 = images
            # Getting comments indicator
            indicator1,indicator2,indicator3 = buildCommentsIndicators(best_by_comments)
            style_div_indicator1,style_div_indicator2,style_div_indicator3 = {},{},{}
            indicator_views1,indicator_views2,indicator_views3 = None, None, None
            style_indicator_views1,style_indicator_views2,style_indicator_views3 = {'display':'none'},{'display':'none'},{'display':'none'}
    
    # PEORES
    if switch_val == True:
        mejores_videos_label_style = {"text-align": "right", 'color':'white'}
        peores_videos_label_style = {'color':switchTextColor}
        if dropdown_val == 'likes':
            # Getting three worst videos from videos dataframe
            worst_by_likes = df.nsmallest(3, 'likesProportion')
            # Getting images and titles
            images, titles = buildVideosImagesAndTitles(worst_by_likes, 'likes')
            title1,title2,title3 = titles
            image1,image2,image3 = images
            # Getting dislikes indicators
            indicator1,indicator2,indicator3 = buildLikesIndicators(worst_by_likes)
            style_div_indicator1,style_div_indicator2,style_div_indicator3 = {},{},{}
            indicator_views1,indicator_views2,indicator_views3 = None, None, None
            style_indicator_views1,style_indicator_views2,style_indicator_views3 = {'display':'none'},{'display':'none'},{'display':'none'}
        elif dropdown_val == 'reproducciones':
            # Getting three best videos from videos dataframe
            worst_by_views = df.nsmallest(3, 'viewCount')
            # Getting images and titles
            images, titles = buildVideosImagesAndTitles(worst_by_views, 'views')
            title1,title2,title3 = titles
            image1,image2,image3 = images
            dummyFig = go.Figure()
            indicator1,indicator2,indicator3 = dummyFig, dummyFig, dummyFig
            style_div_indicator1,style_div_indicator2,style_div_indicator3 = {'display':'none'},{'display':'none'},{'display':'none'}
            # Getting inicators
            indicator_views1,indicator_views2,indicator_views3 = buildViewsIndicators(worst_by_views)
            style_indicator_views1,style_indicator_views2,style_indicator_views3 = {'text-align':'center'}, {'text-align':'center'},{'text-align':'center'}
        else:
            # Getting three best videos from videos dataframe
            worst_by_comments = df.nlargest(3, 'negativeProportion')
            # Getting images and titles
            images, titles = buildVideosImagesAndTitles(worst_by_comments, 'comments')
            title1,title2,title3 = titles
            image1,image2,image3 = images
            # Getting indicators
            indicator1,indicator2,indicator3 = buildCommentsIndicators(worst_by_comments)
            style_div_indicator1,style_div_indicator2,style_div_indicator3 = {},{},{}
            indicator_views1,indicator_views2,indicator_views3 = None, None, None
            style_indicator_views1,style_indicator_views2,style_indicator_views3 = {'display':'none'},{'display':'none'},{'display':'none'}
    
    return mejores_videos_label_style,peores_videos_label_style,title1,title2,title3,image1,image2,image3,indicator1,indicator2,indicator3,style_div_indicator1,style_div_indicator2,style_div_indicator3,indicator_views1,indicator_views2,indicator_views3,style_indicator_views1,style_indicator_views2,style_indicator_views3
