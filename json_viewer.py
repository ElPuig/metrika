import streamlit as st
import json
import os
from sections.student_marks import display_student_marks
from sections.student_selector import display_student_selector
from sections.visualization import display_marks_pie_chart, display_group_statistics, group_failure_table, display_subjects_bar_chart, display_student_ranking, display_student_subject_heatmap
from utils.constants import MarkConfig
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px

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
    st.set_page_config(layout="wide")
    st.title("Sistema de Visualització de Notes")
    
    # Load all students
    students = load_json_files()
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Grup", "Alumne"])
    
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
        # Display student selector and get selected student data
        selected_student_data = display_student_selector(students)
        col1, col2 = st.columns(2)
        with col1:
            # Display student marks
            display_student_marks(selected_student_data)
        with col2:
            # Display pie chart of marks
            display_marks_pie_chart(selected_student_data)

if __name__ == "__main__":
    main() 