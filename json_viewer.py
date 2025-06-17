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
from csv_converter import main as csv_converter_main
import logging

# logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_json_files(directory):
    """Get all JSON files in the directory"""
    json_files = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            json_files.append(filename)
    return sorted(json_files)

def load_json_files(directory, selected_files, trimestre=None):
    """Load selected JSON files, optionally filtered by trimester"""
    all_students = []
    file_info = {}  # Store file metadata for display
    
    for filename in selected_files:
        try:
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Check if it's the new structure (with grup, trimestre, estudiants)
                if isinstance(data, dict) and 'estudiants' in data:
                    # New structure
                    students = data['estudiants']
                    grup = data.get('grup', 'Grup desconegut')
                    trimestre_name = data.get('trimestre', 'Trimestre desconegut')
                    
                    # Create display name: grup_trimestre
                    display_name = f"{grup}_{trimestre_name}"
                    file_info[filename] = {
                        'display_name': display_name,
                        'grup': grup,
                        'trimestre': trimestre_name
                    }
                    
                    # Filter out students with NULL IDs and add trimester info
                    for student in students:
                        if student['id'].upper() != "NULL" and student['id']:
                            student['trimestre'] = trimestre_name
                            student['grup'] = grup
                            student['file_display_name'] = display_name
                            all_students.append(student)
                            
                elif isinstance(data, list):
                    # Old structure (direct array of students)
                    # Try to extract trimester from filename
                    trimestre_from_filename = filename.split('.')[0]  # Will be T1, T2, or T3
                    
                    display_name = f"Grup_Antic_{trimestre_from_filename}"
                    file_info[filename] = {
                        'display_name': display_name,
                        'grup': 'Grup Antic',
                        'trimestre': trimestre_from_filename
                    }
                    
                    # Filter out students with NULL IDs and add trimester info
                    for student in data:
                        if student['id'].upper() != "NULL" and student['id']:
                            student['trimestre'] = trimestre_from_filename
                            student['grup'] = 'Grup Antic'
                            student['file_display_name'] = display_name
                            all_students.append(student)
                else:
                    st.warning(f"Format de fitxer no reconegut per a {filename}")
                    continue
                    
        except Exception as e:
            st.error(f"Error carregant el fitxer {filename}: {str(e)}")
            continue
    
    return all_students, file_info

def main():
    st.set_page_config(layout="wide")
    
    # Sidebar menu
    menu = st.sidebar.selectbox(
        "Menú",
        ["Estadísticas", "Convertir CSV"]
    )
    
    if menu == "Estadísticas":
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
            st.error(f"No s'han trobat fitxers JSON al directori '{working_dir}'")
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
        
        # Load all files to get their metadata
        all_students, file_info = load_json_files(working_dir, selected_files)
        
        if not all_students:
            st.error("No s'han pogut carregar estudiants dels fitxers seleccionats")
            return
        
        # Display selected files with their display names
        st.subheader("Fitxers seleccionats:")
        for file in selected_files:
            if file in file_info:
                display_name = file_info[file]['display_name']
                grup = file_info[file]['grup']
                trimestre = file_info[file]['trimestre']
                st.write(f"📄 {file} → {display_name} (Grup: {grup}, Trimestre: {trimestre})")
            else:
                st.write(f"📄 {file}")
        
        # Create trimester selector based on available trimesters
        available_trimesters = []
        for file in selected_files:
            if file in file_info:
                available_trimesters.append(file)
        
        if not available_trimesters:
            st.error("No s'han trobat fitxers vàlids per seleccionar")
            return
        
        # Selector de trimestre
        trimestre = st.selectbox(
            "Selecciona el trimestre",
            available_trimesters,
            index=0,
            key="trimester_selector",
            format_func=lambda x: file_info[x]['display_name'] if x in file_info else x
        )
        
        # Cargar estudiantes según el trimestre seleccionado
        students, _ = load_json_files(working_dir, [trimestre])
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["Grup", "Materia", "Alumne", "Evolució"])
        
        with tab1:
            col1, col2 = st.columns(2)
            display_group_statistics(students)
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
            all_trimesters, _ = load_json_files(working_dir, selected_files)
            if len(all_trimesters) < 2:
                st.warning("Es necessiten almenys dos trimestres per visualitzar l'evolució")
            else:
                display_evolution_dashboard(all_trimesters)
    
    elif menu == "Convertir CSV":
        st.title("Convertir CSV")
        csv_converter_main()

if __name__ == "__main__":
    main() 