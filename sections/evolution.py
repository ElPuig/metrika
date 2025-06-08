import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.constants import MarkConfig

def display_evolution_chart(students):
    """Muestra un gráfico de evolución de las notas por trimestre"""
    # Agrupar datos por trimestre y estudiante
    evolution_data = []
    for student in students:
        for materia in student['materies']:
            evolution_data.append({
                'id': student['id'],
                'nom': student['nom_cognoms'],
                'trimestre': student['trimestre'],
                'materia': materia['materia'],
                'qualificacio': materia['qualificacio']
            })
    
    df_evolution = pd.DataFrame(evolution_data)
    
    # Crear gráfico de evolución
    fig = px.line(df_evolution, 
                 x='trimestre', 
                 y='qualificacio',
                 color='materia',
                 title='Evolució de les qualificacions per trimestre',
                 labels={'trimestre': 'Trimestre', 'qualificacio': 'Qualificació'})
    
    st.plotly_chart(fig, use_container_width=True)

def display_student_evolution(students, selected_student):
    """Muestra la evolución de las notas de un estudiante específico"""
    # Filtrar datos del estudiante seleccionado
    student_data = [s for s in students if s['nom_cognoms'] == selected_student]
    
    if not student_data:
        st.warning("No se encontraron datos para el estudiante seleccionado")
        return
    
    # Preparar datos para el gráfico
    evolution_data = []
    for student in student_data:
        for materia in student['materies']:
            evolution_data.append({
                'trimestre': student['trimestre'],
                'materia': materia['materia'],
                'qualificacio': materia['qualificacio']
            })
    
    df_evolution = pd.DataFrame(evolution_data)
    
    # Crear gráfico de evolución
    fig = px.line(df_evolution, 
                 x='trimestre', 
                 y='qualificacio',
                 color='materia',
                 title=f'Evolució de les qualificacions de {selected_student}',
                 labels={'trimestre': 'Trimestre', 'qualificacio': 'Qualificació'})
    
    st.plotly_chart(fig, use_container_width=True)

def display_subject_evolution(students, selected_subject):
    """Muestra la evolución de las notas de una asignatura específica"""
    # Preparar datos para el gráfico
    evolution_data = []
    for student in students:
        for materia in student['materies']:
            if materia['materia'] == selected_subject:
                evolution_data.append({
                    'trimestre': student['trimestre'],
                    'nom': student['nom_cognoms'],
                    'qualificacio': materia['qualificacio']
                })
    
    df_evolution = pd.DataFrame(evolution_data)
    
    # Crear gráfico de evolución
    fig = px.line(df_evolution, 
                 x='trimestre', 
                 y='qualificacio',
                 color='nom',
                 title=f'Evolució de les qualificacions de {selected_subject}',
                 labels={'trimestre': 'Trimestre', 'qualificacio': 'Qualificació'})
    
    st.plotly_chart(fig, use_container_width=True)

def display_evolution_dashboard(students):
    """Muestra el dashboard completo de evolución"""
    st.subheader("Evolució de les notes")
    
    # Add course level checkboxes
    col1, col2, col3 = st.columns(3)
    with col1:
        first_year = st.checkbox("1r", value=False, key="evo_1r")
    with col2:
        second_year = st.checkbox("2n", value=False, key="evo_2n")
    with col3:
        third_year = st.checkbox("3r", value=True, key="evo_3r")

    selected_courses = []
    if first_year:
        selected_courses.append("1r")
    if second_year:
        selected_courses.append("2n")
    if third_year:
        selected_courses.append("3r")

    # Filter students based on selected courses
    filtered_students = []
    for student in students:
        filtered_materies = []
        for materia in student['materies']:
            if any(c in materia['materia'] for c in selected_courses):
                filtered_materies.append(materia)
        if filtered_materies:
            student_copy = student.copy()
            student_copy['materies'] = filtered_materies
            filtered_students.append(student_copy)
    
    # Selector de tipo de visualización
    viz_type = st.radio(
        "Selecciona el tipo de visualización",
        ["Evolució general", "Evolució per alumne", "Evolució per assignatura"]
    )
    
    if viz_type == "Evolució general":
        display_evolution_chart(filtered_students)
    
    elif viz_type == "Evolució per alumne":
        # Selector de estudiante
        student_names = list(set(s['nom_cognoms'] for s in filtered_students))
        selected_student = st.selectbox("Selecciona un alumne", student_names)
        display_student_evolution(filtered_students, selected_student)
    
    else:  # Evolució per assignatura
        # Obtener lista de asignaturas únicas
        subjects = set()
        for student in filtered_students:
            for materia in student['materies']:
                subjects.add(materia['materia'])
        
        selected_subject = st.selectbox("Selecciona una assignatura", sorted(list(subjects)))
        display_subject_evolution(filtered_students, selected_subject) 