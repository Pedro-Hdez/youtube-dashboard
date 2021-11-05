import pandas as pd
import os
import csv
from datetime import datetime
import json
import os

channels = ['elRubius', 'fedelobo', 'juegaGerman', 'luisitoComunica']

for channel in channels:

    input_folder = f"./data/raw_data/{channel}/"
    output_folder = f'./data/processed_data/{channel}/'

    if not os.path.exists(output_folder):
            os.makedirs(output_folder)

    # ----- Sorting the folders of data by date -----
    # Getting the folder with the data for each existent day
    all_days_folders = [d for d in os.listdir(input_folder) if os.path.isdir(f"{input_folder}{d}")]
    # Sort the folders by date in ascending order
    all_days_folders.sort(key=lambda folder:datetime.strptime(folder.split('_')[1], "%Y-%m-%d"))
    # Joining the input folder path to build the complete relative path to each folder
    all_days_folders = [f"{input_folder}{folder}/" for folder in all_days_folders]
    # ----- Getting the newest dir where latest channel stats are -----
    newest_dir = all_days_folders[-1]
    print(newest_dir)

    # ----- Getting latest videos stats -----
    latest_videos_stats = pd.read_csv(f"{newest_dir}/videos_stats.csv")

    # ----- Reading the channel stats csv file into a dictionary -----
    channel_stats_csv_file = open(f"{newest_dir}/channel_stats.csv", "r")
    channel_stats = dict(list(csv.DictReader(channel_stats_csv_file))[0])


    # ----- Getting channel's banner and title -----
    channel_banner_url = channel_stats['banner']
    channel_title = channel_stats['title']

    # ----- Getting upper cards data -----
    n_total_views = latest_videos_stats.viewCount.sum()
    n_subscriptors = channel_stats['numSubs']
    n_published_videos = channel_stats['numVideos']
    n_channel_visits = channel_stats['numVisits']

    # ----- Getting number of new views and new subs by day -----

    # For each folder extract the total views and compute the difference of these with the previous
    # day

    # Empty dicttionary to store the new views
    new_views_by_day = {"date":[], "views":[], "newViews":[]}
    # Empty dicttionary to store the new subs
    new_subs_by_day = {"date":[], 'subs':[], 'newSubs':[]}

    day_1_views = pd.read_csv(f"{all_days_folders[0]}videos_stats.csv", usecols=['viewCount'])
    new_views_by_day['date'].append(all_days_folders[0].split('_')[2][:-1])
    new_views_by_day['views'].append(day_1_views.viewCount.sum())
    new_views_by_day['newViews'].append(None)

    day_1_subs = pd.read_csv(f"{all_days_folders[0]}channel_stats.csv", usecols=['numSubs'])
    new_subs_by_day['date'].append(all_days_folders[0].split('_')[2][:-1])
    new_subs_by_day['subs'].append(day_1_subs.numSubs.values[0])
    new_subs_by_day['newSubs'].append(None)

    for i in range(1, len(all_days_folders)):
        # Getting the current date
        current_date = all_days_folders[i].split('_')[2][:-1]

        # Getting views count for the previous and current day
        previous_day_views = new_views_by_day['views'][i-1]
        current_day_views = pd.read_csv(f"{all_days_folders[i]}videos_stats.csv", usecols=['viewCount'])['viewCount'].sum()

        # Storing the number of views of the current day and the new views in base of the number of 
        # views of the previous day
        new_views_by_day['date'].append(current_date)
        new_views_by_day['views'].append(current_day_views)
        new_views_by_day['newViews'].append(current_day_views - previous_day_views)

        # Getting the subs count for the previous and current day
        previous_day_subs = new_subs_by_day['subs'][i-1]
        current_day_subs = pd.read_csv(f"{all_days_folders[i]}channel_stats.csv", usecols=['numSubs'])['numSubs'].values[0]

        # Storing the number of subs of the current day and the new subs in base of the number of 
        # subs of the previous day
        new_subs_by_day['date'].append(current_date)
        new_subs_by_day['subs'].append(current_day_subs)
        new_subs_by_day['newSubs'].append(current_day_subs - previous_day_subs)

    # ----- Getting total number of likes and dislikes -----
    n_likes = latest_videos_stats.likeCount.sum()
    n_dislikes = latest_videos_stats.dislikeCount.sum()

    latest_videos_stats['likesProportion'] = latest_videos_stats.likeCount / (latest_videos_stats.likeCount + latest_videos_stats.dislikeCount) 

    general_info = {}
    general_info['banner'] = channel_banner_url
    general_info['title'] = channel_title
    general_info['total_views'] = int(float(n_total_views))
    general_info['total_subs'] = int(float(n_subscriptors))
    general_info['published_videos'] = int(float(n_published_videos))
    general_info['visits'] = int(float(n_channel_visits))

    with open(f"{output_folder}general_data.json", 'w') as output_file:
        json.dump(general_info, output_file)

    pd.DataFrame(new_views_by_day).to_csv(f"{output_folder}views_by_day.csv", index=False)
    pd.DataFrame(new_subs_by_day).to_csv(f"{output_folder}subs_by_day.csv", index=False)
    pd.DataFrame(latest_videos_stats).to_csv(f"{output_folder}videos.csv", index=False)


















