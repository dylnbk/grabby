import streamlit as st

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

form = st.form("input", clear_on_submit=True)
video = form.text_input('Enter the YouTube link:', placeholder='https://www.youtube.com/watch...')

col1, col2 = st.columns([1,1])

with col1:
    selection = form.selectbox('Selection', ('Video', 'Audio', 'Playlist'), label_visibility="collapsed")
with col2:
    form.form_submit_button("Submit")


