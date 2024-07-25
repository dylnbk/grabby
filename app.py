import streamlit as st
import os
import uuid
import re
import shutil
import ffmpeg
import instaloader
import pyktok as pyk
import yt_dlp
from pytube import YouTube
from pytube import Playlist
from RedDownloader import RedDownloader
from os.path import basename
from itertools import islice
from zipfile import ZipFile

# load & inject style sheet
def local_css(file_name):

    # write <style> tags to allow custom css
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# generate random file names
def file_name():

    # use uuid to create random strings, use .hex to get alphanumeric only
    result = str(uuid.uuid4().hex)
    return result

# create a zip file
def zip_files(file_name):

    # create a ZipFile object
        with ZipFile(f"{file_name}.zip", 'w') as zipObj:

            # Iterate over all the files in directory
            for folderName, subfolders, filenames in os.walk(file_name):

                for filename in filenames:

                    #create complete filepath of file in directory
                    filePath = os.path.join(folderName, filename)

                    # Add file to zip
                    zipObj.write(filePath, basename(filePath))

# delete files
def delete_files(path):

    # check if file or directory exists
    if os.path.isfile(path) or os.path.islink(path):
        
        # remove file
        os.remove(path)

    elif os.path.isdir(path):

        # remove directory and all its content
        shutil.rmtree(path)

