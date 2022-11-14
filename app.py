import streamlit as st
import os
import uuid
import ffmpeg
from os.path import basename
from zipfile import ZipFile
from pytube import YouTube
from pytube.exceptions import *
from RedDownloader import RedDownloader

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
    yt = YouTube(url_from_user_youtube, on_progress_callback=progress_func)

    # if the user wants full video
    if media_type == "Video":

        try:
                
            # filter adpative / progressive streams, adaptive = audio & video are seperated 
            stream_adaptive = yt.streams.filter(adaptive=True)
            stream_progressive = yt.streams.filter(progressive=True)

            # display users video
            st.video(url_from_user_youtube)

            # if it's a progressive stream, for now use this as it's the fastest option
            if stream_progressive:

                # grab the highest quality video 
                video_stream = stream_progressive[-1]

                # capture file type
                video_type = video_stream.mime_type.partition("/")[2]

                # create a download button for the user, can output directly with pytube download()
                with open(video_stream.download(), "rb") as file:
                    st.download_button("Download", data=file, file_name=f"{file_name()}.{video_type}", mime="video")

            # else if it's an adaptive stream only, grab audio + video and merge them with ffmpeg
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
        
        # Try statments using pytube errors
        except VideoPrivate:
            st.error(" This video is private, you can't download it", icon="💔")
        except RegexMatchError:
            st.error(f" Invalid link format", icon="💔")
        except RecordingUnavailable:
            st.error(f" This recording is unavailable", icon="💔")
        except MembersOnly:
            st.error(f" This video is for channel members only", icon="💔")
        except LiveStreamError:
            st.error(f"This is a livestream, it cannot be downloaded", icon="💔")
        except HTMLParseError as e:
            st.error(f"This link is currently unavailable to download... \n\nHTMLParseError: {e}", icon="💔")
        except VideoUnavailable as e:
            st.error(f"This link is currently unavailable to download... \n\nVideoUnavailable: {e}", icon="💔")
    
    # if the user wants audio only
    elif media_type == "Audio":

        try:

            # check for audio only streams
            audio_stream = yt.streams.filter(only_audio=True)
            
            # if audio only is available convert to mp3 and provide download button
            if audio_stream:

                # display users video
                st.video(url_from_user_youtube)

                # create media and store file path
                audio_path = audio_stream[-1].download(filename=f"{file_name()}")

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
                st.video(url_from_user_youtube)

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

        # Try statments using pytube errors
        except VideoPrivate:
            st.error(" This video is private, you can't download it", icon="💔")
        except RegexMatchError:
            st.error(f" Invalid link format", icon="💔")
        except RecordingUnavailable:
            st.error(f" This recording is unavailable", icon="💔")
        except MembersOnly:
            st.error(f" This video is for channel members only", icon="💔")
        except LiveStreamError:
            st.error(f"This is a livestream, it cannot be downloaded", icon="💔")
        except HTMLParseError as e:
            st.error(f"This link is currently unavailable to download... \n\nError: {e}", icon="💔")
        except VideoUnavailable as e:
            st.error(f"This link is currently unavailable to download... \n\nError: {e}", icon="💔")

