import streamlit as st
import uuid
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

# generate random file names
def file_name():
    result = str(uuid.uuid4().hex)
    return result

# YouTube downloader
def youtube_download(media_type):

    # grab YouTube datastream, on_progress_callback generates progress bar data
    yt = YouTube(url_from_user, on_progress_callback=progress_func)

    # if the user wants full video
    if media_type == "Video":

        try:
                
            # filter adpative / progressive streams, adaptive = audio & video are seperated 
            stream_adaptive = yt.streams.filter(adaptive=True)
            stream_progressive = yt.streams.filter(progressive=True)

            # display users video
            st.video(url_from_user)

            # if it's an adaptive stream
            if stream_progressive:

                # grab the highest quality video 
                video_stream = stream_progressive[-1]

                # capture file type
                video_type = video_stream.mime_type.partition("/")[2]

                # create a download button for the user, can output directly with pytube download()
                with open(video_stream.download(), "rb") as file:
                    st.download_button("Download", data=file, file_name=f"{file_name()}.{video_type}", mime="video")

            # if it's a progressive stream only
            elif stream_adaptive:

                # grab the highest quality video and audio stream
                video_stream = stream_adaptive[0]
                audio_stream = stream_adaptive[-1]

                # capture the file type
                audio_type = audio_stream.mime_type.partition("/")[2]
                video_type = video_stream.mime_type.partition("/")[2]

                # create media and store file path
                video_path = video_stream.download(filename=f"{file_name()}.{video_type}")
                audio_path = audio_stream.download(filename=f"{file_name()}.{audio_type}")

                # prep ffmpeg merge with video and audio input
                input_video = ffmpeg.input(video_path)
                input_audio = ffmpeg.input(audio_path)

                # random file name
                output = file_name()

                # merge the files into a single output
                ffmpeg.output(input_audio, input_video, f'{output}.{video_type}').run()

                # create a download button for the user
                with open(f"{output}.{video_type}", "rb") as file:
                    st.download_button("Download", data=file, file_name=f"{file_name()}.{video_type}", mime="video")
        
        except Exception:
            st.error(f"This link is currently unavailble to download... ", icon="🚨")
    
    # if the user wants audio only
    elif media_type == "Audio":

        try:

            # check for audio only streams
            audio_stream = yt.streams.filter(only_audio=True)
            
            # if audio only is available convert to mp3 and provide download button
            if audio_stream:

                # display users video
                st.video(url_from_user)

                # create media and store file path
                audio_path = audio_stream[-1].download(filename=f"audio")

                # prep ffmpeg with input
                input_audio = ffmpeg.input(audio_path)

                # random file name
                output = file_name()

                # convert to mp3
                ffmpeg.output(input_audio, f'{output}.mp3').run()
                
                # create a download button for the user, can output directly with pytube download()
                with open(f"{output}.mp3", "rb") as file:
                    st.download_button("Download", data=file, file_name=f"{file_name()}.mp3", mime="audio")

            # if video only available, extract the audio
            else:

                # grab the highest quality stream
                new_stream = yt.streams[-1]

                # display users video
                st.video(url_from_user)

                # create media and store file path
                video_path = new_stream.download(filename=f"video")

                # prep ffmpeg with video input
                input_video = ffmpeg.input(video_path)

                # random file name
                output = file_name()

                # output the audio only
                ffmpeg.output(input_video, f'{output}.mp3').run()

                # create a download button for the user
                with open(f"{output}.mp3", "rb") as file:
                    st.download_button("Download", data=file, file_name=f"{file_name()}.mp3", mime="audio")

        except Exception:
            st.error(f"This link is currently unavailble to download... ", icon="🚨")

# main
local_css("style.css")
st.title('Grab it.')

# create a form to capture URL and take user options
with st.form("input", clear_on_submit=True):

    # get user URL with a text input box
    url_from_user = st.text_input('Enter the link:', placeholder='https://www.your-link-here.com/...')

    # create a column layout
    col1, col2 = st.columns([6.5, 1])

    # create a selection drop down box
    with col1:
        selection = st.selectbox('Selection', ('Video', 'Audio'), label_visibility="collapsed")

    # create a sumbit button
    with col2:
        confirm_selection = st.form_submit_button("Submit")

try:

    # if there is input by the user
    if confirm_selection:

        # initialize a progress bar
        bar = st.progress(0)

        # grab content and generate download button
        youtube_download(selection)

except Exception:
            st.error(f"This link is currently unavailble to download... ", icon="🚨")