# YouTube video helper
def video_processor(video, quality, playlist):

    # generate a persistent file name
    video_name = file_name()

    # if user wants full HQ, we will try to get the adaptive stream first
    if quality:

        # if the user is downloading a playlist
        if playlist:

            # try adaptive first as it contains highest quality video
            if video.streams.filter(adaptive=True):

                # capture file types
                audio_type = video.streams.filter(adaptive=True)[0].mime_type.partition("/")[2]
                video_type = video.streams.filter(adaptive=True)[-1].mime_type.partition("/")[2]

                # download media and store file paths
                audio_path = video.streams.filter(adaptive=True)[-1].download(filename=f"{file_name()}.{audio_type}")
                video_path = video.streams.filter(adaptive=True)[0].download(filename=f"{file_name()}.{video_type}")

                # prep ffmpeg merge with video and audio input
                input_video = ffmpeg.input(video_path)
                input_audio = ffmpeg.input(audio_path)
                
                # merge the files into a single output
                ffmpeg.output(input_audio, input_video, f'{video_name}.mp4').run()

                # remove unrequired files
                delete_files(audio_path)
                delete_files(video_path)

                # return video name
                return f"{video_name}.mp4"

            # if there is a video & audio merged stream available
            elif video.streams.filter(progressive=True):

                # capture file type
                video_type = video.streams.filter(progressive=True)[-1].mime_type.partition("/")[2]

                # download media
                video.streams.filter(progressive=True)[-1].download(filename=f"{video_name}.{video_type}")

                # return the file name
                return f"{video_name}.{video_type}"
        
        # not a playlist, so only single videos
        else:

            # filter adpative / progressive streams, adaptive = audio & video are seperated 
            stream_adaptive = video.streams.filter(adaptive=True)
            stream_progressive = video.streams.filter(progressive=True)

            # else if it's an adaptive stream only, grab audio + video and merge them with ffmpeg
            if stream_adaptive:

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

                # merge the files into a single output
                ffmpeg.output(input_audio, input_video, f'{video_name}.mp4').run()

                # create a download button for the user
                with open(f"{video_name}.mp4", "rb") as file:
                    st.download_button("Download", data=file, file_name=f"{file_name()}.mp4", mime="video")

                # delete remaining files
                delete_files(f"{video_name}.mp4")
                delete_files(video_path)
                delete_files(audio_path)

            # if it's only a progressive stream
            elif stream_progressive:

                # grab the highest quality video 
                video_stream = stream_progressive[-1]

                # capture file type
                video_type = video_stream.mime_type.partition("/")[2]

                # create media and store file path
                video_path = video_stream.download()

                # create a download button for the user, can output directly with pytube download()
                with open(video_path, "rb") as file:
                    st.download_button("Download", data=file, file_name=f"{file_name()}.{video_type}", mime="video")

                # delete remaining files
                delete_files(video_path)

    # user did not check the HQ box, so we can get the progressive stream as it's the fastest
    else:

        # if user wants a playlist
        if playlist:

            # if there is a video & audio merged stream available
            if video.streams.filter(progressive=True):

                # capture file type
                video_type = video.streams.filter(progressive=True)[-1].mime_type.partition("/")[2]

                # download media
                video.streams.filter(progressive=True)[-1].download(filename=f"{video_name}.{video_type}")

                # return the file name
                return f"{video_name}.{video_type}"

            # if there is only seperate video and audio streams available
            elif video.streams.filter(adaptive=True):

                # capture file types
                audio_type = video.streams.filter(adaptive=True)[0].mime_type.partition("/")[2]
                video_type = video.streams.filter(adaptive=True)[-1].mime_type.partition("/")[2]

                # download media and store file paths
                audio_path = video.streams.filter(adaptive=True)[-1].download(filename=f"{file_name()}.{audio_type}")
                video_path = video.streams.filter(adaptive=True)[0].download(filename=f"{file_name()}.{video_type}")

                # prep ffmpeg merge with video and audio input
                input_video = ffmpeg.input(video_path)
                input_audio = ffmpeg.input(audio_path)
                
                # merge the files into a single output
                ffmpeg.output(input_audio, input_video, f'{video_name}.mp4').run()

                # remove unrequired files
                delete_files(audio_path)
                delete_files(video_path)

                # return video name
                return f"{video_name}.mp4"
        
        # user wants a single video 
        else:

            # filter adpative / progressive streams, adaptive = audio & video are seperated 
            stream_adaptive = video.streams.filter(adaptive=True)
            stream_progressive = video.streams.filter(progressive=True)

            # if it's a progressive stream, use this as it's the faster option
            if stream_progressive:

                # grab the highest quality video 
                video_stream = stream_progressive[-1]

                # capture file type
                video_type = video_stream.mime_type.partition("/")[2]

                # create media and store file path
                video_path = video_stream.download()

                # create a download button for the user, can output directly with pytube download()
                with open(video_path, "rb") as file:
                    st.download_button("Download", data=file, file_name=f"{file_name()}.{video_type}", mime="video")

                # delete remaining files
                delete_files(video_path)

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

                # merge the files into a single output
                ffmpeg.output(input_audio, input_video, f'{video_name}.mp4').run()

                # create a download button for the user
                with open(f"{video_name}.mp4", "rb") as file:
                    st.download_button("Download", data=file, file_name=f"{file_name()}.mp4", mime="video")

                # delete remaining files
                delete_files(f"{video_name}.mp4")
                delete_files(video_path)
                delete_files(audio_path)

# YouTube audio helper
def audio_processor(video):

    # generate a persistent file name
    audio_name = file_name()

    # if there is an audio stream available
    if video.streams.filter(only_audio=True):
        
        # create media and store file path
        audio_path = video.streams.filter(only_audio=True)[-1].download(filename=file_name())

        # prep ffmpeg with input
        input_audio = ffmpeg.input(audio_path)

        # convert to mp3
        ffmpeg.output(input_audio, f'{audio_name}.mp3').run()

        # delete spare file
        delete_files(audio_path)

        # return the file name 
        return f'{audio_name}.mp3'

    else:

        # grab the highest quality stream and store file path
        video_path = video.streams[-1].download(filename=file_name())

        # prep ffmpeg with video input
        input_video = ffmpeg.input(video_path)

        # output the audio only
        ffmpeg.output(input_video, f'{audio_name}.mp3').run()

        # delete spare file
        delete_files(video_path)

        # return the file name 
        return f'{audio_name}.mp3'

