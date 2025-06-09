import pdfplumber
import pandas as pd
import json
import os
from typing import List, Dict, Any
import pdfminer.high_level
from pdfminer.high_level import extract_text

def convert_pdf_to_csv_and_json(pdf_path: str, output_dir: str) -> None:
    """
    Convert the first 3 pages of a PDF to a single CSV and the remaining pages to JSON.
    
    Args:
        pdf_path (str): Path to the input PDF file
        output_dir (str): Directory where output files will be saved
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get the base filename without extension
    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    
    with pdfplumber.open(pdf_path) as pdf:
        # Process first 3 pages as CSV
        all_tables = []
        for i in range(min(3, len(pdf.pages))):
            page = pdf.pages[i]
            tables = page.extract_tables()
            
            if tables:
                # Convert tables to DataFrames and add page number
                for table in tables:
                    if len(table) > 1:  # Check if table has data
                        df = pd.DataFrame(table[1:], columns=table[0])
                        df['page_number'] = i + 1  # Add page number column
                        all_tables.append(df)
        
        if all_tables:
            # Merge all tables into a single DataFrame
            merged_df = pd.concat(all_tables, ignore_index=True)

            # Lista de columnas a conservar (según la imagen y el mensaje del usuario)
            columnas_deseadas = [
                'N.',
                "Identificador de l'alumne/a",
                "Nom i cognoms de l'alumne/a",
                'MAE',
                'Ll. Cat.',
                'Ll. Cast.',
                'Ll. Estr.',
                'Mat.',
                'CS:GH',
                'Ed. Fís.',
                'EVCE',
                'Optativa',
                'Optativa',
                'Optativa',
                'Optativa',
                'Optativa',
                'PG_I',
                'PG_II',
                'Rel.',
                'Comp. Dig.',
                'Comp. Pers.',
                'Comp. Ciut.',
                'Comp. Empr.',
                'Altres Matèries'
            ]

            # Filtrar solo las columnas que existan en el DataFrame
            columnas_presentes = [col for col in columnas_deseadas if col in merged_df.columns]
            filtered_df = merged_df[columnas_presentes]

            # Guardar el CSV filtrado
            csv_path = os.path.join(output_dir, f"{base_filename}_merged_tables.csv")
            filtered_df.to_csv(csv_path, index=False)
            print(f"Saved merged and filtered CSV: {csv_path}")
        
        # Extraer texto puro de las páginas a partir de la cuarta usando pdfminer.six
        full_text = extract_text(pdf_path)
        # pdfminer separa páginas con '\x0c' (form feed)
        pages_text = full_text.split('\x0c')
        # Aseguro que hay suficientes páginas
        remaining_pages_data = []
        for i in range(3, len(pdf.pages)):
            page_text = pages_text[i].strip() if i < len(pages_text) else ''
            # Estructura: nombre alumno (negrita, primera línea), luego comentarios
            # Tomo la primera línea como nombre, el resto como comentarios
            lines = [l for l in page_text.split('\n') if l.strip()]
            if lines:
                alumno = lines[0]
                comentarios = '\n'.join(lines[1:]).strip()
            else:
                alumno = ''
                comentarios = ''
            page_data = {
                "alumno": alumno,
                "comentarios": comentarios
            }
            remaining_pages_data.append(page_data)
        if remaining_pages_data:
            # Save remaining pages to JSON
            json_path = os.path.join(output_dir, f"{base_filename}_remaining_pages.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(remaining_pages_data, f, ensure_ascii=False, indent=2)
            print(f"Saved JSON: {json_path}")

def main():
    """
    Example usage of the PDF converter
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert PDF pages to CSV and JSON formats')
    parser.add_argument('--pdf_path', '-p', help='Path to the input PDF file')
    parser.add_argument('--output-dir', '-o', default='docs/output', help='Directory for output files')
    
    args = parser.parse_args()
    
    if not args.pdf_path:
        parser.error("Please provide a PDF file path using --pdf_path or -p")
    
    convert_pdf_to_csv_and_json(args.pdf_path, args.output_dir)

if __name__ == "__main__":
    main() 