import streamlit as st
from sections.header import show_header
from sections.data_input import show_data_input, select_student
from sections.visualization import show_classroom_stats, subject_visualization, student_mark_freq_visualization, student_marks_per_subject
from utils.data_loader import load_data
from constants import TestConfig, AppConfig

# data = load_data(TestConfig.TEST_CSV_FILE_PATH.value)

def main():

    data = load_data(TestConfig.TEST_CSV_FILE_PATH.value)

    # Set page config
    st.set_page_config(
        page_title=AppConfig.APP_TITLE.value,
        page_icon=":globe_with_meridians:",
        layout="wide"
    )
    
    # Show header section
    show_header()

    # Show classroom visualization
    show_classroom_stats(data)
        
    # Show subject stats visualization
    subject_visualization(data)

    # Show student stats visualization
    selected_student = select_student(data)
    if selected_student:
        student_marks_per_subject(data, selected_student)
        student_mark_freq_visualization(data, selected_student)

if __name__ == "__main__":
    main()