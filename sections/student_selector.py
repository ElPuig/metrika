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
    
    # Calculate average grade
    mark_to_value = {
        "No assoliment": 0,
        "Assoliment satisfactori": 1,
        "Assoliment notable": 2,
        "Assoliment excel·lent": 3
    }
    
    # Get all evaluated subjects (excluding non-evaluated ones)
    evaluated_subjects = [
        subject for subject in selected_student_data['materies']
        if subject['qualificacio'] in mark_to_value
    ]
    
    if evaluated_subjects:
        # Calculate average
        total_value = sum(mark_to_value[subject['qualificacio']] for subject in evaluated_subjects)
        average = total_value / len(evaluated_subjects)
        
        # Convert to 0-10 scale (multiply by 10/3 since original scale is 0-3)
        average_10 = average * (10/3)
        
        # Display average grade in a dashboard style
        st.subheader("Nota Mitjana")
        
        # Create three columns for the metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Nota Mitjana (0-10)",
                value=f"{average_10:.2f}",
                delta=None
            )
        
        with col2:
            # Calculate percentage of each grade
            grade_counts = {grade: 0 for grade in mark_to_value.keys()}
            for subject in evaluated_subjects:
                grade_counts[subject['qualificacio']] += 1
            
            # Find most common grade
            most_common = max(grade_counts.items(), key=lambda x: x[1])
            st.metric(
                label="Qualificació més freqüent",
                value=most_common[0],
                delta=f"{most_common[1]} assignatures"
            )
        
        with col3:
            # Calculate pass rate (AS, AN, AE)
            pass_count = sum(1 for subject in evaluated_subjects 
                           if subject['qualificacio'] in ["Assoliment satisfactori", 
                                                        "Assoliment notable", 
                                                        "Assoliment excel·lent"])
            pass_rate = (pass_count / len(evaluated_subjects)) * 100
            st.metric(
                label="Taxa d'aprovat",
                value=f"{pass_rate:.1f}%",
                delta=f"{pass_count}/{len(evaluated_subjects)} assignatures"
            )
    
    # Display general comment
    st.subheader("Comentari General")
    st.write(selected_student_data['comentari_general'])
    
    return selected_student_data 