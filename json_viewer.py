import streamlit as st
import json
import os
from sections.student_marks import display_student_marks
from sections.student_selector import display_student_selector
from sections.visualization import (
    display_marks_pie_chart, 
    display_group_statistics, 
    group_failure_table, 
    display_subjects_bar_chart, 
    display_student_ranking, 
    display_student_subject_heatmap,
    display_subject_statistics
)
from sections.evolution import display_evolution_dashboard
from utils.constants import MarkConfig
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px

def get_json_files(directory):
    """Get all JSON files in the directory"""
    json_files = []
    valid_trimesters = ['T1.json', 'T2.json', 'T3.json']
    for filename in os.listdir(directory):
        if filename in valid_trimesters:
            json_files.append(filename)
    return sorted(json_files)

def load_json_files(directory, selected_files, trimestre=None):
    """Load selected JSON files, optionally filtered by trimester"""
    all_students = []
    
    for filename in selected_files:
        # Si se especifica un trimestre, solo cargar ese trimestre
        if trimestre and trimestre != filename:
            continue
            
        with open(os.path.join(directory, filename), 'r', encoding='utf-8') as f:
            students = json.load(f)
            # Filter out students with NULL IDs and add trimester info
            for student in students:
                if student['id'].upper() != "NULL" and student['id']:
                    # Use T1, T2, T3 as trimester
                    student['trimestre'] = filename.split('.')[0]  # Will be T1, T2, or T3
                    all_students.append(student)
    
    return all_students

def main():
    st.set_page_config(layout="wide")
    st.title("Sistema de Visualització de Notes")
    
    # Get current directory
    current_dir = os.getcwd()
    
    # Create a text input for the directory path
    working_dir = st.text_input(
        "Selecciona el directori que conté els fitxers JSON (T1.json, T2.json, T3.json)",
        value=current_dir
    )
    
    if not os.path.exists(working_dir):
        st.error("El directori no existeix")
        return
    
    # Get all JSON files in the selected directory
    json_files = get_json_files(working_dir)
    
    if not json_files:
        st.error(f"No s'han trobat fitxers JSON (T1.json, T2.json, T3.json) al directori '{working_dir}'")
        return
    
    # Create a multiselect for JSON files
    selected_files = st.multiselect(
        "Selecciona els fitxers JSON a visualitzar",
        json_files,
        default=json_files  # Select all files by default
    )
    
    if not selected_files:
        st.warning("Selecciona almenys un fitxer JSON per visualitzar")
        return
    
    # Display selected files
    st.subheader("Fitxers seleccionats:")
    for file in selected_files:
        st.write(f"📄 {file}")
    
    # Create options for trimester selector
    trimester_options = ["Tots"] + selected_files
    
    # Selector de trimestre
    trimestre = st.selectbox(
        "Selecciona el trimestre",
        trimester_options,
        index=0,  # Por defecto mostrar todos
        key="trimester_selector"
    )
    
    # Cargar estudiantes según el trimestre seleccionado
    if trimestre == "Tots":
        students = load_json_files(working_dir, selected_files)
    else:
        students = load_json_files(working_dir, [trimestre])
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["Grup", "Materia", "Alumne", "Evolució"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            display_group_statistics(students)
        with col2:
            group_failure_table(students)
            display_subjects_bar_chart(students)
            display_student_subject_heatmap(students)
        display_student_ranking(students)
    
    with tab2:
        # Display subject statistics
        display_subject_statistics(students)
    
    with tab3:    
        # Display student selector and get selected student data
        selected_student_data = display_student_selector(students)
        col1, col2 = st.columns(2)
        with col1:
            # Display student marks
            display_student_marks(selected_student_data)
        with col2:
            # Display pie chart of marks
            display_marks_pie_chart(selected_student_data)
        
    with tab4:
        # Load all trimesters for evolution comparison
        all_trimesters = load_json_files(working_dir, selected_files)
        display_evolution_dashboard(all_trimesters)

if __name__ == "__main__":
    main() 