# YouTube downloader
def youtube_download(media_type, number_of_posts_youtube, quality):

    # random file name
    output = file_name()

    # if the user wants full video
    if media_type == "Video":

        # grab YouTube datastream
        video = YouTube(url_from_user_youtube)
        
        # send stream to be processed and downloaded
        video_processor(video, quality, False)
    
    # if the user wants audio only
    elif media_type == "Audio":

        # grab YouTube datastream
        yt = YouTube(url_from_user_youtube)

        # check for audio only streams
        audio_stream = yt.streams.filter(only_audio=True)
        
        # if audio only is available convert to mp3 and provide download button
        if audio_stream:

            # create media and store file path
            audio_path = audio_stream[-1].download(filename=file_name())

            # prep ffmpeg with input
            input_audio = ffmpeg.input(audio_path)

            # convert to mp3
            ffmpeg.output(input_audio, f'{output}.mp3').run()
            
            # create a download button for the user, can output directly with pytube download()
            with open(f"{output}.mp3", "rb") as file:
                st.download_button("Download", data=file, file_name=f"{file_name()}.mp3", mime="audio")

            # delete remaining files
            delete_files(f"{output}.mp3")
            delete_files(audio_path)

        # if video only available, extract the audio
        else:

            # grab the highest quality stream
            new_stream = yt.streams[-1]

            # create media and store file path
            video_path = new_stream.download(filename=f"video")

            # prep ffmpeg with video input
            input_video = ffmpeg.input(video_path)

            # output the audio only
            ffmpeg.output(input_video, f'{output}.mp3').run()

            # create a download button for the user
            with open(f"{output}.mp3", "rb") as file:
                st.download_button("Download", data=file, file_name=f"{file_name()}.mp3", mime="audio")

            # delete remaining files
            delete_files(f"{output}.mp3")
            delete_files(video_path)

    # if the user wants to download a video playlist
    elif media_type == "Video - Playlist":
        
        # create a playlist object
        p = Playlist(url_from_user_youtube)

        # create a list for file names
        playlist_files = []

        # if the user limited their selection
        if number_of_posts_youtube > 0:

            # iterate through their choice
            for video in islice(p.videos, 0, number_of_posts_youtube):

                # send video object to be processed and downloaded
                playlist_files.append(video_processor(video, quality, True))

        else:

            # iterate through every video
            for video in p.videos:

                # send video object to be processed and downloaded
                playlist_files.append(video_processor(video, quality, True))

        # create a ZipFile object
        with ZipFile(f"{output}.zip", 'w') as zipObj:

            for file in playlist_files:

                # Add file to zip
                zipObj.write(file)

        # create a download button for the user
        with open(f"{output}.zip", "rb") as file:
            st.download_button("Download", data=file, file_name=f"{file_name()}.zip", mime="zip")

        # removing a files
        for file in playlist_files:

            delete_files(file)

        delete_files(f"{output}.zip")

    # if the user wants to download an audio only playlist
    elif media_type == "Audio - Playlist":

        # create a playlist object
        p = Playlist(url_from_user_youtube)

        # create a list for file names
        playlist_files = []

        # if the user limited their selection
        if number_of_posts_youtube > 0:

            # iterate through their choice
            for video in islice(p.videos, 0, number_of_posts_youtube):
                
                # send video object to be processed and downloaded
                playlist_files.append(audio_processor(video))

        else:

            # iterate through every video
            for video in p.videos:
                
                # send video object to be processed and downloaded
                playlist_files.append(audio_processor(video))

        # create a ZipFile object
        with ZipFile(f"{output}.zip", 'w') as zipObj:

            for file in playlist_files:

                # Add file to zip
                zipObj.write(file)

        # create a download button for the user
        with open(f"{output}.zip", "rb") as file:
            st.download_button("Download", data=file, file_name=f"{file_name()}.zip", mime="zip")

        # removing files
        for file in playlist_files:

            delete_files(file)

        delete_files(f"{output}.zip")

