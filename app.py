import streamlit as st
import json
import os
from sections.student_marks import display_student_marks
from sections.student_selector import display_student_selector
from sections.visualization import (
    display_marks_pie_chart, 
    display_group_statistics, 
    group_failure_table, 
    display_subjects_failure_ranking,
    display_subjects_bar_chart, 
    display_student_ranking, 
    display_student_subject_heatmap,
    display_subject_statistics
)
from sections.evolution import display_evolution_dashboard
from sections.acta_viewer import display_acta_viewer
from utils.constants import MarkConfig, AppConfig
from utils.acta_csv_loader import parse_uploaded_acta_csv, get_acta_csv_info
from utils.comments_manager import CommentsManager, get_session_id, render_comments_management_sidebar
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

def load_uploaded_csv_acta_files(uploaded_files):
    """Load uploaded CSV acta files"""
    all_students = []
    file_info = {}
    version_warnings = []
    
    for uploaded_file in uploaded_files:
        try:
            # Parse the CSV file
            students = parse_uploaded_acta_csv(uploaded_file)
            
            if not students:
                st.warning(f"No s'han trobat estudiants en el fitxer {uploaded_file.name}")
                continue
            
            # Get metadata from first student (all have same group info)
            grup = students[0].get('grup_codi', 'Unknown')
            trimestre_name = f"T{students[0].get('numero_avaluacio', 'X')}"
            nom_ensenyament = students[0].get('nom_ensenyament', 'Unknown')
            
            display_name = f"{grup}_{trimestre_name}"
            file_info[uploaded_file.name] = {
                'display_name': display_name,
                'grup': grup,
                'trimestre': trimestre_name,
                'version': 'CSV',
                'nom_ensenyament': nom_ensenyament
            }
            
            # Add file info to each student
            for student in students:
                student['trimestre'] = trimestre_name
                student['grup'] = grup
                student['file_display_name'] = display_name
                all_students.append(student)
                
        except Exception as e:
            st.error(f"Error carregant el fitxer CSV {uploaded_file.name}: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            continue
    
    return all_students, file_info, version_warnings

def main():
    st.set_page_config(
        page_title=f"{AppConfig.APP_NAME} - Sistema de Visualització de Notes",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize comments manager
    if 'comments_manager' not in st.session_state:
        st.session_state.comments_manager = CommentsManager()
    
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
    
    # Always show Estadísticas (menu removed)
    st.title("Sistema de Visualització de Notes")
    
    # Create a drag and drop file uploader for CSV files
    uploaded_files = st.file_uploader(
        "Arrossega els fitxers CSV d'actes aquí",
        type=['csv'],
        accept_multiple_files=True,
        help="Selecciona els fitxers CSV d'actes que vols visualitzar"
    )
    
    if not uploaded_files:
        st.warning("Arrossega almenys un fitxer CSV per visualitzar")
        return
    
    # Load all uploaded CSV files
    all_students, file_info, version_warnings = load_uploaded_csv_acta_files(uploaded_files)
    
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
    students, _, _ = load_uploaded_csv_acta_files([selected_file])
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Grup", "Materia", "Alumne"])
    
    # Add comments management to sidebar
    render_comments_management_sidebar(st.session_state.comments_manager)
    
    with tab1:
        col1, col2 = st.columns(2)
        display_group_statistics(students, comments_manager=st.session_state.comments_manager)
        group_failure_table(students)
        display_subjects_failure_ranking(students)
        display_subjects_bar_chart(students)
        display_student_subject_heatmap(students)
        display_student_ranking(students)
    
    with tab2:
        # Display subject statistics
        display_subject_statistics(students, comments_manager=st.session_state.comments_manager)
    
    with tab3:    
        # Display student selector and get selected student data
        selected_student_data = display_student_selector(students)
        # Display student marks (includes pie chart)
        display_student_marks(selected_student_data, comments_manager=st.session_state.comments_manager)

if __name__ == "__main__":
    main() 