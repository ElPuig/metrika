import streamlit as st
import os
import logging
from utils.csv_to_json import process_csv_to_json
import tempfile

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting CSV converter")
    st.title("Conversor CSV a JSON")
    
    # Create two columns for the layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Opció 1: Seleccionar directori")
        # Get current directory
        current_dir = os.getcwd()
        logger.debug(f"Current directory: {current_dir}")
        
        # Create a text input for the directory path
        working_dir = st.text_input(
            "Selecciona el directori que conté els fitxers CSV",
            value=current_dir
        )
        
        if st.button("Convertir fitxers del directori"):
            logger.info(f"Starting directory conversion for: {working_dir}")
            if os.path.exists(working_dir):
                try:
                    # Find all CSV files in the directory
                    csv_files = [f for f in os.listdir(working_dir) if f.endswith('.csv')]
                    logger.info(f"Found {len(csv_files)} CSV files: {csv_files}")
                    
                    if not csv_files:
                        st.warning("No s'han trobat fitxers CSV al directori seleccionat")
                        return
                    
                    # Create a progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Process each CSV file
                    processed_files = []
                    for i, csv_file in enumerate(csv_files):
                        # Update progress
                        progress = (i + 1) / len(csv_files)
                        progress_bar.progress(progress)
                        status_text.text(f"Processant {csv_file}...")
                        
                        logger.info(f"Processing file {i+1}/{len(csv_files)}: {csv_file}")
                        
                        # Get trimester from filename (assuming format like T1.csv, T2.csv, etc.)
                        trimestre = os.path.splitext(csv_file)[0]
                        logger.debug(f"Extracted trimester: {trimestre}")
                        
                        # Define input and output paths
                        input_csv = os.path.join(working_dir, csv_file)
                        output_json = os.path.join(working_dir, f"{trimestre}.json")
                        logger.debug(f"Input: {input_csv}, Output: {output_json}")
                        
                        try:
                            # Convert CSV to JSON
                            success, message, json_data = process_csv_to_json(input_csv, output_json, trimestre)
                            if success:
                                logger.info(f"Successfully processed {csv_file}")
                                processed_files.append((trimestre, json_data))
                            else:
                                logger.error(f"Failed to process {csv_file}: {message}")
                                st.error(f"Error processant {csv_file}: {message}")
                        except Exception as e:
                            logger.error(f"Exception processing {csv_file}: {str(e)}")
                            st.error(f"Error processant {csv_file}: {str(e)}")
                            # Show file info for debugging
                            try:
                                with open(input_csv, 'r', encoding='utf-8') as f:
                                    first_lines = f.readlines()[:5]
                                logger.debug(f"First 5 lines of {csv_file}:")
                                for i, line in enumerate(first_lines):
                                    logger.debug(f"Line {i+1}: {line.strip()}")
                                st.text(f"Primeres línies del fitxer {csv_file}:")
                                for i, line in enumerate(first_lines):
                                    st.text(f"Línia {i+1}: {line.strip()}")
                            except Exception as read_error:
                                logger.error(f"Cannot read file for debugging: {str(read_error)}")
                                st.error(f"No es pot llegir el fitxer per depuració: {str(read_error)}")
                            continue
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    if processed_files:
                        logger.info(f"Conversion completed successfully. Processed {len(processed_files)} files")
                        st.success("Conversió completada amb èxit!")
                        
                        # Show the list of converted files
                        st.subheader("Fitxers convertits:")
                        for csv_file in csv_files:
                            json_file = os.path.splitext(csv_file)[0] + ".json"
                            st.write(f"✅ {csv_file} → {json_file}")
                        
                        # Create download buttons for processed files
                        if processed_files:
                            st.subheader("Descarregar fitxers JSON:")
                            for trimestre, json_data in processed_files:
                                st.download_button(
                                    label=f"Descarregar {trimestre}.json",
                                    data=json_data,
                                    file_name=f"{trimestre}.json",
                                    mime="application/json"
                                )
                    else:
                        logger.warning("No files were successfully processed")
                        st.error("No s'han pogut processar cap fitxer")
                    
                except Exception as e:
                    logger.error(f"Error accessing directory: {str(e)}")
                    st.error(f"Error accedint al directori: {str(e)}")
            else:
                logger.error(f"Directory does not exist: {working_dir}")
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
            logger.info(f"Files uploaded: {[f.name for f in uploaded_files]}")
            if st.button("Convertir fitxers pujats"):
                logger.info(f"Starting upload conversion for {len(uploaded_files)} files")
                if not os.path.exists(dest_dir):
                    logger.error(f"Destination directory does not exist: {dest_dir}")
                    st.error("El directori de destinació no existeix")
                    return
                    
                # Create a temporary directory to store the uploaded files
                with tempfile.TemporaryDirectory() as temp_dir:
                    logger.debug(f"Created temporary directory: {temp_dir}")
                    # Save uploaded files to temporary directory
                    for uploaded_file in uploaded_files:
                        file_path = os.path.join(temp_dir, uploaded_file.name)
                        with open(file_path, 'wb') as f:
                            f.write(uploaded_file.getbuffer())
                        logger.debug(f"Saved uploaded file to: {file_path}")
                    
                    # Create a progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Process each uploaded file
                    processed_files = []
                    for i, uploaded_file in enumerate(uploaded_files):
                        # Update progress
                        progress = (i + 1) / len(uploaded_files)
                        progress_bar.progress(progress)
                        status_text.text(f"Processant {uploaded_file.name}...")
                        
                        logger.info(f"Processing uploaded file {i+1}/{len(uploaded_files)}: {uploaded_file.name}")
                        
                        # Get trimester from filename
                        trimestre = os.path.splitext(uploaded_file.name)[0]
                        logger.debug(f"Extracted trimester: {trimestre}")
                        
                        # Define input and output paths
                        input_csv = os.path.join(temp_dir, uploaded_file.name)
                        output_json = os.path.join(dest_dir, f"{trimestre}.json")
                        logger.debug(f"Input: {input_csv}, Output: {output_json}")
                        
                        try:
                            # Convert CSV to JSON
                            success, message, json_data = process_csv_to_json(input_csv, output_json, trimestre)
                            if success:
                                logger.info(f"Successfully processed {uploaded_file.name}")
                                processed_files.append((trimestre, json_data))
                            else:
                                logger.error(f"Failed to process {uploaded_file.name}: {message}")
                                st.error(f"Error processant {uploaded_file.name}: {message}")
                        except Exception as e:
                            logger.error(f"Exception processing {uploaded_file.name}: {str(e)}")
                            st.error(f"Error processant {uploaded_file.name}: {str(e)}")
                            # Show file info for debugging
                            try:
                                with open(input_csv, 'r', encoding='utf-8') as f:
                                    first_lines = f.readlines()[:5]
                                logger.debug(f"First 5 lines of {uploaded_file.name}:")
                                for i, line in enumerate(first_lines):
                                    logger.debug(f"Line {i+1}: {line.strip()}")
                                st.text(f"Primeres línies del fitxer {uploaded_file.name}:")
                                for i, line in enumerate(first_lines):
                                    st.text(f"Línia {i+1}: {line.strip()}")
                            except Exception as read_error:
                                logger.error(f"Cannot read file for debugging: {str(read_error)}")
                                st.error(f"No es pot llegir el fitxer per depuració: {str(read_error)}")
                            continue
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    if processed_files:
                        logger.info(f"Upload conversion completed successfully. Processed {len(processed_files)} files")
                        st.success("Conversió completada amb èxit!")
                        
                        # Show the list of converted files
                        st.subheader("Fitxers convertits:")
                        for uploaded_file in uploaded_files:
                            json_file = os.path.splitext(uploaded_file.name)[0] + ".json"
                            st.write(f"✅ {uploaded_file.name} → {json_file}")
                        
                        # Create download buttons for processed files
                        if processed_files:
                            st.subheader("Descarregar fitxers JSON:")
                            for trimestre, json_data in processed_files:
                                st.download_button(
                                    label=f"Descarregar {trimestre}.json",
                                    data=json_data,
                                    file_name=f"{trimestre}.json",
                                    mime="application/json"
                                )
                    else:
                        logger.warning("No uploaded files were successfully processed")
                        st.error("No s'han pogut processar cap fitxer pujat")

if __name__ == "__main__":
    main() 