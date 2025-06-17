import csv
import json
import os
import logging
from typing import Dict, List, Set
import pandas as pd
import streamlit as st
import tempfile

# Configure logging - only if not already configured
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)

def clean_csv_line_breaks(csv_file_path):
    """
    Clean line breaks within CSV cells by properly parsing quoted cells.
    Creates a temporary cleaned file and returns its path.
    """
    logger.info(f"Netejant salts de línia a {csv_file_path}")
    
    # Create a temporary file for the cleaned CSV
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
    temp_file_path = temp_file.name
    
    try:
        # Try different separators to find the right one
        separators = [',', ';', '|', '\t']
        best_separator = None
        best_rows = []
        
        for sep in separators:
            try:
                with open(csv_file_path, 'r', encoding='utf-8') as input_file:
                    reader = csv.reader(input_file, delimiter=sep, quotechar='"')
                    rows = list(reader)
                    if len(rows) > 0 and len(rows[0]) > 1:  # At least one row with multiple columns
                        best_separator = sep
                        best_rows = rows
                        logger.debug(f"S'ha trobat un separador vàlid '{sep}' amb {len(rows)} files")
                        break
            except Exception as e:
                logger.debug(f"El separador '{sep}' ha fallat: {str(e)}")
                continue
        
        if best_separator is None:
            logger.warning("No s'ha pogut determinar el separador CSV, retornant el fitxer original")
            return csv_file_path
        
        # Write cleaned content to temporary file
        with open(temp_file_path, 'w', encoding='utf-8', newline='') as output_file:
            writer = csv.writer(output_file, delimiter=best_separator, quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in best_rows:
                # Clean any remaining line breaks within cells
                cleaned_row = []
                for cell in row:
                    if isinstance(cell, str):
                        # Replace line breaks with spaces within cells
                        cleaned_cell = cell.replace('\n', ' ').replace('\r', ' ').strip()
                        cleaned_row.append(cleaned_cell)
                    else:
                        cleaned_row.append(cell)
                writer.writerow(cleaned_row)
        
        logger.info(f"S'ha netejat amb èxit el fitxer CSV utilitzant el separador '{best_separator}'. Processades {len(best_rows)} files")
        return temp_file_path
        
    except Exception as e:
        logger.error(f"Error netejant el fitxer CSV: {str(e)}")
        # If cleaning fails, return the original file path
        return csv_file_path

def process_csv_to_json(csv_file, output_file, trimestre):
    """Process a single CSV file and convert it to JSON format"""
    logger.info(f"Iniciant el processament de {csv_file}")
    
    # Clean line breaks in the CSV file
    cleaned_csv_file = clean_csv_line_breaks(csv_file)
    should_delete_temp = cleaned_csv_file != csv_file
    
    try:
        # Try to detect the correct separator
        separators = ['|']
        df = None
        
        logger.debug(f"Provant diferents separadors per a {csv_file}")
        for sep in separators:
            try:
                logger.debug(f"Provant separador '{sep}'")
                df = pd.read_csv(cleaned_csv_file, encoding='utf-8', sep=sep, on_bad_lines='skip')
                # If we can read at least one row, assume this separator is correct
                if len(df) > 0:
                    logger.info(f"S'han llegit amb èxit {len(df)} files amb el separador '{sep}'")
                    break
                else:
                    logger.debug(f"El separador '{sep}' ha funcionat però no s'han trobat dades")
            except Exception as e:
                logger.debug(f"El separador '{sep}' ha fallat: {str(e)}")
                continue
        
        # If no separator worked, try without specifying separator
        if df is None or len(df) == 0:
            logger.debug("Cap separador ha funcionat, provant el separador per defecte de pandas")
            try:
                df = pd.read_csv(cleaned_csv_file, encoding='utf-8', on_bad_lines='skip')
                logger.info(f"El separador per defecte ha llegit {len(df)} files")
            except Exception as e:
                logger.error(f"El separador per defecte també ha fallat: {str(e)}")
                return False, f"Error llegint el fitxer CSV {csv_file}: {str(e)}", None
        
        if df is None or len(df) == 0:
            logger.warning(f"No s'han trobat dades vàlides a {csv_file}")
            return False, f"No s'han trobat dades vàlides a {csv_file}", None
        
        # Validate that required columns exist
        required_columns = ['id', 'nom_cognoms', 'numero_avaluacio', 'comentari general']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Falten columnes requerides a {csv_file}: {missing_columns}")
            return False, f"Falten columnes requerides a {csv_file}: {missing_columns}", None
        
        logger.info(f"Columnes del DataFrame: {list(df.columns)}")
        logger.info(f"Forma del DataFrame: {df.shape}")
        
        # Convert DataFrame to list of dictionaries
        students = []
        logger.debug("Convertint DataFrame a llista de diccionaris")
        for i, (idx, row) in enumerate(df.iterrows()):
            try:
                # Validate that id and name are not empty
                if pd.isna(row['id']) or pd.isna(row['nom_cognoms']) or str(row['id']).strip() == '' or str(row['nom_cognoms']).strip() == '':
                    logger.warning(f"Ometent la fila {idx} amb id o nom buit")
                    continue
                
                student = {
                    'id': str(row['id']).strip(),
                    'nom_cognoms': str(row['nom_cognoms']).strip(),
                    'trimestre': str(row['numero_avaluacio']).strip()
                }
                
                # Process materias array
                materias = []
                for j in range(1, 101):  # Check up to 100 materias
                    materia_col = f'm{j}'
                    qualificacio_col = f'q{j}'
                    comentari_col = f'c{j}'
                    
                    # Check if materia column exists and is not empty
                    if materia_col in df.columns:
                        materia_value = row[materia_col]
                        if not pd.isna(materia_value) and str(materia_value).strip() != '':
                            # Get qualificacio and comentari values
                            qualificacio_value = ""
                            comentari_value = ""
                            
                            if qualificacio_col in df.columns:
                                qual_value = row[qualificacio_col]
                                if not pd.isna(qual_value):
                                    qualificacio_value = str(qual_value).strip()
                            
                            if comentari_col in df.columns:
                                com_value = row[comentari_col]
                                if not pd.isna(com_value):
                                    comentari_value = str(com_value).strip()
                            
                            # Add materia to array
                            materias.append({
                                'materia': str(materia_value).strip(),
                                'qualificacio': qualificacio_value,
                                'comentari': comentari_value
                            })
                
                # Add materias array to student
                student['materias'] = materias
                
                # Add all other columns as fields (excluding materias columns)
                for col in df.columns:
                    if col not in ['id', 'nom_cognoms', 'numero_avaluacio', 'comentari general'] and not col.startswith('m') and not col.startswith('q') and not col.startswith('c'):
                        value = row[col]
                        # Handle NaN values
                        if pd.isna(value):
                            student[col] = ""
                        else:
                            student[col] = str(value).strip()
                
                student['comentari_general'] = str(row['comentari general']).strip()
                
                students.append(student)
                if i < 3: # Show first 3 students for debugging
                    logger.debug(f"Estudiant {i}: {student}")
            except Exception as e:
                logger.error(f"Error processant la fila {idx}: {str(e)}")
                logger.debug(f"Dades de la fila: {row.to_dict()}")
                continue
        
        # Validate that we have at least one student
        if len(students) == 0:
            logger.warning(f"No s'han trobat estudiants vàlids a {csv_file}")
            return False, f"No s'han trobat estudiants vàlids a {csv_file}", None
        
        logger.info(f"S'han convertit amb èxit {len(students)} estudiants")
        
        # Convert to JSON string
        logger.debug("Convertint a cadena JSON")
        json_data = json.dumps(students, ensure_ascii=False, indent=2)
        
        # Validate JSON data is not empty
        if not json_data or json_data.strip() == '' or json_data.strip() == '[]':
            logger.error(f"S'ha generat JSON buit per a {csv_file}")
            return False, f"S'ha generat JSON buit per a {csv_file}", None
        
        # Save to file
        logger.debug(f"Desant al fitxer {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_data)
        
        logger.info(f"S'ha processat amb èxit {csv_file}")
            
        return True, f"S'ha processat amb èxit {csv_file}", json_data
        
    except Exception as e:
        logger.error(f"Excepció a process_csv_to_json: {str(e)}")
        return False, f"Error processant {csv_file}: {str(e)}", None
    finally:
        # Clean up temporary file if it was created
        if should_delete_temp and os.path.exists(cleaned_csv_file):
            try:
                os.unlink(cleaned_csv_file)
                logger.debug(f"S'ha netejat el fitxer temporal: {cleaned_csv_file}")
            except Exception as e:
                logger.warning(f"No s'ha pogut eliminar el fitxer temporal {cleaned_csv_file}: {str(e)}")

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
            results.append((False, f"No s'ha pogut determinar el trimestre per a {csv_file}. El nom del fitxer ha de contenir '1r', '2n', o '3r' per indicar el trimestre."))
            continue
        
        # Create output file name
        output_file = os.path.join(output_dir, f"{trimester}.json")
        
        # Process the file
        success, message, json_data = process_csv_to_json(csv_file, output_file, trimester)
        
        # If processing failed, remove any empty JSON file that might have been created
        if not success:
            if os.path.exists(output_file):
                try:
                    # Check if the file is empty or contains only empty array
                    with open(output_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    if not content or content == '[]':
                        os.unlink(output_file)
                        logger.info(f"S'ha eliminat el fitxer JSON buit: {output_file}")
                except Exception as e:
                    logger.warning(f"No s'ha pogut comprovar/eliminar el fitxer JSON buit {output_file}: {str(e)}")
        
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