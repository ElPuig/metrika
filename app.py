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
from utils.constants import MarkConfig, AppConfig
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from csv_converter import main as csv_converter_main
import logging

# logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def compare_versions(version1, version2):
    """Compare two semantic versions and return -1, 0, or 1"""
    def version_to_tuple(version):
        return tuple(map(int, version.split('.')))
    
    v1_tuple = version_to_tuple(version1)
    v2_tuple = version_to_tuple(version2)
    
    if v1_tuple < v2_tuple:
        return -1
    elif v1_tuple > v2_tuple:
        return 1
    else:
        return 0

def get_json_files(directory):
    """Get all JSON files in the directory (kept for compatibility with other modules)"""
    json_files = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            json_files.append(filename)
    return sorted(json_files)

def load_json_files(directory, selected_files, trimestre=None):
    """Load selected JSON files, optionally filtered by trimester (kept for compatibility with other modules)"""
    all_students = []
    file_info = {}  # Store file metadata for display
    version_warnings = []  # Store version compatibility warnings
    
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
                    file_version = data.get('metrika_version', '0.0.0')
                    
                    # Check version compatibility
                    if compare_versions(file_version, AppConfig.MIN_COMPATIBLE_VERSION) < 0:
                        version_warnings.append(f"⚠️ {filename}: Versió {file_version} és anterior a la versió mínima compatible ({AppConfig.MIN_COMPATIBLE_VERSION})")
                    elif compare_versions(file_version, AppConfig.VERSION) > 0:
                        version_warnings.append(f"⚠️ {filename}: Versió {file_version} és posterior a la versió actual ({AppConfig.VERSION})")
                    
                    # Create display name: grup_trimestre
                    display_name = f"{grup}_{trimestre_name}"
                    file_info[filename] = {
                        'display_name': display_name,
                        'grup': grup,
                        'trimestre': trimestre_name,
                        'version': file_version
                    }
                    
                    # Filter out students with NULL IDs and add trimester info
                    for student in students:
                        # Ensure ID is always a string
                        student['id'] = str(student['id'])
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
                        'trimestre': trimestre_from_filename,
                        'version': '0.0.0'  # Old files don't have version
                    }
                    
                    # Add warning for old format
                    version_warnings.append(f"⚠️ {filename}: Format antic sense informació de versió")
                    
                    # Filter out students with NULL IDs and add trimester info
                    for student in data:
                        # Ensure ID is always a string
                        student['id'] = str(student['id'])
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
    
    return all_students, file_info, version_warnings

def load_uploaded_json_files(uploaded_files, trimestre=None):
    """Load uploaded JSON files, optionally filtered by trimester"""
    all_students = []
    file_info = {}  # Store file metadata for display
    version_warnings = []  # Store version compatibility warnings
    
    for uploaded_file in uploaded_files:
        try:
            # Read the uploaded file content and decode it
            uploaded_file.seek(0)  # Reset file pointer to beginning
            file_content = uploaded_file.read()
            data = json.loads(file_content.decode('utf-8'))
            
            # Check if it's the new structure (with grup, trimestre, estudiants)
            if isinstance(data, dict) and 'estudiants' in data:
                # New structure
                students = data['estudiants']
                grup = data.get('grup', 'Grup desconegut')
                trimestre_name = data.get('trimestre', 'Trimestre desconegut')
                file_version = data.get('metrika_version', '0.0.0')
                
                # Check version compatibility
                if compare_versions(file_version, AppConfig.MIN_COMPATIBLE_VERSION) < 0:
                    version_warnings.append(f"⚠️ {uploaded_file.name}: Versió {file_version} és anterior a la versió mínima compatible ({AppConfig.MIN_COMPATIBLE_VERSION})")
                elif compare_versions(file_version, AppConfig.VERSION) > 0:
                    version_warnings.append(f"⚠️ {uploaded_file.name}: Versió {file_version} és posterior a la versió actual ({AppConfig.VERSION})")
                
                # Create display name: grup_trimestre
                display_name = f"{grup}_{trimestre_name}"
                file_info[uploaded_file.name] = {
                    'display_name': display_name,
                    'grup': grup,
                    'trimestre': trimestre_name,
                    'version': file_version
                }
                
                # Filter out students with NULL IDs and add trimester info
                for student in students:
                    # Ensure ID is always a string
                    student['id'] = str(student['id'])
                    if student['id'].upper() != "NULL" and student['id']:
                        student['trimestre'] = trimestre_name
                        student['grup'] = grup
                        student['file_display_name'] = display_name
                        all_students.append(student)
                        
            elif isinstance(data, list):
                # Old structure (direct array of students)
                # Try to extract trimester from filename
                trimestre_from_filename = uploaded_file.name.split('.')[0]  # Will be T1, T2, or T3
                
                display_name = f"Grup_Antic_{trimestre_from_filename}"
                file_info[uploaded_file.name] = {
                    'display_name': display_name,
                    'grup': 'Grup Antic',
                    'trimestre': trimestre_from_filename,
                    'version': '0.0.0'  # Old files don't have version
                }
                
                # Add warning for old format
                version_warnings.append(f"⚠️ {uploaded_file.name}: Format antic sense informació de versió")
                
                # Filter out students with NULL IDs and add trimester info
                for student in data:
                    # Ensure ID is always a string
                    student['id'] = str(student['id'])
                    if student['id'].upper() != "NULL" and student['id']:
                        student['trimestre'] = trimestre_from_filename
                        student['grup'] = 'Grup Antic'
                        student['file_display_name'] = display_name
                        all_students.append(student)
            else:
                st.warning(f"Format de fitxer no reconegut per a {uploaded_file.name}")
                continue
                
        except Exception as e:
            st.error(f"Error carregant el fitxer {uploaded_file.name}: {str(e)}")
            continue
    
    return all_students, file_info, version_warnings

