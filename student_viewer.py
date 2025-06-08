import streamlit as st
import json
import os
import pandas as pd

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
    st.title("Sistema de Visualització d'Notes")
    
    # Load all students
    students = load_json_files()
    
    # Create a list of student names for the dropdown
    student_names = [f"{student['nom_cognoms']} ({student['id']})" for student in students]
    
    # Create the dropdown
    selected_student = st.selectbox(
        "Selecciona un alumne:",
        student_names,
        key="student_selector"
    )
    
    # Get the selected student's data
    student_id = selected_student.split("(")[-1].strip(")")
    selected_student_data = next(student for student in students if student['id'] == student_id)
    
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
        hide_index=True,
        key="subjects_table"
    )

if __name__ == "__main__":
    main() 