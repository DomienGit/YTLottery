import streamlit as st
from logic import thread_collect_comments, CommentAuthors, get_video_id
import threading

st.set_page_config(page_title="YT Lottery", page_icon=":tada:", layout="centered")
st.title("YT Lottery")

# Inicjalizacja CommentAuthors w st.session_state
if 'author_manager' not in st.session_state:
    st.session_state.author_manager = CommentAuthors()
if 'video_url' not in st.session_state:
    st.session_state.video_url = ""
if 'video_id' not in st.session_state:
    st.session_state.video_id = None
if 'url_confirmed' not in st.session_state:
    st.session_state.url_confirmed = False
if 'stop_event' not in st.session_state:
    st.session_state.stop_event = None
if 'active_thread' not in st.session_state:
    st.session_state.active_thread = None

entered_url = st.text_input("Wklej URL do transmisji/filmu YouTube:", placeholder="https://www.youtube.com/watch?v=VIDEO_ID_HERE", key="url_input")

if st.button("Potwierdź URL"):
    if not entered_url:
        st.error("Proszę wprowadzić URL.")
        st.session_state.url_confirmed = False
    else:
        video_id = get_video_id(entered_url)
        if not video_id:
            st.error("Nieprawidłowy URL YouTube. Proszę sprawdzić format.")
            st.session_state.url_confirmed = False
        else:
            st.session_state.video_url = entered_url
            st.session_state.video_id = video_id
            st.session_state.url_confirmed = True
            st.success("URL potwierdzony!")

if st.session_state.url_confirmed:
    st.write(f"Wybrany URL: {st.session_state.video_url}")

    keyword = st.text_input("Wprowadź słowo kluczowe do wyszukania w komentarzach:", placeholder="np. 'wygrałem', 'nagroda'")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Rozpocznij zbieranie komentarzy", type="primary"):
            st.session_state.stop_event = threading.Event()  # Używamy Event do kontrolowania wątku    
            st.info("Rozpoczynanie zbierania komentarzy... Może to potrwać, a dla streamów na żywo funkcja `collect_comments` będzie blokować aplikację.")
            # Wyczyść poprzednich autorów przed rozpoczęciem nowego zbierania
            st.session_state.author_manager = CommentAuthors()
            st.session_state.active_thread = threading.Thread(target=thread_collect_comments, args=(st.session_state.video_url, st.session_state.author_manager, st.session_state.stop_event))
            st.session_state.active_thread.start()

    with col2:
        if st.button("Zatrzymaj zbieranie"):
            st.warning("Zatrzymywanie zbierania komentarzy nie jest w pełni zaimplementowane dla blokującej funkcji `collect_comments`. Wymagałoby to uruchomienia w osobnym wątku.")
            # Placeholder dla logiki zatrzymywania
            st.session_state.stop_event.set()

    if st.session_state.active_thread and st.session_state.active_thread.is_alive():
        st.info("Zbieranie komentarzy w toku... Odśwież stronę, aby zobaczyć aktualną listę.")
    
    authors = st.session_state.author_manager.get_authors()
    if authors:
        st.write(f"### Zebrani unikalni autorzy ({len(authors)}):")
        for author in sorted(list(authors)): # Display all authors, sorted for consistency
            st.write(f"- {author}")
    