import streamlit as st

st.title("Testowa aplikacja YTLottery")

st.write("Witaj w prostej aplikacji do testowania Streamlit.")

st.info("Jeśli to widzisz, oznacza to, że Streamlit jest poprawnie skonfigurowany.")

if st.button("Pokaż magię!"):
    st.balloons()
    st.success("Magia! Przycisk działa.")
