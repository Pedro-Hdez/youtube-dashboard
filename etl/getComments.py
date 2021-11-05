import datetime
from datetime import date
import pandas as pd
from youtubeApiClient import YoutubeApiClient
import time

keys_file = "keys.txt"

today = date.today()
yesterday = today - datetime.timedelta(days=1)
d = yesterday.strftime("%Y-%m-%d")

data_path = './data/raw_data/'

channels = ['elRubius', 'fedelobo', 'juegaGerman', 'luisitoComunica']
channel_ids = [ 
    'UCXazgXDIYyWH-yXLAkcrFxw', 
    'UCSM3FVwdCIJfU0OdjKZb94A', 
    'UCYiGq8XF7YQD00x7wAd62Zg', 
    'UCECJDeK0MNapZbpaOzxrUPA'
]

for channel, channel_id in zip(channels, channel_ids):
    channel_path = f"{data_path}{channel}"
    ids_path = f"{channel_path}/{channel}_{d}"
    results_path = f"{channel_path}/"
    videos_ids = pd.read_csv(f"{ids_path}/videos_ids.csv")['id'].values
    client = YoutubeApiClient(keys_file, results_path)
    client.getComments(videos_ids)
    client.saveResultsToCsvs(which=['comments'])