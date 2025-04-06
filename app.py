import streamlit as st
from sections.header import show_header
from sections.data_input import show_data_input, select_student
from sections.visualization import show_classroom_stats, subject_visualization, student_mark_freq_visualization, student_marks_per_subject
from utils.data_loader import load_data
from constants import TestConfig, AppConfig

# data = load_data(TestConfig.TEST_CSV_FILE_PATH.value)

def main():

    data1 = load_data(TestConfig.TEST_CSV_FILE1_PATH.value)
    data2 = load_data(TestConfig.TEST_CSV_FILE2_PATH.value)

    # Set page config
    st.set_page_config(
        page_title=AppConfig.APP_TITLE.value,
        page_icon=":globe_with_meridians:",
        layout="wide"
    )
    
    # Show header section
    show_header()

    # Show classroom visualization
    show_classroom_stats(data1)
        
    # Show subject stats visualization
    subject_visualization(data1)

    # Show student stats visualization
    selected_student = select_student(data1)
    if selected_student:
        st.subheader(f"Diagrama de barras: notas por materia de {selected_student}")
        student_marks_per_subject(data1, selected_student, "1r trimestre")
        student_marks_per_subject(data2, selected_student, "2o trimestre")
        st.subheader(f"Distribución de notas para {selected_student}")
        col1, col2 = st.columns(2)
        with col1:
            student_mark_freq_visualization(data1, selected_student, "1r trimestre")
        with col2:
            student_mark_freq_visualization(data2, selected_student, "2o trimestre")

if __name__ == "__main__":
    main()