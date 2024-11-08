import os
import subprocess
from moviepy.editor import *
from loguru import logger
import json

def download_youtube_audio_as_mp3(youtube_url, output_path='output.mp3'):
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Download the audio using yt-dlp
    temp_audio = 'temp_audio.m4a'
    subprocess.run(['yt-dlp', '-x', '--audio-format', 'm4a', '-o', temp_audio, youtube_url], check=True)
    
    # Convert the downloaded file to mp3 using moviepy
    audio_clip = AudioFileClip(temp_audio)
    audio_clip.write_audiofile(output_path, codec='mp3')
    
    # Clean up temporary audio file
    os.remove(temp_audio)
    print(f"Downloaded and converted to {output_path}")

def download_youtube_video_as_mp4(youtube_url, output_path='output.mp4'):
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Download the video using yt-dlp
    temp_video = 'temp_video.mp4'
    subprocess.run(['yt-dlp', '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4', '-o', temp_video, youtube_url], check=True)
    
    # Move the downloaded video file to the desired output path
    os.rename(temp_video, output_path)
    print(f"Downloaded video to {output_path}")

def run_from_file_list():
    logger.info("Starting youtube downloader")
    logger.info("loading video list")
    with open('files_to_download.json') as f:
        video_list = json.load(f)
    
    for video in video_list:
        if video.get('video') is None:
            download_youtube_audio_as_mp3(video['url'], f"{video['filepath']}/{video['name']}.mp3")
        else:
            download_youtube_video_as_mp4(video['url'], f"{video['filepath']}/{video['name']}.mp4")

if __name__ == '__main__':
    run_from_file_list()
