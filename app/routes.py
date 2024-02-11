from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
import cv2
import os
import requests
from pytube import YouTube
import cv2
import os

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


@main.route('/preprocess', methods=['GET'])
def preprocess_videos():
    videos_path = 'uploads/'
    processed_path = 'processed/'

    # Create processed folder if not exists
    os.makedirs(processed_path, exist_ok=True)

    # Loop through each video in the uploads folder
    for video_filename in os.listdir(videos_path):
        if video_filename.endswith('.mp4'):
            video_path = os.path.join(videos_path, video_filename)

            # Extract frames from the video
            frames_path = os.path.join(processed_path, f"{os.path.splitext(video_filename)[0]}_frames")
            os.makedirs(frames_path, exist_ok=True)
            extract_frames(video_path, frames_path)

            # Detect shot boundaries
            shots = detect_shot_boundaries(frames_path)

            # Save shot boundaries to a text file
            save_shot_boundaries(video_filename, shots)

    return "Video preprocessing completed!"

def extract_frames(video_path, frames_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame_filename = f"{frame_count}.jpg"
        frame_path = os.path.join(frames_path, frame_filename)

        cv2.imwrite(frame_path, frame)
        frame_count += 1

    cap.release()


def detect_shot_boundaries(frames_path):
    shots = []

    # Get the list of frame files in sorted order
    frame_files = sorted(os.listdir(frames_path), key=lambda x: int(x.split('.')[0]))

    # Compare each frame with the next one
    for i in range(len(frame_files) - 1):
        frame_path_current = os.path.join(frames_path, frame_files[i])
        frame_path_next = os.path.join(frames_path, frame_files[i + 1])

        # Read frames
        frame_current = cv2.imread(frame_path_current, cv2.IMREAD_GRAYSCALE)
        frame_next = cv2.imread(frame_path_next, cv2.IMREAD_GRAYSCALE)

        # Compute the absolute difference between frames
        frame_diff = cv2.absdiff(frame_current, frame_next)

        # Compute the mean of the pixel differences
        mean_diff = frame_diff.mean()

        # Define a threshold for shot boundary detection
        threshold = 30

        # If the mean difference exceeds the threshold, it indicates a shot boundary
        if mean_diff > threshold:
            shots.append(i + 1)  # Append the frame index where the shot boundary occurs

    return shots

def save_shot_boundaries(video_filename, shots):
    with open(f"processed/{os.path.splitext(video_filename)[0]}_shot_boundaries.txt", 'w') as file:
        for shot in shots:
            file.write(f"{shot}\n")