# Instagram downloader
def instagram_download(media_type, number_of_posts_insta):

    # random file name
    output = file_name()

    # Get instance
    L = instaloader.Instaloader(save_metadata=False)

    # if the user wants a video or image post
    if media_type == "Video" or media_type == "Image":

        # basic URL formatting
        temp_url = url_from_user_instagram.partition("/p/")[2]
        url = "".join([temp_url[x] for x in range(0, 11)])

        # store a post object
        post = instaloader.Post.from_shortcode(L.context, url)

        # download the post
        L.download_post(post, target=f"{output}")

        # create a ZipFile object
        zip_files(output)

        # create a download button for the user
        with open(f"{output}.zip", "rb") as file:
            st.download_button("Download", data=file, file_name=f"{file_name()}.zip", mime="zip")

        # removing a files
        delete_files(f"{output}.zip")
        delete_files(output)
        
    # if the user wants a full profile
    elif media_type == "Profile":

        # basic URL formatting
        temp_url = url_from_user_instagram[:-1]
        url = temp_url.partition(".com/")[2]

        # create a profile object
        profile = instaloader.Profile.from_username(L.context, url)

        # get posts from profile
        posts = profile.get_posts()

        # if the user has input a specific # of posts to download
        if number_of_posts_insta > 0:

            # iterate through user selected input and download them to a folder named f"{output}"
            for post in islice(posts, 0, number_of_posts_insta):
                L.download_post(post, target=f"{output}")
        
        else:

            # iterate through all posts on profile and download them to a folder named f"{output}"
            for post in posts:
                L.download_post(post, target=f"{output}")

        # create a ZipFile 
        zip_files(output)

        # create a download button for the user
        with open(f"{output}.zip", "rb") as file:
            st.download_button("Download", data=file, file_name=f"{file_name()}.zip", mime="zip")

        # removing a files
        delete_files(f"{output}.zip")
        delete_files(output)

