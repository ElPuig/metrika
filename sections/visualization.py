import streamlit as st
import pandas as pd
import numpy as np
from constants import DataConfig, MarkConfig
import plotly.express as px
import plotly.graph_objects as go


def show_classroom_stats(data:pd.DataFrame):
    with st.expander("Visualización global de la clase (tabla)"):
        st.dataframe(data, use_container_width=True)


def subject_visualization(data:pd.DataFrame):
    st.subheader("Estadísticas por materia")
    # Add a dropdown to select the column
    selected_subject = st.selectbox(key="sb_subject", label="Selecciona materia", options=DataConfig.SUBJ_NAMES.value)
    # Display the selected subject
    st.write(f"### Materia seleccionada: {selected_subject}")

    # Count the occurrences of each unique value in the selected column
    value_counts = data[selected_subject].value_counts()
    # Create a pie chart using Plotly with custom colors
    figGlobal = px.pie(
        value_counts, 
        names=value_counts.index, 
        values=value_counts.values, 
        title=f"Dstribucion de {selected_subject}",
        color=value_counts.index,  # Use the index (unique values) for coloring
        color_discrete_map=MarkConfig.COLOR_MAP.value  # Map custom colors to values
    )
    
    # Display the pie chart
    st.plotly_chart(figGlobal)


def student_mark_freq_visualization(data:pd.DataFrame, std_name:str):
    st.subheader("Estadísticas por alumno")
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
        title=f'Distribución de notas para {std_name}',
        color='Nota',  # Use the index (unique values) for coloring
        color_discrete_map=MarkConfig.COLOR_MAP.value,
        hover_data=['Frecuencia'],
        # labels={'Frecuencia': 'Cantidad'}
    )
    
    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)


def student_marks_per_subject(data:pd.DataFrame, std_name:str):
    st.subheader("Diagrama de barras: notas por materia")
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
        title='Representación de valores por columna',
        yaxis=dict(showticklabels=False, range=[0, 1.1]),
        height=300,
        showlegend=False,
        hovermode='closest',
        yaxis_autorange=True
    )
    
    # Display the bar chart
    st.plotly_chart(fig, use_container_width=True)
