from warnings import resetwarnings
import googleapiclient.discovery
import math
import pandas as pd
import os

class YoutubeApiClient():
    def __init__(self, keys_file, results_path="."):
        self.keys = list(map(str.strip, open(keys_file, 'r').readlines()))
        self.current_key = self.keys.pop(0)

        if results_path[-1] == "/":
            results_path = results_path[:-1]
        
        self.results_path = f"{results_path}/"
        if not os.path.exists(self.results_path):
            os.makedirs(self.results_path)

        self.api_service_name = "youtube"
        self.api_version = "v3"

        # All channel stats
        self.channel_stats = {}
        # All videos ids
        self.videos_ids = []
        # All videos stats
        self.videos_stats = []
        # All videos comments
        self.comments = []
        self.vids_to_use = 0

        # client
        self.youtube = googleapiclient.discovery.build(
            self.api_service_name, self.api_version, developerKey = self.current_key
        )
    
    def calculateQuotaUsage(self, channelId):
        self.getChannelStats(channelId)
        
        if self.channel_stats['numVideos'] > 1e4:
            vids_number_exceeded = True
            self.vids_to_use = 1e4
            videos_usage = 400
            comments_usage = 10000
        else:
            vids_number_exceeded = False
            self.vids_to_use = self.channel_stats['numVideos']
            videos_usage = math.ceil((self.channel_stats['numVideos']/50))
            comments_usage = math.ceil(self.channel_stats['numVideos'])
        
        total = (videos_usage*2) + comments_usage + 1
        
        print(f"APROXIMATE QUOTA USAGE FOR '{self.channel_stats['title']}' CHANNEL DATA EXTRACTION\n")
        
        print("TO RETRIEVE THE VIDEOS LIST (A query for each 50 videos costs 1 unit)")
        if vids_number_exceeded:
            print(f"Since the channel has more than 10,0000 videos ({self.channel_stats['numVideos']}) "+
                  f"only the {self.vids_to_use} most recent videos will be used for the analysis. To " +
                  f"retrieve this ammount of videos {videos_usage} units will be spent.\n\n")
        else:
            print(f"{self.vids_to_use} will be retrieved. Thus, {videos_usage} units will be spent\n\n")

        print("TO RETRIEVE EACH VIDEO STATS (A query for each 50 videos stats costs 1 unit)")
        if vids_number_exceeded:
            print(f"Since the channel has more than 10,0000 videos ({self.channel_stats['numVideos']}) "+
                  f"only the {self.vids_to_use} most recent videos will be used for the analysis. To " +
                  f"retrieve stats for all videos {videos_usage} units will be spent.\n\n")
        else:
            print(f"Stats for {self.vids_to_use} will be retrieved. Thus, {videos_usage} units will be "+
                  f"spent\n\n")
        
        print("TO RETRIEVE COMMENTS (A query for each 100 comments costs 1 unit)")
        print("***Important note*** In this case usage is an approximation. It's supposed each " + 
              "video has at least 100 comments. For the analysis the 100 most relevant comments " + 
              "for each video will be used.\n")
        if vids_number_exceeded:
            print(f"Since the channel has more than 10,0000 videos ({self.channel_stats['numVideos']}) "+
                  f"only the 100 most relevant comments for the last {self.vids_to_use} most recent " + 
                  f"videos will be used for the analysis. To " +
                  f"retrieve 100 comments for each video {comments_usage} units will be spent.\n\n")
        else:
            print(f"100 comment for each of the {self.vids_to_use} videos will be retrieved. Thus, "+
                  f"{comments_usage} units will be spent\n\n")

        print("TOTAL AMOUNT OF NEEDED UNITS")
        

        print(f"{total} units will be spent (1 more unit was added because it was used to " + 
              f"extract channel info to compute the quota usage). Since each API " +
              f"key contains 10,000 units per day, to retrieve the information for this analysis " +
              f"{math.ceil(total / 10000)} different keys are needed. To avoid problems, only " + 
              f"provide non-used keys.")
    
    def saveResultsToCsvs(self, which=None, terminate=False):
        print("SAVING RESULTS IN CSV FILES\n")

        print("Channel stats: channel_stats.csv")
        print("Videos ids: videos_ids.csv")
        print("Videos stats: videos_stats.csv")
        print("Comments: comments.csv")

        channel_stats_file = f"{self.results_path}channel_stats.csv"
        videos_ids_file = f"{self.results_path}videos_ids.csv"
        videos_stats_file = f"{self.results_path}videos_stats.csv"
        comments_file = f"{self.results_path}comments.csv"

        if not which:
            pd.DataFrame([self.channel_stats]).to_csv(channel_stats_file, index=False)
            pd.DataFrame(data={'id':self.videos_ids}).to_csv(videos_ids_file, index=False)
            pd.DataFrame(self.videos_stats).to_csv(videos_stats_file, index=False)
            pd.DataFrame(self.comments).to_csv(comments_file, index=False)
        else:
            for w in which:
                if w == "channel_stats":
                    pd.DataFrame([self.channel_stats]).to_csv(channel_stats_file, index=False)
                if w == "videos_ids":
                    pd.DataFrame(data={'id':self.videos_ids}).to_csv(videos_ids_file, index=False)
                if w == "videos_stats":
                    pd.DataFrame(self.videos_stats).to_csv(videos_stats_file, index=False)
                if w == "comments":
                    pd.DataFrame(self.comments).to_csv(comments_file, index=False)
            
        if terminate:
            exit()


    def __informKeyShift(self, method_name, new_key):
        print(f"Key {self.current_key} was completely consumed in a " + 
              f"{method_name} call. Switching to the next key " + 
              f"({new_key}).\n")
    
    def __informNoRemainingKeys(self, method):
        print(f"No remaining keys!. Last key was used in {method} callRetrieved data until now will be stored in csv files.")

        self.saveResultsToCsvs(terminate=True)

    # ---------- Getting channel stats ----------
    def getChannelStats(self, channelId):

        if self.channel_stats:
            return
        # trying to use the client
        try:
            r = self.youtube.channels().list(
                part='snippet, statistics, contentDetails, brandingSettings',
                id=channelId,
                fields='items(snippet(title, defaultLanguage, country),' + 
                    'statistics(viewCount, subscriberCount, videoCount),' + 
                    'contentDetails(relatedPlaylists(uploads)),'+
                    'brandingSettings(image(bannerExternalUrl)))'
            ).execute()
        except:
            # Tellin the user the key was consumed. Switch to a new one and repeat the
            # query with a new client
            try:
                new_key = self.keys.pop(0)
            except:
                self.__informNoRemainingKeys("getChannelStats")

            self.__informKeyShift("getChannelStats", new_key)

            self.current_key = new_key
            self.youtube = googleapiclient.discovery.build(
                self.api_service_name, self.api_version, developerKey = self.current_key
            )

            r = self.youtube.channels().list(
                part='snippet, statistics, contentDetails',
                id=channelId,
                fields='items(snippet(title, defaultLanguage, country),' + 
                    'statistics(viewCount, subscriberCount, videoCount),' + 
                    'contentDetails(relatedPlaylists(uploads)))'
            ).execute()

        self.channel_stats['id'] = channelId
        self.channel_stats['title'] = r['items'][0]['snippet']['title']
        self.channel_stats['numVisits'] = float(r['items'][0]['statistics']['viewCount'])
        self.channel_stats['numSubs'] = float(r['items'][0]['statistics']['subscriberCount'])
        self.channel_stats['numVideos'] = float(r['items'][0]['statistics']['videoCount'])
        self.channel_stats['mainPlaylistId'] = r['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        self.channel_stats['banner'] = r['items'][0]['brandingSettings']['image']['bannerExternalUrl']

    def __getPlaylistItems(self, playlistId, token=None):
        try:
            r = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=playlistId,
                maxResults=50,
                fields='nextPageToken, items(snippet(resourceId(videoId)))',
                pageToken = token
            ).execute()
        except:
            exceeded = True
            while exceeded:
                try:
                    new_key = self.keys.pop(0)
                    # Tellin the user the key was consumed. Switch to a new one and repeat the
                    # query with a new client
                    self.__informKeyShift("__getPlaylistItems", new_key)
                    self.current_key = new_key
                    self.youtube = googleapiclient.discovery.build(
                        self.api_service_name, self.api_version, developerKey = self.current_key
                    )

                    r = self.youtube.playlistItems().list(
                        part='snippet',
                        playlistId=playlistId,
                        maxResults=50,
                        fields='nextPageToken, items(snippet(resourceId(videoId)))',
                        pageToken = token
                    ).execute()
                    
                    exceeded = False

                except Exception as e:
                    if str(e) == "pop from empty list":
                        self.__informNoRemainingKeys("__getPlaylistItems")

        return r
        
    def getAllVideosIds(self, playlistId):
        n_videos = 0
        limit_reached = False

        r = self.__getPlaylistItems(playlistId)

        for video in r['items']:
            self.videos_ids.append(video['snippet']['resourceId']['videoId'])
            n_videos += 1

        # Trying to extract next token. This token will not exists if the channel has 
        # less or equal than 50 videos
        if "nextPageToken" in r:
            next_token = r['nextPageToken']
            remaining_results = True
        else:
            remaining_results = False

        while remaining_results and not limit_reached:
            r = self.__getPlaylistItems(playlistId, token=next_token)

            for video in r['items']:
                self.videos_ids.append(video['snippet']['resourceId']['videoId'])
                
                # Break if 10,000 videos limit is reached
                n_videos += 1
                if n_videos == 10000:
                    limit_reached = True
                    break
            
            if "nextPageToken" in r:
                next_token = r['nextPageToken']
                remaining_results = True
            else:
                remaining_results = False
        
    
    def __getVideos(self, ids):
        try:
            str_ids = ','.join(ids)
            r = self.youtube.videos().list(
                part="snippet, statistics",
                id=str_ids,
                fields = "items(id,snippet(publishedAt, title), " + 
                        "statistics(viewCount, likeCount, dislikeCount))"
            ).execute()
        except:
            exceeded = True
            while exceeded:
                try:
                    new_key = self.keys.pop(0)
                
                    # Tellin the user the key was consumed. Switch to a new one and repeat the
                    # query with a new client
                    self.__informKeyShift("__getVideos", new_key)
                    self.current_key = new_key
                    self.youtube = googleapiclient.discovery.build(
                        self.api_service_name, self.api_version, developerKey = self.current_key
                    )

                    str_ids = ','.join(ids)
                    r = self.youtube.videos().list(
                        part="snippet, statistics",
                        id=str_ids,
                        fields = "id, items(snippet(publishedAt, title), " + 
                                "statistics(viewCount, likeCount, dislikeCount))"
                    ).execute()

                    exceeded = False
                except Exception as e:
                    if str(e) == "pop from empty list":
                        self.__informNoRemainingKeys("__getVideos")

        return r['items']

    
    def getVideosStats(self,videos_ids):
        videos_items = []
        
        a, b, n_videos = 0, 0, len(videos_ids)

        if n_videos > 50:
            for i in range(50, n_videos, 50):
                b = i 
                videos_items.extend(self.__getVideos(videos_ids[a:b]))
                a = b
        
        videos_items.extend(self.__getVideos(videos_ids[b:]))

        for record in videos_items:
            record['snippet'].update(record['statistics'])
            record['snippet']['thumbnail'] = f"https://i1.ytimg.com/vi/{record['id']}/hqdefault.jpg"
            record['snippet']['id'] = record['id']

            self.videos_stats.append(record['snippet'])
    
    def __getSubs(self, channelId, token=None):
        try:
            r = self.youtube.subscriptions().list(
                part = "snippet",
                id=channelId,
                forChannelId = channelId,
                maxResults=50,
                order="relevance",
                pageToken=token,
                fields="nextPageToken, items(snippet(publishedAt, title, resourceId(channelId)))"
            ).execute()
        except Exception as e:
            if "The requester is not allowed to access the requested subscriptions" in str(e):
                print("Error. The channel does not allow to access its subscriptions.")
                print("Analysis will be done without subscriptions info.")
                
                return
            try:
                new_key = self.keys.pop(0)
            except:
                self.__informNoRemainingKeys("__getSubs")
            # Tellin the user the key was consumed. Switch to a new one and repeat the
            # query with a new client
            self.__informKeyShift("__getSubs", new_key)
            self.current_key = new_key
            self.youtube = googleapiclient.discovery.build(
                self.api_service_name, self.api_version, developerKey = self.current_key
            )

            r = self.youtube.subscriptions().list(
                part = "snippet",
                forChannelId = channelId,
                maxResults=50,
                order="relevance",
                pageToken=token,
                fields="nextPageToken, items(snippet(publishedAt, title, resourceId(channelId)))"
            ).execute()

        return r

    def getSubsIdAndDate(self, channelId):
        n_subs = 0
        limit_reached = False

        r = self.__getSubs(channelId)
        
        if not r:
            return

        for sub in r['items']:
            record = {}
            record['channelId'] = sub['snippet']['resourceId']['channelId']
            record['publishedAt'] = sub['snippet']['publishedAt']
            self.subs_date_and_id.append(record)
            n_subs += 1

        if "nextPageToken" in r:
            next_token = r['nextPageToken']
            remaining_results = True
        else:
            remaining_results = False

        while remaining_results and not limit_reached:
            r = self.__getSubs(channelId, token=next_token)
            for sub in r['items']:
                record = {}
                record['channelId'] = sub['snippet']['resourceId']['channelId']
                record['publishedAt'] = sub['snippet']['publishedAt']
                self.subs_date_and_id.append(record)
                n_subs += 1

                if n_subs == 1000000:
                    limit_reached = True
                    break
            
            if "nextPageToken" in r:
                next_token = r['nextPageToken']
                remaining_results = True
            else:
                remaining_results = False
    
    def __getChannelLanguageAndCountry(self, ids):
        try:
            str_ids = ','.join(ids)
            r = self.youtube.channels().list(
                part="snippet",
                id=str_ids,
                maxResults=50,
                fields="items(id, snippet(defaultLanguage, country))"
            ).execute()
        except:
            try:
                new_key = self.keys.pop(0)
            except:
                self.__informNoRemainingKeys("__getSubs")
            # Tellin the user the key was consumed. Switch to a new one and repeat the
            # query with a new client
            self.__informKeyShift("__getSubs", new_key)
            self.current_key = new_key
            self.youtube = googleapiclient.discovery.build(
                self.api_service_name, self.api_version, developerKey = self.current_key
            )

            str_ids = ','.join(ids)
            r = self.youtube.channels().list(
                part="id, snippet",
                id=str_ids,
                maxResults=50,
                fields="items(id, snippet(defaultLanguage, country))"
            ).execute()

        return r['items']

    def getSubsLanguageAndCountry(self):
        channel_items = []
        subs_list = [sub['channelId'] for sub in self.subs_date_and_id]

        if not subs_list:
            return

        a, b, n_subs = 0, 0, len(subs_list)

        if n_subs > 50:
            for i in range(50, n_subs, 50):
                b = i 
                channel_items.extend(self.__getChannelLanguageAndCountry(subs_list[a:b]))
                a = b
        
        channel_items.extend(self.__getChannelLanguageAndCountry(subs_list[b:]))

        for item in channel_items:
            record = {'channelId':item['id']}
            if "defaultLanguage" in item['snippet']:
                record['defaultLanguage'] = item['snippet']['defaultLanguage']
            else:
                record['defaultLanguage'] = None
            
            if "country" in item['snippet']:
                record['country'] = item['snippet']['country']
            else:
                record['country'] = None
            
            self.subs_language_and_country.append(record)


    def __getComments(self, video_id, token=None):
        try:
            r = self.youtube.commentThreads().list(
                    part = "snippet",
                    videoId = video_id,
                    maxResults = 100,
                    fields="nextPageToken, items(snippet(topLevelComment(" + 
                        "snippet(textDisplay, publishedAt))))",
                    pageToken=token,
                    textFormat = "plainText"
                ).execute()
        except Exception as e:
            if "has disabled comments" in str(e):
                print(f"video: {video_id} has disabled the comments\n\n")
                return
            
            exceeded = True
            while exceeded:
                try:
                    new_key = self.keys.pop(0)
            

                    # Tellin the user the key was consumed. Switch to a new one and repeat the
                    # query with a new client
                    self.__informKeyShift("__getComments", new_key)
                    self.current_key = new_key
                    self.youtube = googleapiclient.discovery.build(
                        self.api_service_name, self.api_version, developerKey = self.current_key
                    )

                    r = self.youtube.commentThreads().list(
                        part = "snippet",
                        videoId = video_id,
                        maxResults = 100,
                        fields="nextPageToken, items(snippet(topLevelComment(" + 
                            "snippet(textDisplay, publishedAt))))",
                        pageToken=token,
                        textFormat = "plainText"
                    ).execute()

                    exceeded = False

                except Exception as e:
                    if "has disabled comments" in str(e):
                        print(f"video: {video_id} has disabled the comments\n\n")
                        return
                    
                    if str(e) == "pop from empty list":
                        self.__informNoRemainingKeys("__getPlaylistItems")
            
        return r
    
    def getComments(self, videos_ids):
        n_videos = len(videos_ids)
        current_videos = 0

        for video_id in videos_ids:
            r = self.__getComments(video_id)
            
            if not r:
                continue

            for c in r['items']:
                record = {}
                record['videoId'] = video_id
                
                if "textDisplay" in c['snippet']['topLevelComment']['snippet']:
                    record['textDisplay'] = c['snippet']['topLevelComment']['snippet']['textDisplay'].replace('\n', ' ').strip()
                    record['publishedAt'] = c['snippet']['topLevelComment']['snippet']['publishedAt']
                else:
                    current_videos += 1
                    continue

                self.comments.append(record)
                
            current_videos += 1
            print(f"{current_videos}/{n_videos}", end="\r")
            




    
    