# TikTok downloader
def tiktok_download(media_type, number_of_posts_tiktok):

    # create a persistent file name
    output = file_name()

    # if the user chooses a single video
    if media_type == "Video":

        # this section is copied from pytok to get the same file name convention
        regex_url = re.findall(r'(?<=@)(.+?)(?=\?|$)', url_from_user_tiktok)[0]

        # store the name of the video
        video_fn = regex_url.replace('/','_') + '.mp4'

        # download the video
        pyk.save_tiktok(url_from_user_tiktok, True)
        
        # create a download button for the user
        with open(f"{video_fn}", "rb") as file:
            st.download_button("Download", data=file, file_name=f"{output}.mp4", mime="Video")

        # delete remaining files
        delete_files(video_fn)

    # if the user wants to download up to last 30 videos
    elif media_type == "Profile":

        # array for file names
        file_names = []

        # get up to 30 latest videos
        tiktok_videos = pyk.get_account_video_urls(url_from_user_tiktok)

        # if the user provided a selection
        if number_of_posts_tiktok > 0:

            # while the amount of URLs are more than the users selection
            while len(tiktok_videos) > number_of_posts_tiktok:

                # remove excess URLs
                tiktok_videos.pop()

        # save the selected videos
        pyk.save_tiktok_multi(tiktok_videos)

        # get a list of file names
        for video_url in tiktok_videos:

            regex_url = re.findall(r'(?<=@)(.+?)(?=\?|$)', video_url)[0]

            file_names.append(regex_url.replace('/','_') + '.mp4')

        # create a ZipFile object
        with ZipFile(f"{output}.zip", 'w') as zipObj:

            for file in file_names:

                # Add file to zip
                zipObj.write(file)

        # create a download button for the user
        with open(f"{output}.zip", "rb") as file:
            st.download_button("Download", data=file, file_name=f"{file_name()}.zip", mime="zip")

        # removing a files
        for file in file_names:

            delete_files(file)

        delete_files(f"{output}.zip")

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
            
            # create a download button for the user
            with open(f"{output}.mp4", "rb") as file:
                st.download_button("Download", data=file, file_name=f"{file_name()}.mp4", mime=f"{media_type.lower()}")

            # removing a files
            delete_files(f"{output}.mp4")

        # if it's a Reddit video, display a download button
        else:

            # create a download button for the user
            with open(f"{output}.mp4", "rb") as file:
                st.download_button("Download", data=file, file_name=f"{file_name()}.mp4", mime=f"{media_type.lower()}")

            # removing a files
            delete_files(f"{output}.mp4")
    
    # if the user wants only audio 
    elif media_type == "Audio":

        # grab the audio
        RedDownloader.GetPostAudio(url_from_user_reddit, output=f"{output}")

        # create a download button for the user
        with open(f"{output}.mp3", "rb") as file:
            st.download_button("Download", data=file, file_name=f"{file_name()}.mp3", mime=f"{media_type.lower()}")

        # removing a files
        delete_files(f"{output}.mp3")
    
    # if the user is downloading a single image or a gallery of images
    elif media_type == "Image":

        # download the content and store the object
        media = RedDownloader.Download(url_from_user_reddit, output=f"{output}")

        # find out if it's a single image, gif or a gallery of images
        media_info = media.GetMediaType()

        # if it's an image
        if media_info == "i":

            # create a download button for the user
            with open(f"{output}.jpeg", "rb") as file:
                st.download_button("Download", data=file, file_name=f"{file_name()}.jpeg", mime=f"{media_type.lower()}")

            # removing a files
            delete_files(f"{output}.jpeg")

        # if it's a gallery, iterate over the images and create a zip file for the user to download
        elif media_info == "g":

            # create a ZipFile object
            zip_files(output)

            # create a download button for the user
            with open(f"{output}.zip", "rb") as file:
                st.download_button("Download", data=file, file_name=f"{file_name()}.zip", mime="zip")

            # removing a files
            delete_files(f"{output}.zip")
            delete_files(output)
                
        # if it's a gif
        elif media_info == "gif":

            # create a download button for the user
            with open(f"{output}.gif", "rb") as file:
                st.download_button("Download", data=file, file_name=f"{file_name()}.gif", mime=f"{media_type.lower()}")

            # removing a files
            delete_files(f"{output}.gif")

# Twitter downloader
def twitter_downloader():
    
    # generate a persistent file name
    output = file_name()

    # grab .mp4
    ydl_opts = {'outtmpl': f'{output}.mp4'}

    # download if available
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url_from_user_twitter])

    # create a download button for the user
    with open(f"{output}.mp4", "rb") as file:
        st.download_button("Download", data=file, file_name=f"{output}.mp4", mime="video")

    # removing a files
    delete_files(f"{output}.mp4")

# Surprise downloader - all yt-dlp supported sites
def surprise_downloader(media_type):

    # generate a persistent file name
    output = file_name()

    # if user wants a video
    if media_type == "Video":

        # grab .mp4
        ydl_opts = {'outtmpl': f'{output}.mp4', 'format': 'mp4'}

        # download the file if available
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url_from_user_surprise])

        # create a download button for the user
        with open(f"{output}.mp4", "rb") as file:
            st.download_button("Download", data=file, file_name=f"{output}.mp4", mime="video")

        # removing a files
        delete_files(f"{output}.mp4")

    # if the user wants audio
    elif media_type == "Audio":

        # grab .mp3
        ydl_opts = {'outtmpl': f'{output}.mp3'}

        # download the file if available
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url_from_user_surprise])

        # create a download button for the user
        with open(f"{output}.mp3", "rb") as file:
            st.download_button("Download", data=file, file_name=f"{output}.mp3", mime="audio")

        # removing a files
        delete_files(f"{output}.mp3")

    # if the user wants image
    elif media_type == "Image":

        # grab .jpeg
        ydl_opts = {'outtmpl': f'{output}.jpeg'}

        # download the file if available
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url_from_user_surprise])

        # create a download button for the user
        with open(f"{output}.jpeg", "rb") as file:
            st.download_button("Download", data=file, file_name=f"{output}.jpeg", mime="image")

        # removing a files
        delete_files(f"{output}.jpeg")

