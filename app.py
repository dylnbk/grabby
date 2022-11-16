import streamlit as st
import os
import uuid
import re
import ffmpeg
import instaloader
import pyktok as pyk
import youtube_dl
from pytube import YouTube
from pytube.exceptions import *
from RedDownloader import RedDownloader
from os.path import basename
from itertools import islice
from zipfile import ZipFile

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

    # write <style> tags to allow custom css
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# calculate progress bar
def progress_func(stream, chunk, bytes_remaining):

    # send stream size and bytes remaining to calculate the progress
    size = stream.filesize
    p = int((float(abs(bytes_remaining-size)/size))*float(100))
    bar.progress(p)

# generate random file names
def file_name():

    # use uuid to create random strings, use .hex to get alphanumeric only
    result = str(uuid.uuid4().hex)
    return result

# YouTube downloader
def youtube_download(media_type):

    # grab YouTube datastream, on_progress_callback generates progress bar data
    yt = YouTube(url_from_user_youtube, on_progress_callback=progress_func)

    # if the user wants full video
    if media_type == "Video":
                
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
    
    # if the user wants audio only
    elif media_type == "Audio":

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

# Instagram downloader
def instagram_download(media_type, number_of_posts):

    # random file name
    output = file_name()

    # Get instance
    L = instaloader.Instaloader(save_metadata=False)

    if media_type == "Post":

        # basic URL formatting
        temp_url = url_from_user_instagram.partition("/p/")[2]
        url = "".join([temp_url[x] for x in range(0, 11)])

        # store a post object
        post = instaloader.Post.from_shortcode(L.context, url)

        # download the post
        L.download_post(post, target=f"{output}")

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

    elif media_type == "Profile":

        # basic URL formatting
        temp_url = url_from_user_instagram[:-1]
        url = temp_url.partition(".com/")[2]

        # create a profile object
        profile = instaloader.Profile.from_username(L.context, url)

        # get posts from profile
        posts = profile.get_posts()

        # if the user has input a specific # of posts to download
        if number_of_posts > 0:

            # iterate through user selected input and download them to a folder named f"{output}"
            for post in islice(posts, 0, number_of_posts):
                L.download_post(post, target=f"{output}")
        
        else:

            # iterate through all posts on profile and download them to a folder named f"{output}"
            for post in posts:
                L.download_post(post, target=f"{output}")

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

# TikTok downloader
def tiktok_download(media_type):

    # create a random file name
    output = file_name()

    # if the user chooses a single video
    if media_type == "Video":

        # this section is copied from pytok to get the same file name convention
        regex_url = re.findall('(?<=@)(.+?)(?=\?|$)', url_from_user_tiktok)[0]

        # store the name of the video
        video_fn = regex_url.replace('/','_') + '.mp4'

        # download the video
        pyk.save_tiktok(url_from_user_tiktok, True)

        # bar progress complete
        bar.progress(100)
        
        # create a download button for the user
        with open(f"{video_fn}", "rb") as file:
            st.download_button("Download", data=file, file_name=f"{output}.mp4", mime="Video")

    # if the user wants to download the last 10 videos
    elif media_type == "Profile":

        file_names = []

        tiktok_videos = pyk.get_account_video_urls(url_from_user_tiktok)

        pyk.save_tiktok_multi(tiktok_videos)

        for video_url in tiktok_videos:

            regex_url = re.findall('(?<=@)(.+?)(?=\?|$)', video_url)[0]

            file_names.append(regex_url.replace('/','_') + '.mp4')

        # create a ZipFile object
        with ZipFile(f"{output}.zip", 'w') as zipObj:

            for file in file_names:

                # Add file to zip
                zipObj.write(file)

        # bar progress complete
        bar.progress(100)

        # create a download button for the user
        with open(f"{output}.zip", "rb") as file:
            st.download_button("Download", data=file, file_name=f"{file_name()}.zip", mime="zip")

# Reddit downloader
def reddit_download(media_type):
    
    # generate a persistent file name
    output = file_name()

    # if the user wants to download a video
    if media_type == "Video":

        # download the video
        video_object = RedDownloader.Download(url_from_user_reddit, output=f"{output}")

        # if video is YouTube content, it will probably show error message as still figuring out a way to get this working
        if "youtu.be" in video_object.postLink or "youtube.com" in video_object.postLink:
            
            # bar progress complete
            bar.progress(100)
            
            # create a download button for the user
            with open(f"{output}.mp4", "rb") as file:
                st.download_button("Download", data=file, file_name=f"{file_name()}.mp4", mime=f"{media_type.lower()}")

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

# Twitter downloader
def twitter_downloader():
    
    output = file_name()

    ydl_opts = {'outtmpl': f'{output}.mp4'}

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url_from_user_twitter])

    # bar progress complete
    bar.progress(100)

    # create a download button for the user
    with open(f"{output}.mp4", "rb") as file:
        st.download_button("Download", data=file, file_name=f"{output}.mp4", mime="video")

# Surprise downloader - all yt-dlp supported sites
def surprise_downloader(media_type):

    output = file_name()

    if media_type == "Video":

        ydl_opts = {'outtmpl': f'{output}.mp4'}

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url_from_user_surprise])

        # bar progress complete
        bar.progress(100)

        # create a download button for the user
        with open(f"{output}.mp4", "rb") as file:
            st.download_button("Download", data=file, file_name=f"{output}.mp4", mime="video")

    elif media_type == "Audio":

        ydl_opts = {'outtmpl': f'{output}.mp3'}

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url_from_user_surprise])

        # bar progress complete
        bar.progress(100)

        # create a download button for the user
        with open(f"{output}.mp3", "rb") as file:
            st.download_button("Download", data=file, file_name=f"{output}.mp3", mime="audio")

    elif media_type == "Image":

        ydl_opts = {'outtmpl': f'{output}.jpeg'}

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url_from_user_surprise])

        # bar progress complete
        bar.progress(100)

        # create a download button for the user
        with open(f"{output}.jpeg", "rb") as file:
            st.download_button("Download", data=file, file_name=f"{output}.jpeg", mime="image")

