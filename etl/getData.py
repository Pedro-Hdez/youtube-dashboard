import datetime
from datetime import date
from youtubeApiClient import YoutubeApiClient

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
    results_path = f"{data_path}{channel}/{channel}_{d}"
    client = YoutubeApiClient(keys_file, results_path)

    client.getChannelStats(channel_id)

    client.getAllVideosIds(client.channel_stats['mainPlaylistId'])

    client.getVideosStats(client.videos_ids)

    client.saveResultsToCsvs(which=['channel_stats', 'videos_ids', 'videos_stats'])





