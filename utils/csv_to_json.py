import csv
import json
import os
import logging
from typing import Dict, List, Set
import pandas as pd
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_csv_to_json(csv_file, output_file, trimestre):
    """Process a single CSV file and convert it to JSON format"""
    logger.info(f"Starting to process {csv_file}")
    try:
        # Try to detect the correct separator
        separators = [',', ';', '|', '\t']
        df = None
        
        logger.debug(f"Trying different separators for {csv_file}")
        for sep in separators:
            try:
                logger.debug(f"Trying separator '{sep}'")
                df = pd.read_csv(csv_file, encoding='utf-8', sep=sep, on_bad_lines='skip')
                # If we can read at least one row, assume this separator is correct
                if len(df) > 0:
                    logger.info(f"Successfully read {len(df)} rows with separator '{sep}'")
                    break
                else:
                    logger.debug(f"Separator '{sep}' worked but no data found")
            except Exception as e:
                logger.debug(f"Separator '{sep}' failed: {str(e)}")
                continue
        
        # If no separator worked, try without specifying separator
        if df is None or len(df) == 0:
            logger.debug("No separator worked, trying default pandas separator")
            try:
                df = pd.read_csv(csv_file, encoding='utf-8', on_bad_lines='skip')
                logger.info(f"Default separator read {len(df)} rows")
            except Exception as e:
                logger.error(f"Default separator also failed: {str(e)}")
                return False, f"Error reading CSV file {csv_file}: {str(e)}", None
        
        if df is None or len(df) == 0:
            logger.warning(f"No valid data found in {csv_file}")
            return False, f"No valid data found in {csv_file}", None
        
        logger.info(f"DataFrame columns: {list(df.columns)}")
        logger.info(f"DataFrame shape: {df.shape}")
        
        # Convert DataFrame to list of dictionaries
        students = []
        logger.debug("Converting DataFrame to list of dictionaries")
        for i, (idx, row) in enumerate(df.iterrows()):
            try:
                student = {
                    'id': str(row['id']),
                    'name': row['name'],
                    'trimestre': trimestre
                }
                
                # Add all other columns as fields
                for col in df.columns:
                    if col not in ['id', 'name']:
                        student[col] = row[col]
                
                students.append(student)
                if i < 3:  # Show first 3 students for debugging
                    logger.debug(f"Student {i}: {student}")
            except Exception as e:
                logger.error(f"Error processing row {idx}: {str(e)}")
                logger.debug(f"Row data: {row.to_dict()}")
                continue
        
        logger.info(f"Successfully converted {len(students)} students")
        
        # Convert to JSON string
        logger.debug("Converting to JSON string")
        json_data = json.dumps(students, ensure_ascii=False, indent=2)
        
        # Save to file
        logger.debug(f"Saving to file {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_data)
        
        logger.info(f"Successfully processed {csv_file}")
            
        return True, f"Successfully processed {csv_file}", json_data
        
    except Exception as e:
        logger.error(f"Exception in process_csv_to_json: {str(e)}")
        return False, f"Error processing {csv_file}: {str(e)}", None

def process_trimestre_files(csv_files, output_dir):
    """Process multiple CSV files for different trimesters"""
    results = []
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each CSV file
    for csv_file in csv_files:
        # Get the base name without extension
        base_name = os.path.splitext(os.path.basename(csv_file))[0]
        
        # Map the base name to T1, T2, or T3
        trimester_map = {
            '1r': 'T1',
            '2n': 'T2',
            '3r': 'T3'
        }
        
        # Extract trimester from base name
        trimester = None
        for key, value in trimester_map.items():
            if key in base_name.lower():
                trimester = value
                break
        
        if trimester is None:
            results.append((False, f"Could not determine trimester for {csv_file}. The filename must contain '1r', '2n', or '3r' to indicate the trimester."))
            continue
        
        # Create output file name
        output_file = os.path.join(output_dir, f"{trimester}.json")
        
        # Process the file
        success, message, json_data = process_csv_to_json(csv_file, output_file, trimester)
        results.append((success, message))
    
    return results

def main():
    st.title("Conversor de CSV a JSON")
    
    # Get current directory
    current_dir = os.getcwd()
    
    # Create a text input for the directory path
    working_dir = st.text_input(
        "Selecciona el directori que conté els fitxers CSV (han de contenir '1r', '2n' o '3r' al nom)",
        value=current_dir
    )
    
    if not os.path.exists(working_dir):
        st.error("El directori no existeix")
        return
    
    # Get all CSV files in the selected directory
    csv_files = [f for f in os.listdir(working_dir) if f.endswith('.csv')]
    
    if not csv_files:
        st.error(f"No s'han trobat fitxers CSV al directori '{working_dir}'")
        return
    
    # Create a multiselect for CSV files
    selected_files = st.multiselect(
        "Selecciona els fitxers CSV a convertir (han de contenir '1r', '2n' o '3r' al nom)",
        csv_files,
        default=csv_files  # Select all files by default
    )
    
    if not selected_files:
        st.warning("Selecciona almenys un fitxer CSV per convertir")
        return
    
    # Display selected files
    st.subheader("Fitxers seleccionats:")
    for file in selected_files:
        st.write(f"📄 {file}")
    
    # Process files when button is clicked
    if st.button("Convertir a JSON"):
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Process files
        full_paths = [os.path.join(working_dir, f) for f in selected_files]
        results = process_trimestre_files(full_paths, working_dir)
        
        # Display results
        st.subheader("Resultats de la conversió:")
        for i, (success, message) in enumerate(results):
            if success:
                st.success(message)
            else:
                st.error(message)
            progress_bar.progress((i + 1) / len(results))
        
        st.success("Conversió completada!")

if __name__ == "__main__":
    main() 