import streamlit as st

def display_student_selector(students):
    """Display the student selector dropdown and return the selected student data"""
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
    
    return selected_student_data 