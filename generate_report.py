import json
import os
from sections.pdf_report import create_pdf_report

def load_json_files(trimestre=None):
    """Load JSON files from the docs directory, optionally filtered by trimester"""
    all_students = []
    docs_dir = "docs"
    
    for filename in os.listdir(docs_dir):
        if filename.endswith('.json'):
            # Si se especifica un trimestre, solo cargar ese trimestre
            if trimestre and not trimestre in filename:
                continue
                
            with open(os.path.join(docs_dir, filename), 'r', encoding='utf-8') as f:
                students = json.load(f)
                # Añadir información del trimestre a cada estudiante
                for student in students:
                    student['trimestre'] = filename.split('.')[0]  # Extraer el trimestre del nombre del archivo
                all_students.extend(students)
    
    return all_students

def ensure_report_dir():
    """Ensure the report directory exists"""
    report_dir = os.path.join("docs", "report")
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    return report_dir

def main():
    # Cargar datos del último trimestre
    students = load_json_files("T1")
    
    # Asegurar que existe el directorio de informes
    report_dir = ensure_report_dir()
    
    # Generar informe PDF
    output_path = os.path.join(report_dir, "informe_qualificacions.pdf")
    create_pdf_report(students, output_path)
    print(f"Informe generado exitosamente: {output_path}")

if __name__ == "__main__":
    main() 