import plotly.express as px
import pandas as pd
from wordcloud import WordCloud
import _pickle as cPickle
import bz2

plotBgColor = 'rgba(35,36,64,255)'
imageBgcolor = "rgba(23,22,46,255)"

def createWordCloudFig(num_words, text):
    wc = WordCloud(
        width=1920,
        height=540,
        max_words=num_words,
        background_color=plotBgColor
    ).generate(text)

    wordcloud = px.imshow(
        wc.to_array(),
        template='plotly_dark'
    )
    wordcloud.update_xaxes(visible=False)
    wordcloud.update_yaxes(visible=False)
    wordcloud.update_layout(paper_bgcolor=imageBgcolor)

    return wordcloud

def getWordClouds(df):
    word_clouds = {'all':{}, 'positives':{}, 'neutrals':{}, 'negatives':{}}

    all_text = " ".join(comment for comment in df.textNormalized)
    positive_text = " ".join(comment for comment in df[df.prediction == 1].textNormalized)
    neutral_text = " ".join(comment for comment in df[df.prediction == 0].textNormalized)
    negative_text = " ".join(comment for comment in df[df.prediction == -1].textNormalized)

    for i in range(10, 110, 10):
        word_clouds['all'][str(i)] = createWordCloudFig(i, all_text)
        word_clouds['positives'][str(i)] = createWordCloudFig(i, positive_text)
        word_clouds['negatives'][str(i)] = createWordCloudFig(i, negative_text)
        word_clouds['neutrals'][str(i)] = createWordCloudFig(i, neutral_text)
    
    return word_clouds


channels = ['elRubius', 'fedelobo', 'juegaGerman', 'luisitoComunica']

for channel in channels:
    DATA_PATH = f"./data/processed_data/{channel}"
    df_comments = pd.read_csv(f"{DATA_PATH}/comments_classified.csv", lineterminator='\n', quotechar='"')
    df_clean = df_comments[~df_comments.textNormalized.isna()]

    wordClouds = getWordClouds(df_clean)

    with bz2.BZ2File(f'{DATA_PATH}/wordClouds.pbz2', 'w') as f:
        cPickle.dump(wordClouds, f)
    print(f"done {channel}")
