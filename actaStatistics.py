import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import COL_NAMES, SUBJ_NAMES, select_folder
import os
import pathlib

# Load the CSV file
@st.cache_data
def load_data(input_file:str):
    data = pd.read_csv(input_file, delimiter=",", na_filter=False)
    return data



# current working directory
# print(f"Working from: {pathlib.Path().absolute()}")

# # List all files and directories in the current directory
# docs_path = os.path.join(pathlib.Path().absolute(), 'docs')
# # print(f"docs folder path: {docs_path}")

# with os.scandir('docs') as entries:
#     docs_files = [entry.name for entry in entries if entry.is_file()]

# Main function
def main():
    st.title("Esfera - Datos academicos")
    st.markdown("Este es un proyecto dedicado a gente que extrae información del tan tedioso Esfera. Va como va, ojala fuera mejor, pero la vida no es un lugar seguro. Así que: **tené paciencia nene**.")
    selected_folder_path = st.session_state.get("folder_path", None)
    folder_select_button = st.button("Selecciona carpeta")
    if folder_select_button:
        selected_folder_path = select_folder()
        st.session_state.folder_path = selected_folder_path

    if selected_folder_path:
        st.write("Selected folder path:", selected_folder_path)

    with os.scandir(selected_folder_path) as entries:
        docs_files = [entry.name for entry in entries if entry.is_file()]

    selected_file = st.selectbox(
    "Selecciona el archivo CSV",
        docs_files,
    )
    

    # Load the data
    data = load_data(os.path.join(selected_folder_path, selected_file))
    
    # Define the columns to visualize
    materias_options = COL_NAMES.values()
    
    # Define custom colors for each unique value
    color_map = {
        "NA": "#d62728",  # Red
        "AS": "#ff7f0e",  # Orange
        "AN": "#1f77b4",  # Blue
        "AE": "#2ca02c",  # Green
        "": "gray",
        pd.NA: "gray"
    }
    # Asignar pesos/alturas a cada categoría
    height_map = {'NA': 1, 'AS': 2, 'AN': 3, 'AE': 4, pd.NA: 0, '': 0}  # Ejemplo de valores
    
    # Add a dropdown to select the column
    selected_materia = st.selectbox(key="sb1", label="Selecciona materia", options=materias_options)
    
    # Display the selected column
    st.write(f"### Materia seleccionada: {selected_materia}")
    
    # Count the occurrences of each unique value in the selected column
    value_counts = data[selected_materia].value_counts()
    
    # Create a pie chart using Plotly with custom colors
    figGlobal = px.pie(
        value_counts, 
        names=value_counts.index, 
        values=value_counts.values, 
        title=f"Dstribucion de {selected_materia}",
        color=value_counts.index,  # Use the index (unique values) for coloring
        color_discrete_map=color_map  # Map custom colors to values
    )
    
    # Display the pie chart
    st.plotly_chart(figGlobal)

    # Add a dropdown to select a student by name
    student_names = data["NOM"].unique()  # Get unique student names
    selected_student = st.selectbox("Selecciona estudiante", student_names)
    
    # 1. Filtrar por estudiante
    student_data = data[data["NOM"] == selected_student].copy()

    # 2. Lista de columnas a EXCLUIR (si aparecieran en SUBJ_NAMES)
    EXCLUDE_COLS = {'id', 'NOM'}  # Usamos conjunto para búsqueda rápida

    # 3. Filtrar columnas: 
    # - Que estén en SUBJ_NAMES 
    # - Y NO estén en EXCLUDE_COLS
    subject_cols = [col for col in SUBJ_NAMES 
                if col in student_data.columns 
                and col not in EXCLUDE_COLS]

    # 4. Seleccionar solo las columnas de asignaturas
    student_data = student_data[subject_cols]
    
    # Display the selected student's data in a table
    st.write(f"### Datos de {selected_student}")
    st.dataframe(student_data)

    # Display graphics from selected student
    # Crear gráfico interactivo
    fig = go.Figure()
    # Preparar datos para Plotly
    columns = student_data.columns.tolist()
    values = student_data.iloc[0].tolist()
    colors = [color_map[val] for val in values]
    heights = [height_map[val] for val in values]  # Obtener alturas

    fig.add_trace(go.Bar(
        x=student_data.columns.tolist(),
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

    fig.update_traces(
        texttemplate='%{text}',
        hovertemplate='<b>%{x}</b><br>Valor: %{text}<extra></extra>'
    )
    # Display the pie chart
    st.plotly_chart(fig, use_container_width=True)

# Run the app
if __name__ == "__main__":
    main()