import streamlit as st
import pandas as pd
from utils.comments_manager import render_comment_input, render_comment_display

def display_student_marks(selected_student_data, comments_manager=None):
    """Display student marks in a filtered and sorted table"""
    
    # Check if this is CSV data or JSON data
    is_csv_data = 'subjects' in selected_student_data
    
    if is_csv_data:
        # CSV format: subjects and pending_subjects
        # Display current level subjects (4t)
        st.subheader("Notes de 4t (Curs Actual)")
        
        if selected_student_data['subjects']:
            subjects_data = []
            for subject in selected_student_data['subjects']:
                subjects_data.append({
                    'Materia': subject['subject'],
                    'Qualificació': subject['qualification'],
                    'Comentari': subject['comment']
                })
            
            df = pd.DataFrame(subjects_data)
            df = df.sort_values('Materia')
            
            st.dataframe(
                df,
                column_config={
                    "Materia": st.column_config.TextColumn("Materia", width="medium"),
                    "Qualificació": st.column_config.TextColumn("Qualificació", width="small"),
                    "Comentari": st.column_config.TextColumn("Comentari", width="large")
                },
                hide_index=True,
                height=400
            )
        else:
            st.info("No hi ha matèries de 4t per mostrar")
        
        # Display pending subjects from previous years
        if selected_student_data.get('pending_subjects'):
            st.subheader("⚠️ Matèries Pendents (Cursos Anteriors)")
            
            pending_data = []
            for subject in selected_student_data['pending_subjects']:
                pending_data.append({
                    'Materia': subject['subject'],
                    'Qualificació': subject['qualification'],
                    'Comentari': subject['comment']
                })
            
            df_pending = pd.DataFrame(pending_data)
            df_pending = df_pending.sort_values('Materia')
            
            st.dataframe(
                df_pending,
                column_config={
                    "Materia": st.column_config.TextColumn("Materia", width="medium"),
                    "Qualificació": st.column_config.TextColumn("Qualificació", width="small"),
                    "Comentari": st.column_config.TextColumn("Comentari", width="large")
                },
                hide_index=True,
                height=200
            )
        
        # Display general comment
        # if selected_student_data.get('comentari_general'):
        #     st.subheader("📝 Comentari General")
        #     st.info(selected_student_data['comentari_general'])
        
        # Add comments functionality if available
        if comments_manager:
            student_id = selected_student_data.get('id', '')
            if student_id:
                st.subheader("💬 Comentaris Adicionals")
                
                # Display existing general comment
                render_comment_display(
                    comments_manager, 
                    "student", 
                    student_id, 
                    show_empty=False
                )
                
                # Input for new/edit general comment
                render_comment_input(
                    comments_manager,
                    "student",
                    student_id,
                    label="Comentari general de l'alumne",
                    key_suffix="general",
                    placeholder="Afegeix un comentari general sobre l'alumne..."
                )
    
    else:
        # JSON format: materies
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
        df = df.sort_values(by='Materia') # type: ignore
        
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
            height=400
        )
        
        # Add comments functionality if available
        if comments_manager:
            student_id = selected_student_data.get('id', '')
            if student_id:
                st.subheader("💬 Comentaris Adicionals")
                
                # Display existing general comment
                render_comment_display(
                    comments_manager, 
                    "student", 
                    student_id, 
                    show_empty=False
                )
                
                # Input for new/edit general comment
                render_comment_input(
                    comments_manager,
                    "student",
                    student_id,
                    label="Comentari general de l'alumne",
                    key_suffix="general_json",
                    placeholder="Afegeix un comentari general sobre l'alumne..."
                ) 