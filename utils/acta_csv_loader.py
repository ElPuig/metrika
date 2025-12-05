"""
Utility module to load and parse CSV acta files with the specific structure:
- Basic student info (n, id, nom_cognoms)
- Group and evaluation info (grup_codi, numero_avaluacio, codi_ensenyament, nom_ensenyament)
- Subject triplets (m1/q1/c1, m2/q2/c2, ...) where:
  - m = subject name
  - q = qualification
  - c = comment
- General comment (comentari general)
"""

import pandas as pd
import os
from typing import List, Dict, Any


def parse_acta_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse a CSV acta file and return a list of student dictionaries.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        List of dictionaries, each representing a student with their subjects and info
    """
    # Read CSV with pipe delimiter
    df = pd.read_csv(file_path, delimiter='|', encoding='utf-8')
    
    students = []
    
    for _, row in df.iterrows():
        # Extract basic student info
        student = {
            'id': str(row['id']),
            'nom': row['nom_cognoms'],
            'grup_codi': row['grup_codi'],
            'numero_avaluacio': row['numero_avaluacio'],
            'codi_ensenyament': row['codi_ensenyament'],
            'nom_ensenyament': row['nom_ensenyament'],
            'subjects': [],
            'pending_subjects': [],
            'comentari_general': row.get('comentari general', '')
        }
        
        # Find all subject columns (m1, m2, m3, ... m100)
        # Each subject has 3 columns: mX (name), qX (qualification), cX (comment)
        for i in range(1, 101):  # Support up to 100 subjects
            subject_col = f'm{i}'
            qual_col = f'q{i}'
            comment_col = f'c{i}'
            
            if subject_col not in df.columns:
                break
                
            subject_name = row.get(subject_col, '')
            qualification = row.get(qual_col, '')
            comment = row.get(comment_col, '')
            
            # Skip if subject name is empty or NaN
            if pd.isna(subject_name) or subject_name == '':
                continue
            
            # Create subject dictionary
            subject_data = {
                'subject': str(subject_name),
                'qualification': str(qualification) if not pd.isna(qualification) else '',
                'comment': str(comment) if not pd.isna(comment) else ''
            }
            
            # Determine if it's a current level subject (4t) or pending (1r, 2n, 3r)
            if '4t' in str(subject_name):
                student['subjects'].append(subject_data)
            elif any(level in str(subject_name) for level in ['1r', '2n', '3r']):
                student['pending_subjects'].append(subject_data)
        
        students.append(student)
    
    return students


def parse_uploaded_acta_csv(uploaded_file) -> List[Dict[str, Any]]:
    """
    Parse an uploaded CSV acta file (Streamlit UploadedFile object).
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        List of dictionaries, each representing a student with their subjects and info
    """
    # Reset file pointer to beginning
    uploaded_file.seek(0)
    
    # Read CSV with pipe delimiter
    try:
        df = pd.read_csv(uploaded_file, delimiter='|', encoding='utf-8')
    except Exception as e:
        # If it fails, try with different encoding or parameters
        uploaded_file.seek(0)
        try:
            df = pd.read_csv(uploaded_file, delimiter='|', encoding='latin-1')
        except Exception as e2:
            # Last attempt: try to read it as text and debug
            uploaded_file.seek(0)
            content = uploaded_file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='ignore')
            
            # Check if file is empty
            if not content.strip():
                raise ValueError("El fitxer CSV està buit")
            
            # Try to detect the actual delimiter
            first_line = content.split('\n')[0] if '\n' in content else content
            if '|' not in first_line:
                raise ValueError(f"El fitxer no conté el separador '|'. Primera línia: {first_line[:100]}")
            
            raise ValueError(f"Error llegint el CSV: {str(e)}")
    
    students = []
    
    for _, row in df.iterrows():
        # Extract basic student info
        student = {
            'id': str(row['id']),
            'nom': row['nom_cognoms'],
            'grup_codi': row['grup_codi'],
            'numero_avaluacio': row['numero_avaluacio'],
            'codi_ensenyament': row['codi_ensenyament'],
            'nom_ensenyament': row['nom_ensenyament'],
            'subjects': [],
            'pending_subjects': [],
            'comentari_general': row.get('comentari general', '')
        }
        
        # Find all subject columns (m1, m2, m3, ... m100)
        # Each subject has 3 columns: mX (name), qX (qualification), cX (comment)
        for i in range(1, 101):  # Support up to 100 subjects
            subject_col = f'm{i}'
            qual_col = f'q{i}'
            comment_col = f'c{i}'
            
            if subject_col not in df.columns:
                break
                
            subject_name = row.get(subject_col, '')
            qualification = row.get(qual_col, '')
            comment = row.get(comment_col, '')
            
            # Skip if subject name is empty or NaN
            if pd.isna(subject_name) or subject_name == '':
                continue
            
            # Create subject dictionary
            subject_data = {
                'subject': str(subject_name),
                'qualification': str(qualification) if not pd.isna(qualification) else '',
                'comment': str(comment) if not pd.isna(comment) else ''
            }
            
            # Determine if it's a current level subject (4t) or pending (1r, 2n, 3r)
            if '4t' in str(subject_name):
                student['subjects'].append(subject_data)
            elif any(level in str(subject_name) for level in ['1r', '2n', '3r']):
                student['pending_subjects'].append(subject_data)
        
        students.append(student)
    
    return students


def get_acta_csv_info(file_path: str) -> Dict[str, Any]:
    """
    Get metadata information from a CSV acta file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Dictionary with file metadata (grup, trimestre, etc.)
    """
    df = pd.read_csv(file_path, delimiter='|', encoding='utf-8', nrows=1)
    
    if len(df) == 0:
        return {
            'grup': 'Unknown',
            'trimestre': 'Unknown',
            'nom_ensenyament': 'Unknown'
        }
    
    row = df.iloc[0]
    
    return {
        'grup': row.get('grup_codi', 'Unknown'),
        'trimestre': f"T{row.get('numero_avaluacio', 'X')}",
        'nom_ensenyament': row.get('nom_ensenyament', 'Unknown')
    }
