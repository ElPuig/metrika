import csv
import json
import os
from typing import Dict, List, Set

def process_csv_to_json(csv_file: str, json_file: str) -> None:
    # List to store all students data
    students_data = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            # Read CSV file with custom delimiter and quote character
            csv_reader = csv.DictReader(file, delimiter='|', quotechar='"')
            
            # Print column names for debugging
            print("Available columns:", csv_reader.fieldnames)
            
            for row in csv_reader:
                try:
                    # Create student dictionary with more flexible field names
                    student = {
                        "id": row.get("id", row.get("ID", "")),
                        "nom_cognoms": row.get("nom_cognoms", row.get("NOM_COGNOMS", "")),
                        "materies": [],
                        "comentari_general": row.get("comentari general", row.get("COMENTARI GENERAL", ""))
                    }
                    
                    # Process subjects (up to 100)
                    for i in range(1, 101):
                        m_key = f"m{i}"
                        q_key = f"q{i}"
                        c_key = f"c{i}"
                        
                        # Check if the subject exists in the row
                        if m_key in row and row[m_key]:
                            subject = {
                                "materia": row[m_key],
                                "qualificacio": row.get(q_key, ""),
                                "comentari": row.get(c_key, "")
                            }
                            student["materies"].append(subject)
                    
                    students_data.append(student)
                except Exception as row_error:
                    print(f"Error processing row: {row}")
                    print(f"Row error details: {str(row_error)}")
                    continue
        
        # Write to JSON file
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(students_data, f, ensure_ascii=False, indent=2)
            
    except FileNotFoundError:
        print(f"Error: Could not find the CSV file at {csv_file}")
        raise
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        raise

def get_unique_subjects(csv_file: str) -> Set[str]:
    unique_subjects = set()
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file, delimiter='|', quotechar='"')
            
            for row in csv_reader:
                # Process subjects (up to 100)
                for i in range(1, 101):
                    m_key = f"m{i}"
                    if m_key in row and row[m_key]:
                        unique_subjects.add(row[m_key])
                        
    except FileNotFoundError:
        print(f"Error: Could not find the CSV file at {csv_file}")
        raise
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        raise
        
    return unique_subjects

if __name__ == "__main__":
    # Get the parent directory path
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Define input and output paths
    input_csv = os.path.join(parent_dir, "docs", "dummy1.csv")
    output_json = os.path.join(parent_dir, "docs", "dummy1.json")
    
    try:
        # Get and print unique subjects
        unique_subjects = get_unique_subjects(input_csv)
        print("\nMaterias únicas encontradas:")
        for subject in sorted(unique_subjects):
            print(f"- {subject}")
            
        # Process CSV to JSON
        process_csv_to_json(input_csv, output_json)
        print(f"\nConversión completada con éxito. Output guardado en {output_json}")
    except Exception as e:
        print(f"An error occurred: {str(e)}") 