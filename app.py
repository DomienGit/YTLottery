import streamlit as st
import multiprocessing
import random
import time

# Importujemy funkcje z app_no_streamlit.py
from logic import _get_video_id, start_chat_listener

def main():
    st.title("YouTube Lottery App")

    # Inicjalizacja stanu sesji
    if 'video_url' not in st.session_state:
        st.session_state.video_url = ""
    if 'video_id' not in st.session_state:
        st.session_state.video_id = None
    if 'authors' not in st.session_state:
        st.session_state.authors = multiprocessing.Manager().list() # Używamy Manager().list() do współdzielenia
    if 'listener_process' not in st.session_state:
        st.session_state.listener_process = None
    if 'is_listening' not in st.session_state:
        st.session_state.is_listening = False
    if 'stop_event_manager' not in st.session_state:
        st.session_state.stop_event_manager = multiprocessing.Manager()
    if 'stop_event' not in st.session_state:
        st.session_state.stop_event = st.session_state.stop_event_manager.Event()
    if 'drawn_author' not in st.session_state:
        st.session_state.drawn_author = None
    if 'authors_placeholder' not in st.session_state:
        st.session_state.authors_placeholder = None

    # Sekcja wprowadzania linku
    st.header("1. Podaj link do transmisji YouTube Live")
    new_url = st.text_input("Link do YouTube Live:", value=st.session_state.video_url, key="url_input")

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Potwierdź Link"):
            st.session_state.video_url = new_url
            st.session_state.video_id = _get_video_id(st.session_state.video_url)
            if st.session_state.video_id:
                st.success(f"Link poprawny! Video ID: {st.session_state.video_id}")
            else:
                st.error("Nieprawidłowy link do filmu YouTube. Spróbuj ponownie.")
                st.session_state.video_url = ""
                st.session_state.video_id = None

    if st.session_state.video_id:
        st.subheader("2. Kontroluj zbieranie autorów komentarzy")

        # Start/Stop Buttons
        if not st.session_state.is_listening:
            if st.button("Start Zbierania Autorów"):
                if st.session_state.video_id:
                    st.session_state.stop_event.clear() # Upewnij się, że zdarzenie jest czyste
                    st.session_state.authors = st.session_state.stop_event_manager.list() # Reset listy autorów
                    st.session_state.listener_process = multiprocessing.Process(
                        target=start_chat_listener, # Używamy zaimportowanej funkcji
                        args=(st.session_state.video_id, st.session_state.authors, st.session_state.stop_event)
                    )
                    st.session_state.listener_process.start()
                    st.session_state.is_listening = True
                    st.success("Rozpoczęto zbieranie autorów komentarzy...")
                else:
                    st.warning("Najpierw podaj i potwierdź prawidłowy link do YouTube Live.")
        else:
            if st.button("Zatrzymaj Zbieranie Autorów"):
                st.session_state.stop_event.set()
                if st.session_state.listener_process and st.session_state.listener_process.is_alive():
                    st.session_state.listener_process.join(timeout=5) # Poczekaj na zakończenie procesu
                    if st.session_state.listener_process.is_alive():
                        st.session_state.listener_process.terminate() # Zakończ proces, jeśli nie reaguje
                st.session_state.is_listening = False
                st.info("Zatrzymano zbieranie autorów komentarzy.")
                st.session_state.drawn_author = None # Reset drawn author after stopping


        # Wyświetlanie autorów
        st.subheader("Aktualni Autorzy Komentarzy:")
        authors_display = list(st.session_state.authors) # Kopiujemy do listy, aby uniknąć problemów z Manager().list()
        if authors_display:
            st.write(f"Liczba unikalnych autorów: {len(authors_display)}")
            if st.session_state.authors_placeholder is None:
                st.session_state.authors_placeholder = st.empty()
            st.session_state.authors_placeholder.code("\n".join(authors_display))
        else:
            st.write("Brak autorów do wyświetlenia.")
        
        # Automatyczne odświeżanie, gdy nasłuchiwanie jest aktywne
        if st.session_state.is_listening:
            time.sleep(1) # Odśwież co 1 sekundę
            st.rerun() # Wymusza odświeżenie Streamlit, aby aktualizować listę autorów


        # Losowanie
        if not st.session_state.is_listening and len(authors_display) > 0:
            st.subheader("3. Losowanie Autora")
            if st.button("Losuj Autora"):
                st.session_state.drawn_author = random.choice(authors_display)
                st.success(f"Wylosowano: {st.session_state.drawn_author}!")

            if st.session_state.drawn_author:
                st.write(f"Wylosowany autor: **{st.session_state.drawn_author}**")
                col3, col4, col5 = st.columns(3)
                with col3:
                    if st.button("Usuń i Losuj Ponownie"):
                        try:
                            # Tworzymy nową listę bez wylosowanego autora, a następnie przypisujemy do session_state.authors
                            new_authors_list = [author for author in list(st.session_state.authors) if author != st.session_state.drawn_author]
                            st.session_state.authors[:] = new_authors_list # Aktualizacja Manager().list()
                            st.session_state.drawn_author = None
                            st.rerun() # Odśwież widok
                        except ValueError:
                            st.error("Wylosowany autor nie znajduje się już na liście.")
                with col4:
                    if st.button("Pozostaw i Losuj Ponownie"):
                        st.session_state.drawn_author = None # Wyczyść wylosowanego, aby można było losować ponownie
                        st.rerun() # Odśwież widok
                with col5:
                    if st.button("Anuluj Losowanie"):
                        st.session_state.drawn_author = None
                        st.info("Anulowano losowanie.")

if __name__ == "__main__":
    main()
