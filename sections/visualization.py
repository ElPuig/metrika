import streamlit as st
import pandas as pd
import numpy as np
from constants import DataConfig, MarkConfig
import plotly.express as px
import plotly.graph_objects as go


def show_classroom_table(data:pd.DataFrame, title:str=None):
    with st.expander(f"Tabla global clase ({title})"):
        st.dataframe(data, use_container_width=True)


def subject_visualization(data:pd.DataFrame, selected_subject:str, title:str):

    # Count the occurrences of each unique value in the selected column
    value_counts = data[selected_subject].value_counts()
    # Create a pie chart using Plotly with custom colors
    figGlobal = px.pie(
        value_counts, 
        names=value_counts.index, 
        values=value_counts.values, 
        title=title,
        color=value_counts.index,  # Use the index (unique values) for coloring
        color_discrete_map=MarkConfig.COLOR_MAP.value  # Map custom colors to values
    )
    
    # Display the pie chart
    st.plotly_chart(figGlobal)


def student_mark_freq_visualization(data:pd.DataFrame, std_name:str, title:str):
    # Display pie chart of marks count
    count_cols = [f"{x}_COUNT" for x in MarkConfig.LIST.value]
    student_data_count = data[data["NOM"] == std_name][count_cols].iloc[0]

    # Prepare data for Plotly
    plot_data = pd.DataFrame({
        'Nota': [label.replace('_COUNT', '') for label in count_cols],
        'Frecuencia': student_data_count.values
    })

    # Create interactive pie chart
    fig = px.pie(
        plot_data,
        values='Frecuencia',
        names='Nota',
        title=title,
        color='Nota',  # Use the index (unique values) for coloring
        color_discrete_map=MarkConfig.COLOR_MAP.value,
        hover_data=['Frecuencia'],
        # labels={'Frecuencia': 'Cantidad'}
    )
    
    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)


def student_marks_per_subject(data:pd.DataFrame, std_name:str, title:str):
    student_data = data[data["NOM"] == std_name]
    student_data = student_data[list(DataConfig.SUBJ_NAMES.value)]
    
    # Display bar diagram from selected student
    fig = go.Figure()
    # Preparar datos para Plotly
    columns = list(DataConfig.SUBJ_NAMES.value)
    values = list(student_data.iloc[0])
    colors = [MarkConfig.COLOR_MAP.value[val] for val in values]
    heights = [MarkConfig.HEIGHT_MAP.value[val] for val in values]
    
    # Set bar diagram content
    fig.add_trace(go.Bar(
        x=columns,
        y=heights,  # Usar alturas variables
        marker_color=colors,
        text=values,
        textposition='inside',
        textfont=dict(color='white', size=14),
        hoverinfo='text',
        hovertext=[f"Columna: {col}<br>Valor: {val}" for col, val in zip(columns, values)]
    ))

    # Personalizar diseño
    fig.update_layout(
        title=title,
        yaxis=dict(showticklabels=False, range=[0, 1.1]),
        height=300,
        showlegend=False,
        hovermode='closest',
        yaxis_autorange=True
    )
    
    # Display the bar chart
    st.plotly_chart(fig, use_container_width=True)


def show_student_evolution(data1:pd.DataFrame, data2:pd.DataFrame, student_name:str, title:str):
    """Muestra la evolución de las notas de un alumno específico entre trimestres.
    
    Args:
        data1 (pd.DataFrame): Datos del primer trimestre
        data2 (pd.DataFrame): Datos del segundo trimestre
        student_name (str): Nombre del alumno
        title (str): Título de la visualización
    """
    # Obtener las notas del primer trimestre
    t1_marks = data1[data1["NOM"] == student_name][list(DataConfig.SUBJ_NAMES.value)]
    t1_marks = t1_marks.replace(MarkConfig.HEIGHT_MAP.value)
    t1_avg = t1_marks.mean().mean()
    
    # Obtener las notas del segundo trimestre
    t2_marks = data2[data2["NOM"] == student_name][list(DataConfig.SUBJ_NAMES.value)]
    t2_marks = t2_marks.replace(MarkConfig.HEIGHT_MAP.value)
    t2_avg = t2_marks.mean().mean()
    
    # Crear DataFrame con la evolución por asignatura
    evolution_data = []
    for subject in DataConfig.SUBJ_NAMES.value:
        t1_subj = t1_marks[subject].iloc[0]
        t2_subj = t2_marks[subject].iloc[0]
        evolution_data.append({
            "Asignatura": DataConfig.get_key_from_value(subject),
            "Trimestre 1": t1_subj,
            "Trimestre 2": t2_subj,
            "Evolución": t2_subj - t1_subj
        })
    
    evolution_df = pd.DataFrame(evolution_data)
    
    # Crear el gráfico de dispersión con líneas
    fig = go.Figure()
    
    # Añadir puntos y líneas para cada asignatura
    for _, row in evolution_df.iterrows():
        color = "red" if row["Evolución"] < 0 else "green" if row["Evolución"] > 0 else "gray"
        fig.add_trace(go.Scatter(
            x=["Trimestre 1", "Trimestre 2"],
            y=[row["Trimestre 1"], row["Trimestre 2"]],
            mode='lines+markers',
            name=row["Asignatura"],
            line=dict(color=color),
            text=[f"{row['Asignatura']}<br>Nota: {MarkConfig.get_mark_from_height(y)}" for y in [row["Trimestre 1"], row["Trimestre 2"]]],
            hoverinfo='text'
        ))
    
    # Personalizar el diseño
    fig.update_layout(
        title=title,
        xaxis_title="Trimestre",
        yaxis_title="Nota",
        yaxis=dict(
            range=[0, 4.5],  # Rango basado en HEIGHT_MAP
            ticktext=["NA", "AS", "AN", "AE"],
            tickvals=[1, 2, 3, 4]
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
    
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)
    
    # Mostrar tabla con la evolución
    st.subheader("Resumen de Evolución por Asignatura")
    # Convertir los valores numéricos a notas en la tabla
    display_df = evolution_df.copy()
    display_df["Trimestre 1"] = display_df["Trimestre 1"].apply(lambda x: MarkConfig.get_mark_from_height(x))
    display_df["Trimestre 2"] = display_df["Trimestre 2"].apply(lambda x: MarkConfig.get_mark_from_height(x))
    st.dataframe(
        display_df.sort_values("Evolución", ascending=False),
        use_container_width=True
    )
    
    # Mostrar resumen general
    st.subheader("Resumen General")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Promedio T1", MarkConfig.get_mark_from_height(t1_avg))
    with col2:
        st.metric("Promedio T2", MarkConfig.get_mark_from_height(t2_avg))
    with col3:
        st.metric("Evolución", f"{t2_avg - t1_avg:+.2f}", delta=f"{t2_avg - t1_avg:+.2f}")