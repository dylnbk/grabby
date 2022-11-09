import streamlit as st
from pytube import YouTube

# page configurations
st.set_page_config(
    page_title="Grab it.",
    page_icon="∞",
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

local_css("style.css")

st.title('Grab it.')

text_contents = "derp"

with st.form("input", clear_on_submit=True):

    video = st.text_input('Enter the YouTube link:', placeholder='https://www.youtube.com/watch...')

    col1, col2 = st.columns([7,1])

    with col1:
        selection = st.selectbox('Selection', ('Video', 'Audio', 'Playlist'), label_visibility="collapsed")
    with col2:
        test = st.form_submit_button("Submit")
    if test:
        if video:
            yt = YouTube(video)
            st.video(video)
            #stream.download()