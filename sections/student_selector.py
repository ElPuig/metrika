import streamlit as st
from utils.data_normalizer import normalize_student_data
from utils.comments_manager import render_student_adaptation_toggle, render_adaptation_badge

def display_student_selector(students, comments_manager=None):
    """Display the student selector dropdown and return the selected student data"""
    # Create a list of student names for the dropdown
    student_names = [f"{student.get('nom_cognoms', student.get('nom', 'Unknown'))} ({student['id']})" for student in students]
    
    # Create the dropdown
    selected_student = st.selectbox(
        "Selecciona un alumne:",
        student_names,
        key="student_selector"
    )
    
    # Get the selected student's data
    student_id = selected_student.split("(")[-1].strip(")")
    selected_student_data = next(student for student in students if str(student['id']) == student_id)
    
    # Normalize the student data but keep original for display
    original_data = selected_student_data.copy()
    normalized_data = normalize_student_data(selected_student_data)
    
    # Display adaptation toggle if comments manager is available
    if comments_manager:
        st.markdown("---")
        render_student_adaptation_toggle(
            comments_manager,
            student_id,
            student_name=selected_student_data.get('nom_cognoms', selected_student_data.get('nom', 'Unknown')),
            key_suffix="selector"
        )
        st.markdown("---")
    
    # Calculate average grade
    mark_to_value = {
        "No assoliment": 2.5,
        "Assoliment satisfactori": 5,
        "Assoliment notable": 7.5,
        "Assoliment excel·lent": 10
    }
    
    # Get all evaluated subjects (excluding non-evaluated ones)
    evaluated_subjects = [
        subject for subject in normalized_data['materies']
        if subject['qualificacio'] in mark_to_value
    ]
    
    if evaluated_subjects:
        # Calculate average
        total_value = sum(mark_to_value[subject['qualificacio']] for subject in evaluated_subjects)
        average = total_value / len(evaluated_subjects)
                
        # Display average grade in a dashboard style
        st.subheader("Nota Mitjana")
        
        # Create three columns for the metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Nota Mitjana (0-10)",
                value=f"{average:.2f}",
                delta=None
            )
        
        with col2:
            # Calculate percentage of each grade
            grade_counts = {grade: 0 for grade in mark_to_value.keys()}
            for subject in evaluated_subjects:
                grade_counts[subject['qualificacio']] += 1
            
            # Find most common grade
            most_common = max(grade_counts.items(), key=lambda x: x[1])
            
            # Determine color based on most common grade
            delta_color = "inverse" if most_common[0] == "No assoliment" else "normal"
            
            st.metric(
                label="Qualificació més freqüent",
                value=most_common[0],
                delta=f"{most_common[1]} assignatures",
                delta_color=delta_color
            )
        
        with col3:
            # Calculate pass rate (AS, AN, AE)
            pass_count = sum(1 for subject in evaluated_subjects 
                           if subject['qualificacio'] in ["Assoliment satisfactori", 
                                                        "Assoliment notable", 
                                                        "Assoliment excel·lent"])
            pass_rate = (pass_count / len(evaluated_subjects)) * 100
            
            # Determine color based on most common grade
            delta_color = "inverse" if most_common[0] == "No assoliment" else "normal"
            
            st.metric(
                label="Taxa d'aprovat",
                value=f"{pass_rate:.1f}%",
                delta=f"{pass_count}/{len(evaluated_subjects)} assignatures",
                delta_color=delta_color
            )
    
    # Display general comment if available
    if 'comentari_general' in original_data and original_data['comentari_general']:
        st.subheader("Comentari General")
        st.write(original_data['comentari_general'])
    
    return original_data 