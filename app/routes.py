from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
import os
import requests
from pytube import YouTube

main = Blueprint('main', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv'}

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')

@main.route('/upload', methods=['POST'])
def upload_file():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

    elif 'video_url' in request.form:
        video_url = request.form['video_url']
        if video_url:
            save_video_from_url(video_url)

    return redirect(url_for('main.home'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_video_from_url(video_url):
    # Parse the video URL
    parsed_url = urlparse(video_url)
    print("Debugging: ", parsed_url)
    # Check if the URL is a valid video URL
    if parsed_url.netloc in ['www.youtube.com', 'youtube.com','youtu.be']:
        try:
            # Download YouTube video using pytube
            print("debug1")
            yt = YouTube(video_url)
            stream = yt.streams.filter(file_extension='mp4').first()
            filename = secure_filename(yt.title + '.mp4')
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            stream.download(output_path=UPLOAD_FOLDER, filename=filename)
            print(f"Downloaded YouTube video: {filename}")
        except Exception as e:
            print(f"Error downloading YouTube video: {e}")
    elif parsed_url.scheme and parsed_url.netloc and parsed_url.path:
        response = requests.get(video_url, stream=True)

        if response.status_code == 200 and allowed_file(parsed_url.path):
            # Extract the filename from the URL path
            filename = secure_filename(os.path.basename(parsed_url.path))
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            # Save the video file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded video from URL: {filename}")