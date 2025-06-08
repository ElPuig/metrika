import streamlit as st
from sections.header import show_header
from sections.data_input import select_student
from sections.visualization import show_classroom_table, subject_visualization, student_mark_freq_visualization, student_marks_per_subject, show_student_evolution
from utils.data_loader import load_data
from utils.constants import TestConfig, AppConfig, DataConfig
import json
import os
import pandas as pd

# data = load_data(TestConfig.TEST_CSV_FILE_PATH.value)

def load_json_files():
    """Load all JSON files from the docs directory"""
    all_students = []
    docs_dir = "docs"
    
    for filename in os.listdir(docs_dir):
        if filename.endswith('.json'):
            with open(os.path.join(docs_dir, filename), 'r', encoding='utf-8') as f:
                students = json.load(f)
                all_students.extend(students)
    
    return all_students

def main():
    # Load data from JSON files
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
    show_classroom_table(data1, title="T1")
    show_classroom_table(data2, title="T2")
    
    # Add a dropdown to select the column
    selected_subject = st.selectbox(key="sb_subject", label="Selecciona materia", options=DataConfig.SUBJ_NAMES.value)
    if selected_subject:        
        st.subheader("Estadísticas por materia")
        # Display the selected subject
        st.write(f"#### Materia seleccionada: {DataConfig.get_key_from_value(selected_subject)}")
        col1, col2 = st.columns(2)
        with col1:
            subject_visualization(data1, selected_subject, "1r trimestre")
        with col2:
            subject_visualization(data2, selected_subject, "2o trimestre")

    # Show student stats visualization
    students = load_json_files()
    student_names = [f"{student['nom_cognoms']} ({student['id']})" for student in students]
    selected_student = st.selectbox(
        "Selecciona un alumne:",
        student_names
    )
    
    if selected_student:
        st.subheader(f"Evolución de notas para {selected_student}")
        student_id = selected_student.split("(")[-1].strip(")")
        selected_student_data = next(student for student in students if student['id'] == student_id)
        show_student_evolution(data1, data2, selected_student_data, f"Evolución de notas entre trimestres - {selected_student}")
        
        st.subheader(f"Diagrama de barras: notas por materia de {selected_student}")
        student_marks_per_subject(data1, selected_student_data, "1r trimestre")
        student_marks_per_subject(data2, selected_student_data, "2o trimestre")
        
        st.subheader(f"Distribución de notas para {selected_student}")
        col1, col2 = st.columns(2)
        with col1:
            student_mark_freq_visualization(data1, selected_student_data, "1r trimestre")
        with col2:
            student_mark_freq_visualization(data2, selected_student_data, "2o trimestre")

    # Display general comment
    st.subheader("Comentari General")
    st.write(selected_student_data['comentari_general'])
    
    # Create a DataFrame for the subjects
    subjects_data = []
    for subject in selected_student_data['materies']:
        subjects_data.append({
            'Materia': subject['materia'],
            'Qualificació': subject['qualificacio'],
            'Comentari': subject['comentari']
        })
    
    df = pd.DataFrame(subjects_data)
    
    # Display the subjects table
    st.subheader("Notes per Materia")
    st.dataframe(
        df,
        column_config={
            "Materia": st.column_config.TextColumn("Materia", width="medium"),
            "Qualificació": st.column_config.TextColumn("Qualificació", width="small"),
            "Comentari": st.column_config.TextColumn("Comentari", width="large")
        },
        hide_index=True
    )

if __name__ == "__main__":
    main()