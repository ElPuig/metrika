import streamlit as st

def create_sidebar():
    with st.sidebar:
        st.title("Navigation")
        page = st.radio("Go to", ["Home", "Analysis", "Settings"])
    return page