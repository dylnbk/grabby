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

def progress_func(stream, chunk, bytes_remaining):
    size = stream.filesize
    p = int((float(abs(bytes_remaining-size)/size))*float(100))
    bar.progress(p)

local_css("style.css")

test_data = "random"
# begin
st.title('Grab it.')

with st.form("input", clear_on_submit=True):

    url_from_user = st.text_input('Enter the YouTube link:', placeholder='https://www.youtube.com/watch...')

    col1, col2 = st.columns([7,1])

    with col1:
        selection = st.selectbox('Selection', ('Video', 'Audio', 'Playlist'), label_visibility="collapsed")
    with col2:
        confirm_selection = st.form_submit_button("Submit")

with st.container():
    if confirm_selection:
        if url_from_user:
            bar = st.progress(0)
            yt = YouTube(url_from_user, on_progress_callback=progress_func)
            stream = yt.streams.get_by_itag(22)
            st.video(url_from_user)
            with open(stream.download(), "rb") as file:
                st.download_button("Download", data=file, file_name="grabit.mp4", mime="video")
