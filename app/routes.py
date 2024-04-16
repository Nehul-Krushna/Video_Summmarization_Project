from flask import Blueprint, render_template, request, jsonify
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
from moviepy.video.io.VideoFileClip import VideoFileClip
import assemblyai as aai
from transformers import pipeline
import os
import requests
from pytube import YouTube
import time

main = Blueprint('main', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4'}
processing_progress = 0

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
    global processing_progress
    processing_progress = 0
    text = ''
    result_summaries = ''
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '' and allowed_file(file.filename):
            file.save(os.path.join(UPLOAD_FOLDER, "input_video.mp4"))
            processing_progress = 10
            if check_video_duration(os.path.join(UPLOAD_FOLDER, "input_video.mp4")):
                processing_progress = 30
                audio_path = convert_video_to_audio()
                processing_progress = 50
                text = convert_audio_to_text(audio_path)
                processing_progress = 70
                # Process the text in chunks and get summaries for each chunk
                result_summaries = process_large_text(text)
                processing_progress = 100

                #add sleep to check progress bar
                time.sleep(2)
            else:
                return render_template('home.html', error="Video duration should be less than 1 hour")
        else:
            return render_template('home.html', error="Invalid file format. Please upload a valid (.mp4) video file.")

    elif 'video_url' in request.form:
        video_url = request.form['video_url']
        if video_url:
            video_saved=save_video_from_url(video_url)
            processing_progress = 10
            if check_video_duration(os.path.join(UPLOAD_FOLDER, "input_video.mp4")):
                processing_progress = 30
                audio_path = convert_video_to_audio()
                processing_progress = 50
                text = convert_audio_to_text(audio_path)
                processing_progress = 70
                # Process the text in chunks and get summaries for each chunk
                result_summaries = process_large_text(text)
                processing_progress = 100
                #add sleep to check progress bar
                time.sleep(2)
            else:
                if video_saved:
                    return render_template('home.html', error="Video duration should be less than 1 hour")
                else:
                    return render_template('home.html', error="Invalid video URL")
    else:
        return render_template('home.html', error="No file or video URL provided. Please provide a file or video URL.")
    
    return render_template('audio_to_text.html', text=text,summary=result_summaries)

def check_video_duration(video_path, max_duration=60*60):
    # Load the video using moviepy
    video_clip = VideoFileClip(video_path)

    # Get the duration of the video
    video_duration = video_clip.duration

    # Check if the video duration is less than the maximum duration
    if video_duration <= max_duration:
        return True
    else:
        return False

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
            return True
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
            return True
    else:
        print("Invalid video URL")

def convert_audio_to_text(audio_path):
    global processing_progress
    aai.settings.api_key = "bf79eb95a322490bb79b682dc83d2893"
    transcriber = aai.Transcriber()
    processing_progress = 55
    transcript = transcriber.transcribe(audio_path)
    processing_progress = 60
    print("converted audio to text")
    return transcript.text

def convert_video_to_audio():
    global processing_progress
    video_path = os.path.join(UPLOAD_FOLDER, 'input_video.mp4')
    audio_path = os.path.join(UPLOAD_FOLDER, 'output_audio.wav')

    # Extract audio from the video using moviepy
    video_clip = VideoFileClip(video_path)
    processing_progress = 35
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(audio_path, codec='pcm_s16le')
    audio_clip.close()
    processing_progress = 40
    print(f"Extracted audio from video: {audio_path}")

    return audio_path

def process_large_text(input_text, words_per_chunk=512):
    # Split the input text into words
    words = input_text.split()

    # Create chunks of approximately words_per_chunk words
    chunks = [words[i:i + words_per_chunk] for i in range(0, len(words), words_per_chunk)]

    # Join each chunk to form the text chunk
    chunks_text = [' '.join(chunk) for chunk in chunks]
    
    # finding a number to add in processing_progress to get 100 for each chunk
    adder = 30//len(chunks_text)
    # Generate summaries for each chunk
    summaries = [generate_summary(chunk,adder) for chunk in chunks_text]
    print("text to summary done")
    return summaries

def generate_summary(text_chunk,adder):
    global processing_progress
    # Load pre-trained summarization model
    summarizer = pipeline("summarization")

    # Generate summary for the current chunk
    summary = summarizer(text_chunk, max_length=150, min_length=50, length_penalty=2.0, num_beams=4, early_stopping=True)
    if processing_progress+adder<=100:
        processing_progress+=adder

    return summary[0]['summary_text']

@main.route('/progress')
def progress():
    global processing_progress
    return jsonify({'progress': processing_progress})