# main VISUAL ELEMENTS BEGIN HERE <<----------------------------------------------------------------------------||

# burger menu config
st.set_page_config(
    page_title="Grab it.",
    page_icon="▶️",
    menu_items={
        'Report a bug': "mailto:dyln.bk@gmail.com",
        'Get help': None,
        'About': "Made by dyln.bk"
    }
)

# inject css
local_css("style.css")

# page title
st.title('Grab it.')

# define tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["YouTube", "Instagram", "TikTok", "Reddit", "Twitter", "Lucky 🤞 "])

# create an info box
with st.expander("See info"):

    st.write("### Thanks for visiting Grabby!")

    st.write("""
        This website was made using Python, you can view the source [here](https://github.com/dylnbk/grabby).
             
        Check out my personal website [dylnbk.page](https://dylnbk.page).
<<<<<<< HEAD:main.py
=======
        
        You can run this app locally by downloading and opening the Grabby.exe found [here](https://drive.google.com/file/d/1wpsyToNvN1-ouWkjOJ3J2fXI4GDANhT0/view?usp=sharing).
>>>>>>> 86dc29a0d37fc2e753266b8bb41c155935afa400:app.py

        To show support, you can ☕ [buy me a coffee](https://www.buymeacoffee.com/dylnbk).

        **CAUTION** 
        - Leaving the number input at zero will download the entire playlist/profile.
        - HQ will grab the highest available quality, which can take quite a while.
        """)

    st.write("***")

    st.write("""
        ##### YouTube
        - Video (MP4) & Audio (MP3) download.
        - Video (MP4) & Audio (MP3) playlist download.
        - Shorts (MP4) download.
         """)
    
    st.write("***")

    st.write("""
        ##### Instagram
        - Single post & Profile download.
        - Web version doesn't always work.
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
        - Video (MP4) & Audio (MP3) download - will convert videos to audio.
        - Image (JPG) & Gallery download - will grab all images in a post.
         """)

    st.write("***")

    st.write("""
        ##### Twitter
        - Video (MP4) download.
         """)

    st.write("***")

    st.write("""
        ##### Lucky 🤞
        - You can grab from many different places.
        - Powered by yt dlp - for a full list of supported websites visit [here](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).
         """)

    st.write("")
    st.write("")

# YouTube tab
with tab1:

    # create a form to capture URL and take user options
    with st.form("input_youtube", clear_on_submit=True):

        # get user URL with a text input box
        url_from_user_youtube = st.text_input('Enter a link:', placeholder='https://www.youtube.com...')

        # create a column layout
        col1, col2, col3 = st.columns([2, 1, 1])

        # create a selection drop down box
        with col1:
            selection_youtube = st.selectbox('Selection', ('Video', 'Audio', 'Video - Playlist', 'Audio - Playlist'), label_visibility="collapsed")

        # how many posts to download from profile
        with col2:
            number_of_posts_youtube = st.number_input('Leave at zero to grab entire playlist:', min_value=0, label_visibility="collapsed")

        # create a sumbit button
        with col3:
            confirm_selection_youtube = st.form_submit_button("Submit")

        # check box if True will try to download highest available stream
        quality = st.checkbox('HQ')

