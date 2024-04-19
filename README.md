# Video Summarization Project

This project allows users to upload videos or provide video URLs, which are then processed to generate a textual summary. The algorithmic approach involves video preprocessing, feature extraction, temporal summarization, content clustering, summary length control, and summary generation.

## Table of Contents
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Uploading Videos](#uploading-videos)
  - [Providing Video URLs](#providing-video-urls)
- [Algorithmic Approach](#algorithmic-approach)
- [File Structure](#file-structure)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

### Prerequisites
Make sure you have the following prerequisites installed:
- Python (version 3.x)
- pip (Python package installer)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Nehul-Krushna/Video_Summmarization_Project.git

2. Install dependencies:
   ```bash
   pip install -r requirements.txt

3. run the script:
   ```bash
   python3 run.py

## Usage
### Uploading Videos
Users can upload videos directly through the website. Supported video formats include MP4.

### Providing Video URLs
Alternatively, users can provide video URLs (YouTube links) to generate summaries.

## Algorithmic Approach
### Video Processing and Summarization:
1. Input Handling:
  - Users can upload a video file directly or provide a URL to a video hosted online.
  - The application checks the validity of the input file or URL.
  - If a valid video file is uploaded, it is saved in the designated upload directory. If a valid URL is provided, the video is downloaded and saved locally.

2. Video Processing:
  - The uploaded video file undergoes audio extraction to convert it into a suitable format for text processing.
  - Audio extraction is performed using the moviepy library, which extracts audio from video files.
  - The extracted audio is saved as a separate file in the upload directory.

3. Speech-to-Text Conversion:
  - The extracted audio file is then processed using the AssemblyAI service for speech-to-text conversion.
  - AssemblyAI provides accurate transcription of audio content into text format.
  - The converted text data is used for further processing to generate summaries.

4. Text Summarization:
  - The converted text is divided into smaller chunks to improve processing efficiency.
  - Each chunk of text is passed through a pre-trained summarization model from the transformers library.
  - The summarization model generates concise summaries for each chunk, capturing the key information.
  - Summaries from all chunks are aggregated to create a comprehensive summary of the entire video content.

5. Output Presentation:
  - The generated summary is displayed to the user on the web interface.
  - Users can view the summarized content and download it for reference.
  - Additionally, a progress bar is shown to indicate the processing status, providing real-time feedback to the user.

6. Error Handling:
  - The application includes error handling mechanisms to address various scenarios, such as invalid input files, unavailable URLs, or exceeding processing limits.
  - Users are provided with informative error messages to guide them through the usage of the application effectively.

7. Performance Optimization:
  - To reduce execution time and enhance user experience, optimizations such as text chunking and parallel processing are implemented.
  - Text chunking divides the text into manageable portions, enabling efficient processing and summarization.
  - Parallel processing techniques leverage the computing resources efficiently, enabling faster execution of tasks.

## File Structure
- app/: Contains the Flask web application files.
  - static/: Static files such as CSS and JavaScript.
  - templates/: HTML templates for the web application.
  - routes.py: Handles the application routes.
- requirements.txt: List of Python dependencies.
- run.py: Main script to run the Flask application.
