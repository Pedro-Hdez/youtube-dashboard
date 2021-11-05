import pandas as pd
import re
from classifier import SentimentClassifier
from spacy.lang.es import Spanish
from spacy.lang.es.stop_words import STOP_WORDS

stopwords = ['el','un','la','una','los','unos','las','unas','a','e','y','o','u']

def remove_emoji(string):
    """
        Esta función elimina todos los emojis de una oración
    """
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

clf = SentimentClassifier()
def getSentiment(text):
    """
        Esta función clasifica un texto de acuerdo a 3 sentimientos:
        Positivo, Neutro y Negativo
    """
    val = clf.predict(text)
    if val <.4:
        sentiment = -1
    elif val < .6:
        sentiment = 0
    else:
        sentiment = 1
    return sentiment


accents = {'á':'a', 'é':'e', 'í':'i', 'ó':'o', 'ú':'u'}
def removeAccents(match):
    return accents[match.group()]

nlp = Spanish()
def normalizeText(t):
    """
        Esta función normaliza un texto
    """
    # removing emojis
    text = remove_emoji(t).strip()
    # to lowercase
    text = text.lower()
    # remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # removin accents (unidecode not using because it removes the 'ñ')
    text = re.sub(r'([áéíóú])', removeAccents, text)
    # Replace long "jaja....", long "looo...l" for "jajaja"
    text = re.sub(r'\b(?:a*(?:ja)+h?|(?:l+o+)+l+)\b', 'jajaja', text)
    # remove duplicate and being/end spaces
    text = " ".join(text.split())
    # Tokenizing
    doc = nlp(text)
    token_list = [t.text for t in doc]
    # Removing stop words
    filtered_sentence = []
    for word in token_list:
        if len(word) == 1:
            continue
        if word not in stopwords:
            filtered_sentence.append(word)


    return " ".join(filtered_sentence)


data_path = './data/raw_data/'
channels = ['elRubius', 'fedelobo', 'juegaGerman', 'luisitoComunica']#badabun
channel_ids = [ 
    'UCXazgXDIYyWH-yXLAkcrFxw', 
    'UCSM3FVwdCIJfU0OdjKZb94A', 
    'UCYiGq8XF7YQD00x7wAd62Zg', 
    'UCECJDeK0MNapZbpaOzxrUPA'
    #'UCYWOjHweP2V-8kGKmmAmQJQ'

]


for channel, channel_id in zip(channels, channel_ids):
    # Se obtiene el path de donde se extraerán los comentarios
    channel_path = f"{data_path}{channel}"
    # Se arma el path en donde se guardarán los resultados
    results_path = f'./data/processed_data/{channel}'
    # Se lee el archivo de comentarios raw y se eliminan los registros que contentan nans
    df = pd.read_csv(f"{channel_path}/comments.csv",lineterminator='\n', quotechar='"')
    df.dropna(inplace=True)
    # Se obtiene la columna del texto normalizado
    df["textNormalized"] = df.textDisplay.apply(lambda comment: normalizeText(comment))
    # Se realiza la predicción del texto normalizado
    df['prediction'] = df['textNormalized'].apply(lambda comment: getSentiment(comment))
    # Se guardan los resultados
    df.to_csv(f'{results_path}/comments_classified.csv', index=False)
    print(f"done {channel}")