# Reddit downloader
def reddit_download(media_type):
    
    # generate a persistent file name
    output = file_name()

    try:

        # if the user wants to download a video
        if media_type == "Video":

            # download the video
            video_object = RedDownloader.Download(url_from_user_reddit, output=f"{output}")

            # if video is YouTube content, show error message as still figuring out a way to get this working
            if "youtu.be" in video_object.postLink or "youtube.com" in video_object.postLink:
                st.error(f"Please use the YouTube option...", icon="💔")

            # if it's a Reddit video, display a download button
            else:

                # bar progress complete
                bar.progress(100)

                # create a download button for the user
                with open(f"{output}.mp4", "rb") as file:
                    st.download_button("Download", data=file, file_name=f"{file_name()}.mp4", mime=f"{media_type.lower()}")
        
        # if the user wants only audio 
        elif media_type == "Audio":

            # grab the audio
            RedDownloader.GetPostAudio(url_from_user_reddit, output=f"{output}")

            # bar progress complete
            bar.progress(100)

            # create a download button for the user
            with open(f"{output}.mp3", "rb") as file:
                st.download_button("Download", data=file, file_name=f"{file_name()}.mp3", mime=f"{media_type.lower()}")
        
        # if the user is downloading a single image or a gallery of images
        elif media_type == "Image":

            # download the content and store the object
            media = RedDownloader.Download(url_from_user_reddit, output=f"{output}")

            # find out if it's a single image, gif or a gallery of images
            media_info = media.GetMediaType()

            # if it's an image
            if media_info == "i":

                # bar progress complete
                bar.progress(100)

                # create a download button for the user
                with open(f"{output}.jpeg", "rb") as file:
                    st.download_button("Download", data=file, file_name=f"{file_name()}.jpeg", mime=f"{media_type.lower()}")

            # if it's a gallery, iterate over the images and create a zip file for the user to download
            elif media_info == "g":

                # create a ZipFile object
                with ZipFile(f"{output}.zip", 'w') as zipObj:

                    # Iterate over all the files in directory
                    for folderName, subfolders, filenames in os.walk(output):

                        for filename in filenames:

                            #create complete filepath of file in directory
                            filePath = os.path.join(folderName, filename)

                            # Add file to zip
                            zipObj.write(filePath, basename(filePath))

                # bar progress complete
                bar.progress(100)

                # create a download button for the user
                with open(f"{output}.zip", "rb") as file:
                    st.download_button("Download", data=file, file_name=f"{file_name()}.zip", mime="zip")
                    
            # if it's a gif
            elif media_info == "gif":

                # bar progress complete
                bar.progress(100)

                # create a download button for the user
                with open(f"{output}.gif", "rb") as file:
                    st.download_button("Download", data=file, file_name=f"{file_name()}.gif", mime=f"{media_type.lower()}")
            
            else:

                # throw a generic error
                st.error(f"This link is currently unavailable to download...", icon="💔")

    except Exception as e:
        st.error(f"This link is currently unavailable to download... \n\n{e}", icon="💔")

# main
local_css("style.css")
st.title('Grab it.')

# define tabs
tab1, tab2, tab3 = st.tabs(["YouTube", "Reddit", "Twitter"])

# YouTube tab
with tab1:

    # create a form to capture URL and take user options
    with st.form("input_youtube", clear_on_submit=True):

        # get user URL with a text input box
        url_from_user_youtube = st.text_input('Enter the link:', placeholder='https://www.your-link-here.com/...')

        # create a column layout
        col1, col2 = st.columns([6.5, 1])

        # create a selection drop down box
        with col1:
            selection_youtube = st.selectbox('Selection', ('Video', 'Audio'), label_visibility="collapsed")

        # create a sumbit button
        with col2:
            confirm_selection_youtube = st.form_submit_button("Submit")

# Reddit tab
with tab2:

    # create a form to capture URL and take user options
    with st.form("input_reddit", clear_on_submit=True):

        # get user URL with a text input box
        url_from_user_reddit = st.text_input('Enter the link:', placeholder='https://www.your-link-here.com/...')

        # create a column layout
        col1, col2 = st.columns([6.5, 1])

        # create a selection drop down box
        with col1:
            selection_reddit = st.selectbox('Selection', ('Video', 'Audio', 'Image'), label_visibility="collapsed")

        # create a sumbit button
        with col2:
            confirm_selection_reddit = st.form_submit_button("Submit")

# Twitter tab
with tab3:

    # create a form to capture URL and take user options
    with st.form("input_twitter", clear_on_submit=True):

        # get user URL with a text input box
        url_from_user_twitter = st.text_input('Enter the link:', placeholder='https://www.your-link-here.com/...')

        # create a column layout
        col1, col2 = st.columns([6.5, 1])

        # create a selection drop down box
        with col1:
            selection_twitter = st.selectbox('Selection', ('Video', 'Audio'), label_visibility="collapsed")

        # create a sumbit button
        with col2:
            confirm_selection_twitter = st.form_submit_button("Submit")

if __name__ == "__main__":

    try:
        
        # if user submits YouTube button
        if confirm_selection_youtube:

            # if there is input in the URL field
            if url_from_user_youtube:

                # initialize a progress bar
                bar = st.progress(0)

                # grab content and generate download button
                youtube_download(selection_youtube)
            
            # display generic error
            else:
                st.error(f"This link is currently unavailable to download...", icon="💔")

        # if user submits Reddit button
        elif confirm_selection_reddit:

            # if there is input in the URL field
            if url_from_user_reddit:

                # initialize a progress bar
                bar = st.progress(0)

                # download media
                reddit_download(selection_reddit)
            
            # display generic error
            else:
                st.error(f"This link is currently unavailable to download...", icon="💔")

        # if user submits Twitter button
        elif confirm_selection_twitter:

            # if there is input in the URL field
            if url_from_user_twitter:

                # grab content and generate download button
                st.info("Development in progress")
            
            # display generic error
            else:
                st.info("Development in progress")

    except Exception as e:
                st.error(f"This link is currently unavailable to download... \n\n{e}", icon="💔")