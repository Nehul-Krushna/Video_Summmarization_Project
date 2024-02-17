from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
from moviepy.video.io.VideoFileClip import VideoFileClip
from pydub import AudioSegment
import assemblyai as aai
import os
import nltk
import requests
from pytube import YouTube
import os
import speech_recognition as sr

main = Blueprint('main', __name__)

nltk.download('punkt')
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
    text = ''
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, "input_video.mp4"))
            audio_path = convert_video_to_audio()
            text = convert_audio_to_text(audio_path)

    elif 'video_url' in request.form:
        video_url = request.form['video_url']
        if video_url:
            save_video_from_url(video_url)
            audio_path = convert_video_to_audio()
            text = convert_audio_to_text(audio_path)

    
    return render_template('audio_to_text.html', text=text)

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
            yt = YouTube(video_url)
            stream = yt.streams.filter(file_extension='mp4').first()
            filename = secure_filename("input_video" + '.mp4')
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

def convert_audio_to_text(audio_path):
    aai.settings.api_key = "bf79eb95a322490bb79b682dc83d2893"
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_path)
    return transcript.text

def convert_video_to_audio():
    video_path = os.path.join(UPLOAD_FOLDER, 'input_video.mp4')
    audio_path = os.path.join(UPLOAD_FOLDER, 'output_audio.wav')

    # Extract audio from the video using moviepy
    video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(audio_path, codec='pcm_s16le')
    audio_clip.close()

    return audio_path