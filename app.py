import streamlit as st
from pytube import YouTube

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
def youtube_download():

    # grab YouTube datastream, on_progress_callback generates progress bar data
    yt = YouTube(url_from_user, on_progress_callback=progress_func)
    stream = yt.streams.get_by_itag(22)
    
    # generate option to download file
    with open(stream.download(), "rb") as file:
        st.download_button("Download", data=file, file_name="grabit.mp4", mime="video")

# main
local_css("style.css")
st.title('Grab it.')

# create a form to capture URL and take user options
with st.form("input", clear_on_submit=True):

    url_from_user = st.text_input('Enter the link:', placeholder='https://www.your-link-here.com/...')

    # create a column layout for the selectbox and submit button
    col1, col2 = st.columns([6.5, 1])

    with col1:
        selection = st.selectbox('Selection', ('Video', 'Audio', 'Playlist'), label_visibility="collapsed")
    with col2:
        confirm_selection = st.form_submit_button("Submit")

if confirm_selection:

    # initialize a progress bar
    bar = st.progress(3)
    
    # display users video
    st.video(url_from_user)

    # grab content and generate download button
    youtube_download()