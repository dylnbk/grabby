import streamlit as st
from pytube import YouTube
import ffmpeg

# page configurations
st.set_page_config(
    page_title="Grab it.",
    page_icon="▶️",
    menu_items={
        'Report a bug': "mailto:dyln.bk@gmail.com",
        'Get help': None,
        'About': "Made by dyln.bk"
    }
)

# load & inject style sheet
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# calculate progress bar
def progress_func(stream, chunk, bytes_remaining):
    size = stream.filesize
    p = int((float(abs(bytes_remaining-size)/size))*float(100))
    bar.progress(p)

# YouTube downloader
def youtube_download(media_type):

    # grab YouTube datastream, on_progress_callback generates progress bar data
    yt = YouTube(url_from_user, on_progress_callback=progress_func)
    st.write(yt)

    # if the user wants full video
    if media_type == "Video":

        # filter adpative / progressive streams, adaptive = audio & video are seperated 
        stream_adaptive = yt.streams.filter(adaptive=True)
        stream_progressive = yt.streams.filter(progressive=True)
        st.write(stream_adaptive, stream_progressive)

        # if it's an adaptive stream
        if stream_adaptive:

            # grab the highest quality video and audio stream
            video_stream = stream_adaptive[0]
            audio_stream = stream_adaptive[-1]

            # capture the file type
            audio_type = audio_stream.mime_type.partition("/")[2]
            video_type = video_stream.mime_type.partition("/")[2]

            # create media and store file path
            video_path = video_stream.download(filename=f"video.{video_type}")
            audio_path = audio_stream.download(filename=f"audio.{audio_type}")

            # prep ffmpeg merge with video and audio input
            input_video = ffmpeg.input(video_path)
            input_audio = ffmpeg.input(audio_path)

            # merge the files into a single output
            ffmpeg.output(input_audio, input_video, f'finished_video.{video_type}').run()

            # create a download button for the user
            with open(f"finished_video.{video_type}", "rb") as file:
                st.download_button("Download", data=file, file_name=f"grabit.{video_type}", mime="video")

        # if it's a progressive stream 
        elif stream_progressive:

            # create a download button for the user, can output directly with pytube download()
            with open(stream_progressive.download(), "rb") as file:
                st.download_button("Download", data=file, file_name="grabit", mime="video")
    
    # if the user wants audio only
    elif media_type == "Audio":

        new_stream = yt.streams[-1]

        if new_stream.type == "audio":

            # capture the audio file type
            audio_type = new_stream.mime_type.partition("/")[2]
            
            # create a download button for the user, can output directly with pytube download()
            with open(new_stream.download(), "rb") as file:
                st.download_button("Download", data=file, file_name=f"grabit.mp3", mime="audio")

        # if video only available, extract the audio
        else:

            # create media and store file path
            video_path = new_stream.download(filename=f"video")

            # prep ffmpeg with video input
            input_video = ffmpeg.input(video_path)

            # output the audio only
            ffmpeg.output(input_video, f'finished_audio.mp3').run()

            # create a download button for the user
            with open(f"finished_audio.mp3", "rb") as file:
                st.download_button("Download", data=file, file_name=f"grabit.mp3", mime="audio")



# main
local_css("style.css")
st.title('Grab it.')

# create a form to capture URL and take user options
with st.form("input", clear_on_submit=True):

    # get user URL with a text input box
    url_from_user = st.text_input('Enter the link:', placeholder='https://www.your-link-here.com/...')

    # create a column layout for the selectbox and submit button
    col1, col2 = st.columns([6.5, 1])
    with col1:
        selection = st.selectbox('Selection', ('Video', 'Audio'), label_visibility="collapsed")
    with col2:
        confirm_selection = st.form_submit_button("Submit")

if confirm_selection:

    # initialize a progress bar
    bar = st.progress(3)
    
    # display users video
    st.video(url_from_user)

    # grab content and generate download button
    youtube_download(selection)
