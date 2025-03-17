import streamlit as st
import pandas as pd
import plotly.express as px

# Load the CSV file
@st.cache_data
def load_data(input_file:str):
    data = pd.read_csv(input_file, delimiter=",", na_filter=False)
    return data

# Main function
def main():
    st.title("Pie Chart Visualization with Custom Colors")
    
    
    # Add a dropdown to select the column
    file_options=["docs/3b_t1_acta-avaluació.csv", "docs/3b_t2_acta-avaluació.csv"]
    selected_file = st.selectbox(key="sbSelectFile", label="Selecciona archivo", options=file_options)
    

    # Load the data
    data = load_data(selected_file)
    
    # Define the columns to visualize
    materias_options = [
        "Ll. Cat.",
        "Ll. Cast.",
        "Ll. Estr.",
        "Mat.",
        "BG",
        "FQ",
        "TD",
        "CS:GH",
        "Mús.",
        "Ed. Fís.",
        "Optativa",
        "PG_I",
        "PG_II",
        "comp pers"
    ]
    
    # Define custom colors for each unique value
    custom_colors = {
        "AS": "#1f77b4",  # Blue
        "AN": "#ff7f0e",  # Orange
        "AE": "#2ca02c",  # Green
        "NA": "#d62728",  # Red
        "N": "#9467bd",   # Purple
        "OP3": "#8c564b", # Brown
        "CL3": "#e377c2", # Pink
        "RP3": "#7f7f7f", # Gray
        "SF3": "#bcbd22", # Yellow-green
        "P13": "#17becf", # Cyan
        "P23": "#1a55FF", # Custom blue
    }
    
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
        color_discrete_map=custom_colors  # Map custom colors to values
    )
    
    # Display the pie chart
    st.plotly_chart(figGlobal)

    # Add a dropdown to select a student by name
    student_names = data["noms"].unique()  # Get unique student names
    selected_student = st.selectbox("Selecciona estudiante", student_names)
    
    # Filter data for the selected student
    student_data = data[data["noms"] == selected_student]
    
    # Display the selected student's data in a table
    st.write(f"### Datos de {selected_student}")
    st.dataframe(student_data[materias_options])
    
    # Count the occurrences of each unique value in the selected column for the student
    value_counts = student_data[selected_student].value_counts()
    
    # Create a pie chart using Plotly with custom colors
    figStudent = px.pie(
        value_counts, 
        names=value_counts.index, 
        values=value_counts.values, 
        title=f"Dsitribución de {selected_materia} para {selected_student}",
        color=value_counts.index,  # Use the index (unique values) for coloring
        color_discrete_map=custom_colors  # Map custom colors to values
    )
    
    # Display the pie chart
    st.plotly_chart(figStudent)

# Run the app
if __name__ == "__main__":
    main()