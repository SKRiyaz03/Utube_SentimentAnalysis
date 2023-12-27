from flask import Flask, request, render_template, send_file, session
from flask_sqlalchemy import SQLAlchemy
import API
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)  # Generate a random secret key for sessions

db = SQLAlchemy(app)
data_retrieval = API.YouTubeAPI()  # Initialize the YouTubeAPI class

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        session['channel_id'] = request.form['ChannelId']
        videos = data_retrieval.get_video_data(session['channel_id'])
        return render_template('index.html', videos=videos.items())  # Pass video ID and title pairs
    return render_template('index.html')



@app.route('/analyse/<video_id>')
def analyse(video_id):
    if 'channel_id' not in session:
        return 'Channel ID not specified', 400

    channel_id = session['channel_id']
    comments = data_retrieval.get_comments(video_id)
    sentiment_score = API.analyse_comments(comments)

    plt.pie([sentiment_score['pos'], sentiment_score['neg'], sentiment_score['neu']], labels=['Positive', 'Negative', 'Neutral'], autopct='%1.1f%%')
    plt.title(f"Sentiment Analysis for Video ID: {video_id}")
    image_path = os.path.join('static', 'images', 'analysis.png')
    plt.savefig(image_path)
    plt.close()
    return send_file(image_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
