import streamlit as st

st.set_page_config(page_title="YT Lottery", page_icon=":tada:", layout="centered")
st.title("YT Lottery")

url = st.sidebar.text_input("Enter YouTube video URL:", placeholder="https://www.youtube.com/watch?v=VIDEO_ID_HERE")
keyword = st.sidebar.text_input("Enter keyword to search for:", placeholder="e.g., 'win', 'prize', 'winner'")

col1, col2 = st.sidebar.columns(2)
if col1.button("Start", type="primary"):
    #logika zbierania komentarzy i sprawdzania, czy zawierają słowo kluczowe
    st.write("Starting to collect comments...")

if col2.button("Stop"):
    #logika zatrzymywania zbierania komentarzy
    st.write("Stopped collecting comments.")

placeholder_list = st.empty()
    