# main
local_css("style.css")
st.title('Grab it.')

# define tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["YouTube", "Instagram", "TikTok", "Reddit", "Twitter", "Surprise"])

# create an info box
with st.expander("See info"):

    st.write("### Thanks for visiting Grabby!")

    st.write("""
        This website was made using Python, you can view the source [here](https://github.com/dylnbk/grabby).

        Unfortunately YouTube & Instagram only work correctly if you run this app locally.
        """)

    st.write("***")

    st.write("""
        ##### YouTube
        - Video (MP4) / Audio (MP3) download.
        - Web version doesn't work for every video yet.
         """)
    
    st.write("***")

    st.write("""
        ##### Instagram
        - Single post / Profile download.
        - Web version doesn't work yet.
         """)

    st.write("***")

    st.write("""
        ##### TikTok
        - Single video download.
        - Profile download - up to last 30 videos.
         """)

    st.write("***")

    st.write("""
        ##### Reddit
        - Video (MP4) / Audio (MP3) download - will convert videos to audio.
        - Image (JPG) / Gallery download - will grab all images in a post.
         """)

    st.write("***")

    st.write("""
        ##### Twitter
        - Video (MP4) download.
         """)

    st.write("***")

    st.write("""
        ##### Surprise
        - You can grab from many different places.
        - See [here](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) for a full list of supported websites.
         """)

    st.write("")
    st.write("")

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

# Instagram tab
with tab2:

    # create a form to capture URL and take user options
    with st.form("input_instagram", clear_on_submit=True):

        # get user URL with a text input box
        url_from_user_instagram = st.text_input('Enter the link:', placeholder='https://www.your-link-here.com/...')

        # create a column layout
        col1, col2 = st.columns([6.5, 1])

        # create a selection drop down box
        with col1:
            selection_instagram = st.selectbox('Selection', ('Post', 'Profile'), label_visibility="collapsed")

        # create a sumbit button
        with col2:
            confirm_selection_instagram = st.form_submit_button("Submit")

        # how many posts to download from profile
        number_of_posts = st.number_input('Leave at zero to grab all posts:', min_value=0, label_visibility="collapsed")

# TikTok tab
with tab3:

    # create a form to capture URL and take user options
    with st.form("input_tiktok", clear_on_submit=True):

        # get user URL with a text input box
        url_from_user_tiktok = st.text_input('Enter the link:', placeholder='https://www.your-link-here.com/...')

        # create a column layout
        col1, col2 = st.columns([6.5, 1])

        # create a selection drop down box
        with col1:
            selection_tiktok = st.selectbox('Selection', ('Video', 'Profile'), label_visibility="collapsed")

        # create a sumbit button
        with col2:
            confirm_selection_tiktok = st.form_submit_button("Submit")

# Reddit tab
with tab4:

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
with tab5:

    # create a form to capture URL and take user options
    with st.form("input_twitter", clear_on_submit=True):

        # get user URL with a text input box
        url_from_user_twitter = st.text_input('Enter the link:', placeholder='https://www.your-link-here.com/...')

        # create a column layout
        col1, col2 = st.columns([6.5, 1])

        # create a selection drop down box
        with col1:
            selection_twitter = st.selectbox('Selection', ('Video',), label_visibility="collapsed")

        # create a sumbit button
        with col2:
            confirm_selection_twitter = st.form_submit_button("Submit")

# Surprise tab
with tab6:

    # create a form to capture URL and take user options
    with st.form("input_surprise", clear_on_submit=True):

        # get user URL with a text input box
        url_from_user_surprise = st.text_input('Enter the link:', placeholder='https://www.your-link-here.com/...')

        # create a column layout
        col1, col2 = st.columns([6.5, 1])

        # create a selection drop down box
        with col1:
            selection_surprise = st.selectbox('Selection', ('Video', 'Image', 'Audio'), label_visibility="collapsed")

        # create a sumbit button
        with col2:
            confirm_selection_surprise = st.form_submit_button("Submit")

# start script
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

        # if user submits Instagram button
        elif confirm_selection_instagram:

            # if there is input in the URL field
            if url_from_user_instagram:

                # initialize a progress bar
                bar = st.progress(0)

                # grab content and generate download button
                instagram_download(selection_instagram, number_of_posts)

        # if user submits TikTok button
        elif confirm_selection_tiktok:

            # if there is input in the URL field
            if url_from_user_tiktok:

                # initialize a progress bar
                bar = st.progress(0)

                # grab content and generate download button
                tiktok_download(selection_tiktok)
        
        # if user submits Reddit button
        elif confirm_selection_reddit:

            # if there is input in the URL field
            if url_from_user_reddit:

                # initialize a progress bar
                bar = st.progress(0)

                # download media
                reddit_download(selection_reddit)

        # if user submits Twitter button
        elif confirm_selection_twitter:

            # if there is input in the URL field
            if url_from_user_twitter:

                # initialize a progress bar
                bar = st.progress(0)

                # call downloader
                twitter_downloader()

        # if user submits Twitter button
        elif confirm_selection_surprise:

            # if there is input in the URL field
            if url_from_user_surprise:

                # initialize a progress bar
                bar = st.progress(0)

                # call downloader
                surprise_downloader(selection_surprise)

    except Exception as e:
                st.error(f"This link is currently unavailable to download...\n\n{e}\n\n{number_of_posts}", icon="💔")