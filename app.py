from flask import request, jsonify, Flask, render_template,send_file
from flask_sqlalchemy import SQLAlchemy
import  API
import matplotlib.pyplot as plt
import os
IsAnalysed = False
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
data_retrieval = API.YouTubeAPI(API_KEY='AIzaSyC3xxbqxbioB1jCH5gpzT-sT0zXsCbMBn4')
db = SQLAlchemy(app)

# ChannelId = "UC7IMq6lLHbptAnSucW1pClA"
@app.route('/')
def hello_world():
    # print("Hello world")
    return render_template('./index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    global ChannelId
    print("Search function")
    if request.method == 'POST':
        ChannelId = request.form['ChannelId']
        print(ChannelId)
        videos = data_retrieval.run(ChannelId)
        return render_template('./index.html', videos = zip(list(videos.keys()), list(videos.values())))
    return render_template('./index.html')
@app.route('/anaylse/<videoId>')
def anaylse(videoId):
    # print("Hello world")    
    # print(videoId)
    # print("videoId", videoId)
    details = API.Analyse(ChannelId, videoId)
    score = details[-1]
    # print(details)
    plt.pie([score['pos'],score['neg'],score['neu']],labels=['Positive','Negative','Neutral'],autopct='%1.1f%%')
    plt.title("Sentiment Analysis for:\n " + details[1])
    plt.savefig('./static/images/Analysis.png')
    return send_file('static/images/Analysis.png', as_attachment=True)
if __name__ == "__main__":
    app.run(debug=True)

# Corey Shafer
# https://www.youtube.com/channel/UCCezIgC97PvUuR4_gbFUs5g