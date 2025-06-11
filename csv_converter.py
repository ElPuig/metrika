import streamlit as st
import os
from utils.csv_to_json import process_csv_to_json
import tempfile
import shutil

def main():
    st.set_page_config(layout="wide")
    st.title("Conversor CSV a JSON")
    
    # Create two columns for the layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Opció 1: Seleccionar directori")
        # Get current directory
        current_dir = os.getcwd()
        
        # Create a text input for the directory path
        working_dir = st.text_input(
            "Selecciona el directori que conté els fitxers CSV",
            value=current_dir
        )
        
        if st.button("Convertir fitxers del directori"):
            if os.path.exists(working_dir):
                try:
                    # Find all CSV files in the directory
                    csv_files = [f for f in os.listdir(working_dir) if f.endswith('.csv')]
                    
                    if not csv_files:
                        st.warning("No s'han trobat fitxers CSV al directori seleccionat")
                        return
                    
                    # Create a progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Process each CSV file
                    for i, csv_file in enumerate(csv_files):
                        # Update progress
                        progress = (i + 1) / len(csv_files)
                        progress_bar.progress(progress)
                        status_text.text(f"Processant {csv_file}...")
                        
                        # Get trimester from filename (assuming format like T1.csv, T2.csv, etc.)
                        trimestre = os.path.splitext(csv_file)[0]
                        
                        # Define input and output paths
                        input_csv = os.path.join(working_dir, csv_file)
                        output_json = os.path.join(working_dir, f"{trimestre}.json")
                        
                        try:
                            # Convert CSV to JSON
                            process_csv_to_json(input_csv, output_json, trimestre)
                        except Exception as e:
                            st.error(f"Error processant {csv_file}: {str(e)}")
                            continue
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.success("Conversió completada amb èxit!")
                    
                    # Show the list of converted files
                    st.subheader("Fitxers convertits:")
                    for csv_file in csv_files:
                        json_file = os.path.splitext(csv_file)[0] + ".json"
                        st.write(f"✅ {csv_file} → {json_file}")
                    
                except Exception as e:
                    st.error(f"Error accedint al directori: {str(e)}")
            else:
                st.error("El directori no existeix")
    
    with col2:
        st.subheader("Opció 2: Arrossegar i deixar anar fitxers")
        
        # Add destination directory selection
        dest_dir = st.text_input(
            "Selecciona el directori on es troben els fitxers CSV originals",
            value=current_dir
        )
        
        uploaded_files = st.file_uploader(
            "Arrossega els fitxers CSV aquí",
            type=['csv'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if st.button("Convertir fitxers pujats"):
                if not os.path.exists(dest_dir):
                    st.error("El directori de destinació no existeix")
                    return
                    
                # Create a temporary directory to store the uploaded files
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Save uploaded files to temporary directory
                    for uploaded_file in uploaded_files:
                        file_path = os.path.join(temp_dir, uploaded_file.name)
                        with open(file_path, 'wb') as f:
                            f.write(uploaded_file.getbuffer())
                    
                    # Create a progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Process each uploaded file
                    for i, uploaded_file in enumerate(uploaded_files):
                        # Update progress
                        progress = (i + 1) / len(uploaded_files)
                        progress_bar.progress(progress)
                        status_text.text(f"Processant {uploaded_file.name}...")
                        
                        # Get trimester from filename
                        trimestre = os.path.splitext(uploaded_file.name)[0]
                        
                        # Define input and output paths
                        input_csv = os.path.join(temp_dir, uploaded_file.name)
                        output_json = os.path.join(dest_dir, f"{trimestre}.json")
                        
                        try:
                            # Convert CSV to JSON
                            process_csv_to_json(input_csv, output_json, trimestre)
                        except Exception as e:
                            st.error(f"Error processant {uploaded_file.name}: {str(e)}")
                            continue
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.success("Conversió completada amb èxit!")
                    
                    # Show the list of converted files
                    st.subheader("Fitxers convertits:")
                    for uploaded_file in uploaded_files:
                        json_file = os.path.splitext(uploaded_file.name)[0] + ".json"
                        st.write(f"✅ {uploaded_file.name} → {json_file}")

if __name__ == "__main__":
    main() 