import streamlit as st
import pandas as pd
from sections.visualization import student_marks_per_subject
from utils.data_loader import load_data
from constants import TestConfig

def main():
    st.title("Notas de todos los estudiantes")
    
    # Load data
    data1 = load_data(TestConfig.TEST_CSV_FILE1_PATH.value)
    data2 = load_data(TestConfig.TEST_CSV_FILE2_PATH.value)
    
    # Get all unique student names
    student_names = data1["NOM"].unique()
    
    for student in student_names:
        st.subheader(f"Evolución de notas de {student}")
        student_marks_per_subject(data1, student, "1r trimestre")
        student_marks_per_subject(data2, student, "2o trimestre")
        st.divider()

if __name__ == "__main__":
    main() 