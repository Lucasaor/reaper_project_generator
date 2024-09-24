from pytube import YouTube
import os
from moviepy.editor import *
from loguru import logger
import json

def download_youtube_audio_as_mp3(youtube_url, output_path='output.mp3'):
    # Create a YouTube object
    yt = YouTube(youtube_url)
    
    # Extract the audio stream
    audio_stream = yt.streams.filter(only_audio=True).first()
    
    # Download the audio stream
    audio_file = audio_stream.download(filename='temp_audio')
    
    # Convert the downloaded file to mp3 using moviepy
    audio_clip = AudioFileClip(audio_file)
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    audio_clip.write_audiofile(output_path, codec='mp3')
    
    # Clean up temporary audio file
    os.remove(audio_file)
    print(f"Downloaded and converted to {output_path}")

def download_youtube_video_as_mp4(youtube_url, output_path='output.mp4'):
   # Create a YouTube object
    yt = YouTube(youtube_url)

    # Get the highest resolution video stream
    video_stream = yt.streams.get_highest_resolution()

    # Download the video stream
    video_file = video_stream.download(filename='temp_video')

    # Move the downloaded video file to the desired output path
    os.rename(video_file, output_path)

    print(f"Downloaded video to {output_path}")
    print(f"Downloaded and converted to {output_path}")


def run_from_file_list():
    logger.info("Starting youtube downloader")
    logger.info("loading video list")
    with open('files_to_download.json') as f:
        video_list:list[dict] = json.load(f)
    
    for video in video_list:
        if video.get('video') is None:
            download_youtube_audio_as_mp3(video['url'], f"{video['filepath']}/{video["name"]}.mp3")
        else:
            download_youtube_video_as_mp4(video['url'], f"{video['filepath']}/{video["name"]}.mp4")

if __name__ == '__main__':
    run_from_file_list()

