import streamlit as st
import os
import uuid
import re
import ffmpeg
import instaloader
import youtube_dl
import pyktok as pyk
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

    ydl_opts = {}

    # if the user wants full video
    if media_type == "Video":

        try:
                
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url_from_user_youtube])

        except Exception as e:
            f"{e}"

    # if the user wants audio only
    elif media_type == "Audio":
        
        pass


# Instagram downloader
def instagram_download(media_type):

    # random file name
    output = file_name()

    # Get instance
    L = instaloader.Instaloader(save_metadata=False)

    if media_type == "Video" or media_type == "Image":

        post = instaloader.Post.from_shortcode(L.context, url_from_user_instagram)

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

        # create a profile object
        profile = instaloader.Profile.from_username(L.context, url_from_user_instagram)

        posts = profile.get_posts()

        # iterate through 50 most recent posts on the profile and download them to a folder named f"{output}"
        for post in islice(posts, 0, 50):
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

        st.info("Development in progress")


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
            
            else:

                # throw a generic error
                st.error(f"This link is currently unavailable to download...", icon="💔")

    except Exception as e:
        st.error(f"This link is currently unavailable to download... \n\n{e}", icon="💔")

# main
local_css("style.css")
st.title('Grab it.')

# define tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["YouTube", "Instagram", "TikTok", "Reddit", "Twitter"])

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
            selection_instagram = st.selectbox('Selection', ('Video', 'Image', 'Profile'), label_visibility="collapsed")

        # create a sumbit button
        with col2:
            confirm_selection_instagram = st.form_submit_button("Submit")

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

        # if user submits Instagram button
        elif confirm_selection_instagram:

            # if there is input in the URL field
            if url_from_user_instagram:

                # initialize a progress bar
                bar = st.progress(0)

                # grab content and generate download button
                instagram_download(selection_instagram)
            
            # display generic error
            else:
                st.error(f"This link is currently unavailable to download...", icon="💔")

        # if user submits TikTok button
        elif confirm_selection_tiktok:

            # if there is input in the URL field
            if url_from_user_tiktok:

                # initialize a progress bar
                bar = st.progress(0)

                # grab content and generate download button
                tiktok_download(selection_tiktok)
            
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