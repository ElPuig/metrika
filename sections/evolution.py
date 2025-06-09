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
    """Muestra el dashboard de evolución comparando trimestres para asignaturas de 3r"""
    st.subheader("Evolució de les notes entre trimestres (3r)")
    
    # Agrupar estudiantes por trimestre
    trimesters = {}
    for student in students:
        trimester = student['trimestre']
        if trimester not in trimesters:
            trimesters[trimester] = []
        trimesters[trimester].append(student)
    
    # Verificar que tenemos datos de al menos dos trimestres
    if len(trimesters) < 2:
        st.warning("Es necessiten dades d'almenys dos trimestres per veure l'evolució")
        return
    
    # Obtener lista de asignaturas de 3r
    third_year_subjects = set()
    for student in students:
        for materia in student['materies']:
            if "3r" in materia['materia']:
                third_year_subjects.add(materia['materia'])
    
    if not third_year_subjects:
        st.warning("No s'han trobat assignatures de 3r")
        return
    
    # Selector de tipo de visualización
    viz_type = st.radio(
        "Selecciona el tipus de visualització",
        ["Evolució per assignatura", "Evolució per alumne"],
        key="evolution_type"
    )
    
    if viz_type == "Evolució per assignatura":
        # Selector de asignatura
        selected_subject = st.selectbox(
            "Selecciona una assignatura",
            sorted(list(third_year_subjects)),
            key="evolution_subject"
        )
        
        # Preparar datos para el gráfico
        evolution_data = []
        for trimester, trimester_students in trimesters.items():
            for student in trimester_students:
                for materia in student['materies']:
                    if materia['materia'] == selected_subject:
                        evolution_data.append({
                            'Trimestre': trimester,
                            'Alumne': student['nom_cognoms'],
                            'Qualificació': materia['qualificacio']
                        })
        
        df = pd.DataFrame(evolution_data)
        
        # Convertir calificaciones a valores numéricos para el gráfico
        mark_to_value = {
            MarkConfig.NA.value: 2.5,  # NA = 2.5
            MarkConfig.AS.value: 5.0,  # AS = 5.0
            MarkConfig.AN.value: 7.0,  # AN = 7.0
            MarkConfig.AE.value: 10.0  # AE = 10.0
        }
        df['Valor'] = df['Qualificació'].map(mark_to_value)
        
        # Crear gráfico de evolución
        fig = go.Figure()
        
        # Añadir líneas para cada estudiante
        for student in df['Alumne'].unique():
            student_data = df[df['Alumne'] == student]
            fig.add_trace(go.Scatter(
                x=student_data['Trimestre'],
                y=student_data['Valor'],
                mode='lines+markers',
                name=student,
                text=[f"{row['Alumne']}<br>Nota: {row['Qualificació']}" for _, row in student_data.iterrows()],
                hoverinfo='text'
            ))
        
        # Personalizar diseño
        fig.update_layout(
            title=f"Evolució de {selected_subject} per trimestre",
            xaxis_title="Trimestre",
            yaxis_title="Qualificació",
            yaxis=dict(
                range=[0, 10.5],
                ticktext=["NA", "AS", "AN", "AE"],
                tickvals=[2.5, 5.0, 7.0, 10.0]
            ),
            height=600,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Mostrar tabla de evolución
        st.subheader("Taula d'evolució")
        pivot_df = df.pivot(index='Alumne', columns='Trimestre', values='Qualificació')
        st.dataframe(pivot_df, use_container_width=True)
        
    else:  # Evolució per alumne
        # Selector de estudiante
        student_names = list(set(s['nom_cognoms'] for s in students))
        selected_student = st.selectbox(
            "Selecciona un alumne", 
            sorted(student_names),
            key="evolution_student"
        )
        
        # Preparar datos para el gráfico
        evolution_data = []
        for trimester, trimester_students in trimesters.items():
            student_data = next((s for s in trimester_students if s['nom_cognoms'] == selected_student), None)
            if student_data:
                for materia in student_data['materies']:
                    if "3r" in materia['materia']:
                        evolution_data.append({
                            'Trimestre': trimester,
                            'Assignatura': materia['materia'],
                            'Qualificació': materia['qualificacio']
                        })
        
        df = pd.DataFrame(evolution_data)
        
        # Convertir calificaciones a valores numéricos para el gráfico
        mark_to_value = {
            MarkConfig.NA.value: 2.5,  # NA = 2.5
            MarkConfig.AS.value: 5.0,  # AS = 5.0
            MarkConfig.AN.value: 7.0,  # AN = 7.0
            MarkConfig.AE.value: 10.0  # AE = 10.0
        }
        df['Valor'] = df['Qualificació'].map(mark_to_value)
        
        # Mostrar resumen de evolución al principio
        st.subheader("Resum d'evolució")
        
        # Calcular promedio por trimestre
        trimester_avgs = df.groupby('Trimestre')['Valor'].mean()
        
        # Mostrar métricas con indicadores de evolución
        col1, col2, col3 = st.columns(3)
        with col1:
            if 'T1' in trimester_avgs:
                avg_value = trimester_avgs['T1']
                st.metric("Promig T1", f"{avg_value:.1f}")
            else:
                st.metric("Promig T1", "No disponible")
        with col2:
            if 'T2' in trimester_avgs:
                avg_value = trimester_avgs['T2']
                delta = avg_value - trimester_avgs.get('T1', avg_value)
                st.metric("Promig T2", f"{avg_value:.1f}", delta=f"{delta:+.1f}")
            else:
                st.metric("Promig T2", "No disponible")
        with col3:
            if 'T3' in trimester_avgs:
                avg_value = trimester_avgs['T3']
                delta = avg_value - trimester_avgs.get('T2', avg_value)
                st.metric("Promig T3", f"{avg_value:.1f}", delta=f"{delta:+.1f}")
            else:
                st.metric("Promig T3", "No disponible")
        
        # Crear gráfico de evolución
        fig = go.Figure()
        
        # Añadir líneas para cada asignatura
        for subject in df['Assignatura'].unique():
            subject_data = df[df['Assignatura'] == subject]
            fig.add_trace(go.Scatter(
                x=subject_data['Trimestre'],
                y=subject_data['Valor'],
                mode='lines+markers',
                name=subject,
                text=[f"{row['Assignatura']}<br>Nota: {row['Qualificació']}" for _, row in subject_data.iterrows()],
                hoverinfo='text'
            ))
        
        # Personalizar diseño
        fig.update_layout(
            title=f"Evolució de les notes de {selected_student} per trimestre",
            xaxis_title="Trimestre",
            yaxis_title="Qualificació",
            yaxis=dict(
                range=[0, 10.5],
                ticktext=["NA", "AS", "AN", "AE"],
                tickvals=[2.5, 5.0, 7.0, 10.0]
            ),
            height=600,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Mostrar tabla de evolución
        st.subheader("Taula d'evolució")
        pivot_df = df.pivot(index='Assignatura', columns='Trimestre', values='Qualificació')
        st.dataframe(pivot_df, use_container_width=True)
        
        # Mostrar resumen de evolución
        st.subheader("Resum d'evolució")
        
        # Calcular promedio por trimestre
        trimester_avgs = df.groupby('Trimestre')['Valor'].mean()
        
        # Mostrar métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            if 'T1' in trimester_avgs:
                avg_value = trimester_avgs['T1']
                st.metric("Promig T1", f"{avg_value:.1f}")
            else:
                st.metric("Promig T1", "No disponible")
        with col2:
            if 'T2' in trimester_avgs:
                avg_value = trimester_avgs['T2']
                st.metric("Promig T2", f"{avg_value:.1f}")
            else:
                st.metric("Promig T2", "No disponible")
        with col3:
            if 'T3' in trimester_avgs:
                avg_value = trimester_avgs['T3']
                st.metric("Promig T3", f"{avg_value:.1f}")
            else:
                st.metric("Promig T3", "No disponible") 