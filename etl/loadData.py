import shutil
import os

channels = ['elRubius', 'fedelobo', 'juegaGerman', 'luisitoComunica']
data_path = './data/processed_data'
apps_path = '../heroku_apps'

for channel in channels:
    input_path = f"{data_path}/{channel}/"
    output_path = f"{apps_path}/{channel}/datasets/"
    for file in os.listdir(input_path):
        print(f"{input_path}{file}")
        shutil.copy(f"{input_path}{file}", output_path)


    