# Instagram tab
with tab2:

    # create a form to capture URL and take user options
    with st.form("input_instagram", clear_on_submit=True):

        # get user URL with a text input box
        url_from_user_instagram = st.text_input('Enter a link:', placeholder='https://www.instagram.com...')

        # create a column layout
        col1, col2, col3 = st.columns([2, 1, 1])

        # create a selection drop down box
        with col1:
            selection_instagram = st.selectbox('Selection', ('Video', 'Image', 'Profile'), label_visibility="collapsed")

        # how many posts to download from profile
        with col2:
            number_of_posts_insta = st.number_input('Leave at zero to grab all posts:', min_value=0, label_visibility="collapsed")

        # create a sumbit button
        with col3:
            confirm_selection_instagram = st.form_submit_button("Submit")

# TikTok tab
with tab3:

    # create a form to capture URL and take user options
    with st.form("input_tiktok", clear_on_submit=True):

        # get user URL with a text input box
        url_from_user_tiktok = st.text_input('Enter a link:', placeholder='https://www.tiktok.com...')

        # create a column layout
        col1, col2, col3 = st.columns([2, 1, 1])

        # create a selection drop down box
        with col1:
            selection_tiktok = st.selectbox('Selection', ('Video', 'Profile'), label_visibility="collapsed")

        # how many posts to download from profile
        with col2:
            number_of_posts_tiktok = st.number_input('Leave at zero to grab all posts:', min_value=0, max_value=30, label_visibility="collapsed")

        # create a sumbit button
        with col3:
            confirm_selection_tiktok = st.form_submit_button("Submit")

# Reddit tab
with tab4:

    # create a form to capture URL and take user options
    with st.form("input_reddit", clear_on_submit=True):

        # get user URL with a text input box
        url_from_user_reddit = st.text_input('Enter a link:', placeholder='https://www.reddit.com...')

        # create a column layout
        col1, col2 = st.columns([3, 1])

        # create a selection drop down box
        with col1:
            selection_reddit = st.selectbox('Selection', ('Video', 'Image', 'Audio'), label_visibility="collapsed")

        # create a sumbit button
        with col2:
            confirm_selection_reddit = st.form_submit_button("Submit")

# Twitter tab
with tab5:

    # create a form to capture URL and take user options
    with st.form("input_twitter", clear_on_submit=True):

        # get user URL with a text input box
        url_from_user_twitter = st.text_input('Enter a link:', placeholder='https://www.twitter.com...')

        # create a column layout
        col1, col2 = st.columns([3, 1])

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
        url_from_user_surprise = st.text_input('Enter a link:', placeholder='https://www.areyoulucky.com...')

        # create a column layout
        col1, col2 = st.columns([3, 1])

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
                
                with st.spinner(''):

                    # grab content and generate download button
                    youtube_download(selection_youtube, number_of_posts_youtube, quality)

        # if user submits Instagram button
        elif confirm_selection_instagram:

            # if there is input in the URL field
            if url_from_user_instagram:

                with st.spinner(''):

                    # grab content and generate download button
                    instagram_download(selection_instagram, number_of_posts_insta)

        # if user submits TikTok button
        elif confirm_selection_tiktok:

            # if there is input in the URL field
            if url_from_user_tiktok:

                with st.spinner(''):

                    # grab content and generate download button
                    tiktok_download(selection_tiktok, number_of_posts_tiktok)
        
        # if user submits Reddit button
        elif confirm_selection_reddit:

            # if there is input in the URL field
            if url_from_user_reddit:

                with st.spinner(''):

                    # download media
                    reddit_download(selection_reddit)

        # if user submits Twitter button
        elif confirm_selection_twitter:

            # if there is input in the URL field
            if url_from_user_twitter:

                with st.spinner(''):

                    # call downloader
                    twitter_downloader()

        # if user submits Surprise button
        elif confirm_selection_surprise:

            # if there is input in the URL field
            if url_from_user_surprise:

                with st.spinner(''):

                    # call downloader
                    surprise_downloader(selection_surprise)

    # pain
    except Exception as e:
                st.error(f"This link is currently unavailable to download...", icon="💔")
