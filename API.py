import os
import re
import googleapiclient.discovery
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import string

# Download necessary NLTK data
nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('stopwords')

class YouTubeAPI:
    def __init__(self):
        api_service_name = "youtube"
        api_version = "v3"
        # developer_key = os.getenv("YOUTUBE_API_KEY")  # Use environment variable for API key
        developer_key ="AIzaSyC3xxbqxbioB1jCH5gpzT-sT0zXsCbMBn4"  # Use environment variable for API key
        self.youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=developer_key)

    def get_video_data(self, channel_id, max_results=13):
        request = self.youtube.search().list(
            part="snippet",
            type="video",
            channelId=channel_id,
            maxResults=max_results
        )
        response = request.execute()
        video_data = {item['id']['videoId']: item['snippet']['title'] for item in response['items']}
        return video_data

    def get_comments(self, video_id):
        comments = []
        next_page_token = None

        while True:
            response = self.search_comments(video_id, next_page_token)
            next_page_token, result = self.process_comments_response(response)
            comments.extend(result)
            if not next_page_token:
                break

        return comments

    def search_comments(self, video_id, page_token):
        request = self.youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            pageToken=page_token,
            maxResults=100
        )
        return request.execute()

    def process_comments_response(self, response):
        next_page_token = response.get('nextPageToken')
        comments = [item["snippet"]["topLevelComment"]["snippet"]["textDisplay"] for item in response["items"]]
        return next_page_token, comments

def remove_emoji(text):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def analyse_comments(comments):
    cleaned_comments = []
    for comment in comments:
        comment = remove_emoji(comment)
        comment = comment.lower().translate(str.maketrans('', '', string.punctuation))
        tokens = word_tokenize(comment, language='english')
        tokens = [word for word in tokens if word not in stopwords.words('english')]
        cleaned_comments.append(" ".join(tokens))

    all_text = " ".join(cleaned_comments)
    return SentimentIntensityAnalyzer().polarity_scores(all_text)

# Example usage:
# yt_api = YouTubeAPI()
# video_data = yt_api.get_video_data(channel_id="YOUR_CHANNEL_ID")
# comments = yt_api.get_comments(video_id="A_VIDEO_ID")
# sentiment_score = analyse_comments(comments)
