import streamlit as st
from youtube_downloader import download_youtube_audio_as_mp3, download_youtube_video_as_mp4
from audio_separator.separator import Separator
import shutil
import os

def main():
    separator = Separator()

    separator.load_model(model_filename="htdemucs_ft.yaml")

    st.title("YouTube Downloader")
    st.write("This is a simple YouTube downloader that can download audio or video from YouTube.")

    file_name = st.text_input("Enter the file name")
    youtube_url = st.text_input("Enter the YouTube URL")

    standard_file_path = f"/Users/lucas/Library/CloudStorage/OneDrive-Personal/Black Violet/VS/{file_name}"

    download_type = st.selectbox("Select download type", ["Audio", "Video"])
    separate_audio = st.checkbox("Separate audio")

    if st.button("Download"):
        if download_type == "Audio":
            st.spinner(text="Downloading audio...")
            download_youtube_audio_as_mp3(youtube_url, standard_file_path+'/'+file_name+'.mp3')
           
            if separate_audio:
                st.spinner(text="Separating audio...")
                output_files = separator.separate(standard_file_path+'/'+file_name+'.mp3')
                st.spinner(text="Saving separated audio...")
                os.makedirs(os.path.dirname(standard_file_path+'/compose/'), exist_ok=True)
                for file in output_files:
                    shutil.move(file, standard_file_path+'/compose')
                st.spinner(text="Process complete!")
        else:
            download_youtube_video_as_mp4(youtube_url, standard_file_path+'/'+file_name+'.mp4')
        st.success("Process complete!")

if __name__ == '__main__':
    main()