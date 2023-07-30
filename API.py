import json
import googleapiclient.discovery
import nltk, string, re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
nltk.download('vader_lexicon')
class YouTubeAPI:
    get_name = dict()
    video_data = dict()
    API_KEY = ""
    def __init__ (self, API_KEY):
        api_service_name = "youtube"
        api_version = "v3"
        self.youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=API_KEY)
        self.API_KEY = API_KEY


    # to get the video ids and video names repectively
    def run(self, CHANNEL_ID):
        # print(CHANNEL_ID)
        request = self.youtube.search().list(
            part="snippet",
            type="video",
            channelId=CHANNEL_ID,
            maxResults=13
        )
        response = request.execute()
        for item in response['items']:
            title = item['snippet']['title']
            videoId = item['id']['videoId']
            # print(item,"\n")
            self.get_name[videoId] = title
            self.video_data[title] = videoId
        return self.video_data


    # to get the comments of a particular video returns a response
    def search_comments(self, video_id, page_token):
        request = self.youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            pageToken=page_token,
            maxResults=1000
        )
        response = request.execute()
        return response
    # retuns a list of comments of a particular video and next page token to scroll through the comments
    # (Not all the comments can be retrieved at once)
    def process_comments_response(self, response):
        next_page_token = response.get('nextPageToken')
        result = []
        for i, item in enumerate(response["items"]):
            comment = item["snippet"]["topLevelComment"]
            comment_text = comment["snippet"]["textDisplay"]
            result.append(comment_text)

        return next_page_token, result
    

    # Combining search_comments and process_comments_response to get all the comments of a particular video
    def getComments(self, videoId):
        comments = []
        dataExtractor = YouTubeAPI(self.API_KEY)# API Key
        next_page = None
        while True:
            response = dataExtractor.search_comments(videoId, next_page)
            next_page, result = dataExtractor.process_comments_response(response, self.videos)
            comments += result
            if not next_page:
                break
        return comments
    
    # running the sentiment analysis on the comments using the videoId
# def getData(APIKEY = "AIzaSyC3xxbqxbioB1jCH5gpzT-sT0zXsCbMBn4", CHANNELID = "UCLj_i7yL-8FZrdQA6eE4iqQ"):
#     comments = []
#     dataExtractor = YouTubeAPI(APIKEY)# API Key
#     videos = list(dataExtractor.run(CHANNELID).keys())#Channel ID
#     print("Videos: \n", videos)
#     video_id = dataExtractor.video_data[videos[int(input("Enter the video number: ")) - 1]]
#     # print(dataExtractor.search_comments(video_id, None))
#     next_page = None
#     while True:
#         response = dataExtractor.search_comments(video_id, next_page)
#         next_page, result = dataExtractor.process_comments_response(response, videos)
#         comments += result
#         if not next_page:
#             break
#     return comments
def getData(APIKEY, CHANNELID, VideoId):
    dataExtractor = YouTubeAPI(APIKEY)# API Key
    # video_data = dataExtractor.run(CHANNELID)#Channel ID
    comments = []
    next_page = None
    while True:
        response = dataExtractor.search_comments(VideoId, next_page)
        next_page, result = dataExtractor.process_comments_response(response)
        comments += result
        if not next_page:
            break
    # print(dataExtractor.get_name)
    # print(dataExtractor.get_name.keys() == dataExtractor.video_data.values())
    # print(dataExtractor.video_data.keys() == dataExtractor.get_name.values())
    return comments,dataExtractor.get_name[VideoId]
def remove_emoji(string):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)
# Filter Copy
# channel id = UC7IMq6lLHbptAnSucW1pClA
# video id = D23FmD_5nGs
def Analyse(CHANNELID, VideoId, APIKEY = "AIzaSyC3xxbqxbioB1jCH5gpzT-sT0zXsCbMBn4"):
    print("Analysis started")
    data,videoName = getData(APIKEY, CHANNELID, VideoId)
    cleaned_text = ""
    for i in range(len(data)):
        data[i] = remove_emoji(data[i])
        data[i] = data[i].lower()
        data[i] = data[i].translate(str.maketrans('', '', string.punctuation))
        data[i] = word_tokenize(data[i], language='english')
        data[i] = [word for word in data[i] if word not in stopwords.words('english')]
        cleaned_text += " ".join(data[i])
    score = SentimentIntensityAnalyzer().polarity_scores(cleaned_text)
    # plt.pie([score['pos'],score['neg'],score['neu']],labels=['Positive','Negative','Neutral'],autopct='%1.1f%%')
    # plt.show()
    # plt.savefig('static/images/pie.png')
    print("Analysis done")
    return (len(data), videoName, score)
# Analyse()
# to get the video name when the video id is given