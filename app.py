import streamlit as st
import json
import os
import re
from collections import Counter
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
                'detected_trimestre': trimestre_name,
                'version': 'CSV',
                'nom_ensenyament': nom_ensenyament
            }
            
            # Add file info to each student
            for student in students:
                student['trimestre'] = trimestre_name
                student['grup'] = grup
                student['source_file'] = uploaded_file.name
                student['file_display_name'] = display_name
                all_students.append(student)
                
        except Exception as e:
            st.error(f"Error carregant el fitxer CSV {uploaded_file.name}: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            continue
    
    return all_students, file_info, version_warnings


def _extract_trimester_number(trimester_label):
    """Extract the trimester number from labels such as T1, T2, ..."""
    if not isinstance(trimester_label, str):
        return 999

    match = re.search(r'(\d+)', trimester_label)
    if not match:
        return 999

    return int(match.group(1))


def _render_trimester_label_selector(file_info, uploaded_files):
    """Allow the user to assign trimester labels (T1, T2, T3...) per uploaded file."""
    if len(file_info) <= 1:
        return

    st.subheader("Etiquetatge dels trimestres")
    st.caption(
        "Revisa o ajusta l'etiqueta de cada fitxer per assegurar la comparació correcta T1 → T2 → T3."
    )

    max_trimester_option = max(3, len(file_info) + 1)
    trimester_options = [f"T{i}" for i in range(1, max_trimester_option + 1)]

    for index, uploaded_file in enumerate(uploaded_files, start=1):
        if uploaded_file.name not in file_info:
            continue

        detected_trimester = file_info[uploaded_file.name].get('detected_trimestre', 'T1')
        detected_number = _extract_trimester_number(detected_trimester)

        if detected_number != 999 and f"T{detected_number}" in trimester_options:
            default_label = f"T{detected_number}"
        else:
            fallback_index = min(index - 1, len(trimester_options) - 1)
            default_label = trimester_options[fallback_index]

        default_index = trimester_options.index(default_label)
        selected_label = st.selectbox(
            f"Trimestre per {uploaded_file.name}",
            trimester_options,
            index=default_index,
            key=f"trimester_label_{uploaded_file.name}",
            help="Etiqueta manual del trimestre per aquest fitxer"
        )

        file_info[uploaded_file.name]['trimestre'] = selected_label
        file_info[uploaded_file.name]['display_name'] = (
            f"{file_info[uploaded_file.name]['grup']}_{selected_label}"
        )

    assigned_labels = [info.get('trimestre', '') for info in file_info.values()]
    duplicate_labels = sorted([label for label, count in Counter(assigned_labels).items() if count > 1])
    if duplicate_labels:
        st.warning(
            "Hi ha etiquetes de trimestre repetides "
            f"({', '.join(duplicate_labels)}). "
            "Per una comparació clara, assigna una etiqueta diferent a cada fitxer."
        )


def _apply_selected_trimester_labels(all_students, file_info):
    """Propagate selected trimester labels from file metadata into student records."""
    for student in all_students:
        source_file = student.get('source_file')
        if source_file not in file_info:
            continue

        student['trimestre'] = file_info[source_file].get('trimestre', student.get('trimestre', ''))
        student['grup'] = file_info[source_file].get('grup', student.get('grup', ''))
        student['file_display_name'] = file_info[source_file].get(
            'display_name',
            student.get('file_display_name', '')
        )

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

    # Allow manual trimester label assignment (T1/T2/T3...) when multiple files are uploaded
    _render_trimester_label_selector(file_info, uploaded_files)
    _apply_selected_trimester_labels(all_students, file_info)
    
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
            detected_trimestre = file_info[uploaded_file.name].get('detected_trimestre', trimestre)
            version = file_info[uploaded_file.name]['version']

            if detected_trimestre != trimestre:
                st.write(
                    f"📄 {uploaded_file.name} → {display_name} "
                    f"(Grup: {grup}, Trimestre: {trimestre}, Detectat: {detected_trimestre}, Versió: {version})"
                )
            else:
                st.write(
                    f"📄 {uploaded_file.name} → {display_name} "
                    f"(Grup: {grup}, Trimestre: {trimestre}, Versió: {version})"
                )
        else:
            st.write(f"📄 {uploaded_file.name}")
    
    # Create trimester selector based on available trimesters
    available_trimesters = []
    for uploaded_file in uploaded_files:
        if uploaded_file.name in file_info:
            available_trimesters.append(uploaded_file.name)

    available_trimesters = sorted(
        available_trimesters,
        key=lambda file_name: (
            _extract_trimester_number(file_info[file_name].get('trimestre', '')),
            file_name.lower()
        )
    )
    
    if not available_trimesters:
        st.error("No s'han trobat fitxers vàlids per seleccionar")
        return
    
    # Selector de trimestre
    trimestre = st.selectbox(
        "Selecciona el trimestre per a les vistes principals",
        available_trimesters,
        index=0,
        key="trimester_selector",
        format_func=lambda x: file_info[x]['display_name'] if x in file_info else x
    )
    
    # Load students for the selected trimester from the already-parsed dataset
    students = [student for student in all_students if student.get('source_file') == trimestre]
    if not students:
        st.error("No s'han trobat estudiants per al trimestre seleccionat")
        return
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["Grup", "Materia", "Alumne", "Comparador"])
    
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

    with tab4:
        display_evolution_dashboard(all_students, comments_manager=st.session_state.comments_manager)

if __name__ == "__main__":
    main() 