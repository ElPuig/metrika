import csv
import json
import os
from typing import Dict, List, Set
import pandas as pd
import streamlit as st

def process_csv_to_json(csv_file, output_file, trimestre):
    """Process a single CSV file and convert it to JSON format"""
    try:
        # Read CSV file
        df = pd.read_csv(csv_file, encoding='utf-8')
        
        # Convert DataFrame to list of dictionaries
        students = []
        for _, row in df.iterrows():
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
        
        # Convert to JSON string
        json_data = json.dumps(students, ensure_ascii=False, indent=2)
        
        # Create a download button for the JSON file
        st.download_button(
            label=f"Descarregar {trimestre}.json",
            data=json_data,
            file_name=f"{trimestre}.json",
            mime="application/json"
        )
        
        print(f"Successfully processed {csv_file}")
            
        return True, f"Successfully processed {csv_file}"
        
    except Exception as e:
        return False, f"Error processing {csv_file}: {str(e)}"

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
        success, message = process_csv_to_json(csv_file, output_file, trimester)
        results.append((success, message))
    
    return results

def main():
    st.set_page_config(layout="wide")
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