def main():
    st.set_page_config(
        page_title=f"{AppConfig.APP_NAME} - Sistema de Visualització de Notes",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Sidebar with version information
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📊 Informació de l'aplicació")
        
        # Version info with icon
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown("ℹ️")
        with col2:
            st.markdown(f"**Versió:** {AppConfig.VERSION}")
            st.markdown(f"**Nom:** {AppConfig.APP_NAME}")
        
        st.markdown("---")
    
    # Sidebar menu
    menu = st.sidebar.selectbox(
        "Menú",
        ["Estadísticas", "Convertir CSV"]
    )
    
    if menu == "Estadísticas":
        st.title("Sistema de Visualització de Notes")
        
        # Create a drag and drop file uploader for JSON files
        uploaded_files = st.file_uploader(
            "Arrossega els fitxers JSON aquí (T1.json, T2.json, T3.json)",
            type=['json'],
            accept_multiple_files=True,
            help="Selecciona els fitxers JSON que vols visualitzar"
        )
        
        if not uploaded_files:
            st.warning("Arrossega almenys un fitxer JSON per visualitzar")
            return
        
        # Load all uploaded files to get their metadata
        all_students, file_info, version_warnings = load_uploaded_json_files(uploaded_files)
        
        if not all_students:
            st.error("No s'han pogut carregar estudiants dels fitxers seleccionats")
            return
        
        # Show version compatibility warnings
        if version_warnings:
            st.warning("**Advertències de compatibilitat de versions:**")
            for warning in version_warnings:
                st.markdown(f"• {warning}")
            st.markdown("---")
        
        # Display selected files with their display names
        st.subheader("Fitxers seleccionats:")
        for uploaded_file in uploaded_files:
            if uploaded_file.name in file_info:
                display_name = file_info[uploaded_file.name]['display_name']
                grup = file_info[uploaded_file.name]['grup']
                trimestre = file_info[uploaded_file.name]['trimestre']
                version = file_info[uploaded_file.name]['version']
                st.write(f"📄 {uploaded_file.name} → {display_name} (Grup: {grup}, Trimestre: {trimestre}, Versió: {version})")
            else:
                st.write(f"📄 {uploaded_file.name}")
        
        # Create trimester selector based on available trimesters
        available_trimesters = []
        for uploaded_file in uploaded_files:
            if uploaded_file.name in file_info:
                available_trimesters.append(uploaded_file.name)
        
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
        selected_file = next(f for f in uploaded_files if f.name == trimestre)
        students, _, _ = load_uploaded_json_files([selected_file])
        
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
            all_trimesters, _, _ = load_uploaded_json_files(uploaded_files)
            if len(all_trimesters) < 2:
                st.warning("Es necessiten almenys dos trimestres per visualitzar l'evolució")
            else:
                display_evolution_dashboard(all_trimesters)
    
    elif menu == "Convertir CSV":
        st.title("Convertir CSV")
        csv_converter_main()

if __name__ == "__main__":
    main() 