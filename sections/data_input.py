import streamlit as st
import pandas as pd

def show_data_input():
    with st.expander("Data Input", expanded=True):
        name = st.text_input("Enter your name")
        age = st.slider("Select your age", 0, 100)
        return {"name": name, "age": age}
    
def select_student(data:pd.DataFrame):
    # Add a dropdown to select a student by name
    student_names = data["NOM"].unique()  # Get unique student names
    return st.selectbox("Selecciona estudiante", student_names)