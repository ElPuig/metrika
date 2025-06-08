import streamlit as st
import pandas as pd

def display_student_marks(selected_student_data):
    """Display student marks in a filtered and sorted table"""
    # Create a DataFrame for the subjects
    subjects_data = []
    for subject in selected_student_data['materies']:
        subjects_data.append({
            'Materia': subject['materia'],
            'Qualificació': subject['qualificacio'],
            'Comentari': subject['comentari']
        })
    
    df = pd.DataFrame(subjects_data)
    
    # Add course level checkboxes
    st.subheader("Filtrar per Curs")
    col1, col2, col3 = st.columns(3)
    with col1:
        first_year = st.checkbox("1r", value=False)
    with col2:
        second_year = st.checkbox("2n", value=False)
    with col3:
        third_year = st.checkbox("3r", value=True)
    
    # Filter DataFrame based on selected checkboxes
    selected_courses = []
    if first_year:
        selected_courses.append("1r")
    if second_year:
        selected_courses.append("2n")
    if third_year:
        selected_courses.append("3r")
    
    if selected_courses:
        mask = df['Materia'].str.contains('|'.join(selected_courses), case=False, na=False)
        df = df[mask]
    
    # Sort subjects alphabetically
    df = df.sort_values('Materia')
    
    # Display the subjects table
    st.subheader("Notes per Materia")
    st.dataframe(
        df,
        column_config={
            "Materia": st.column_config.TextColumn("Materia", width="small"),
            "Qualificació": st.column_config.TextColumn("Qualificació", width="small"),
            "Comentari": st.column_config.TextColumn("Comentari", width="large")
        },
        hide_index=True,
        use_container_width=True,
        height=400
    ) 