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
            evolution_data.append({
                'trimestre': student['trimestre'],
                'nom': student['nom_cognoms'],
                'materia': materia['materia'],
                'qualificacio': materia['qualificacio']
            })
    
    df_evolution = pd.DataFrame(evolution_data)
    
    # Get unique subjects
    all_subjects = sorted(df_evolution['materia'].unique())
    
    # Create multi-select for subjects
    selected_subjects = st.multiselect(
        "Selecciona les materies a visualitzar",
        all_subjects,
        default=all_subjects
    )
    
    if not selected_subjects:
        st.warning("Selecciona almenys una materia per visualitzar")
        return
    
    # Filter data for selected subjects
    df_filtered = df_evolution[df_evolution['materia'].isin(selected_subjects)]
    
    # Create line plot for the selected subjects
    fig = px.line(
        df_filtered,
        x='trimestre',
        y='qualificacio',
        color='nom',
        markers=True,
        title='Evolució de les qualificacions per trimestre',
        labels={'trimestre': 'Trimestre', 'qualificacio': 'Qualificació'}
    )
    
    # Update layout to remove legend
    fig.update_layout(
        showlegend=False,
        yaxis=dict(
            range=[0, 10.5],
            tickvals=[2.5, 5, 7.5, 10],
            ticktext=['NA', 'AS', 'AN', 'AE']
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_evolution_dashboard(students):
    """Display evolution dashboard for comparing trimester grades"""
    st.subheader("Evolució de Notes per Trimestre")
    
    # Collect student data by trimester
    trimester_data = []
    
    # Mapeo de calificaciones a valores numéricos
    grade_map = {
        'No assoliment': 2.5,  # Suspenso
        'Assoliment satisfactori': 5.0,  # Aprobado Satisfactoriamente
        'Assoliment notable': 7.5,  # Aprobado Notablemente
        'Assoliment excel·lent': 10.0  # Aprobado Excelentemente
    }
    
    for student in students:
        if 'materies' in student:
            for materia in student['materies']:
                if 'materia' in materia and 'qualificacio' in materia and materia['qualificacio']:
                    # Convertir la calificación a valor numérico
                    valor = grade_map.get(materia['qualificacio'], 0)
                    trimester_data.append({
                        'Alumne': student['nom_cognoms'],
                        'Materia': materia['materia'],
                        'Trimestre': student['trimestre'],
                        'Valor': valor,
                        'Qualificacio': materia['qualificacio']
                    })
    
    if not trimester_data:
        st.warning("No hi ha dades disponibles per visualitzar l'evolució")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(trimester_data)
    
    # Check if we have at least two trimesters
    if len(df['Trimestre'].unique()) < 2:
        st.warning("Es necessiten almenys dos trimestres per visualitzar l'evolució")
        return
    
    # Visualization options
    st.subheader("Visualització de l'evolució")
    viz_type = st.radio(
        "Selecciona el tipus de visualització",
        ["Per Materia", "Per Alumne"]
    )
    
    if viz_type == "Per Materia":
        # Obtener lista única de materias
        materias = sorted(df['Materia'].unique())
        
        # Selector de materia
        materia_seleccionada = st.selectbox(
            "Selecciona una materia",
            materias
        )
        
        # Filtrar datos para la materia seleccionada
        df_materia = df[df['Materia'] == materia_seleccionada]
        
        # Create line plot for the selected subject
        fig = px.line(
            df_materia,
            x='Trimestre',
            y='Valor',
            color='Alumne',
            markers=True,
            title=f'Evolució de Notes de {materia_seleccionada}',
            labels={'Valor': 'Nota', 'Trimestre': 'Trimestre'}
        )
        
        # Update layout
        fig.update_layout(
            yaxis=dict(
                range=[0, 10.5],
                tickvals=[2.5, 5, 7, 10],
                ticktext=['NA', 'AS', 'AN', 'AE']
            ),
            showlegend=True,
            legend_title='Alumnes'
        )
        
    else:  # Per Alumne
        # Obtener lista única de alumnos
        alumnos = sorted(df['Alumne'].unique())
        
        # Selector de alumno
        alumno_seleccionado = st.selectbox(
            "Selecciona un alumne",
            alumnos
        )
        
        # Filtrar datos para el alumno seleccionado
        df_alumno = df[df['Alumne'] == alumno_seleccionado]
        
        # Create line plot for the selected student
        fig = px.line(
            df_alumno,
            x='Trimestre',
            y='Valor',
            color='Materia',
            markers=True,
            title=f'Evolució de Notes de {alumno_seleccionado}',
            labels={'Valor': 'Nota', 'Trimestre': 'Trimestre'}
        )
        
        # Update layout
        fig.update_layout(
            yaxis=dict(
                range=[0, 10.5],
                tickvals=[2.5, 5, 7, 10],
                ticktext=['NA', 'AS', 'AN', 'AE']
            ),
            showlegend=True,
            legend_title='Materies'
        )
    
    st.plotly_chart(fig, use_container_width=True) 