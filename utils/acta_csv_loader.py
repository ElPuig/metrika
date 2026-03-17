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


def _pending_markers_for_level(level: Any) -> List[str]:
    """Return the subject markers that should count as pending for a given level."""
    level_str = '' if pd.isna(level) else str(level).strip()
    mapping = {
        '1': [],
        '2': ['1r'],
        '3': ['1r', '2n'],
        '4': ['1r', '2n', '3r']
    }
    # Fallback keeps previous behaviour (all lower levels) if level is missing or unexpected
    return mapping.get(level_str, ['1r', '2n', '3r'])


def _current_level_marker(level: Any) -> str:
    """Return the subject marker for current level subjects."""
    level_str = '' if pd.isna(level) else str(level).strip()
    mapping = {
        '1': '1r',
        '2': '2n',
        '3': '3r',
        '4': '4t'
    }
    # Fallback to '4t' for backwards compatibility
    return mapping.get(level_str, '4t')


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
        student_level = row.get('nivell', None)
        pending_markers = _pending_markers_for_level(student_level)
        current_marker = _current_level_marker(student_level)

        # Extract basic student info
        student = {
            'id': str(row['id']),
            'nom': row['nom_cognoms'],
            'nivell': row.get('nivell', None),
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
            
            subject_name_str = str(subject_name)

            # Create subject dictionary
            subject_data = {
                'subject': subject_name_str,
                'qualification': str(qualification) if not pd.isna(qualification) else '',
                'comment': str(comment) if not pd.isna(comment) else ''
            }
            
            # Determine if it's a current level subject or pending depending on level markers
            if current_marker in subject_name_str:
                student['subjects'].append(subject_data)
            elif any(marker in subject_name_str for marker in pending_markers):
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
        student_level = row.get('nivell', None)
        pending_markers = _pending_markers_for_level(student_level)
        current_marker = _current_level_marker(student_level)

        # Extract basic student info
        student = {
            'id': str(row['id']),
            'nom': row['nom_cognoms'],
            'nivell': row.get('nivell', None),
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
            
            subject_name_str = str(subject_name)

            # Create subject dictionary
            subject_data = {
                'subject': subject_name_str,
                'qualification': str(qualification) if not pd.isna(qualification) else '',
                'comment': str(comment) if not pd.isna(comment) else ''
            }
            
            # Determine if it's a current level subject or pending depending on level markers
            if current_marker in subject_name_str:
                student['subjects'].append(subject_data)
            elif any(marker in subject_name_str for marker in pending_markers):
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


def _normalize_subject_name(subject_name: Any) -> str:
    """Return a normalized subject name suitable for stable grouping."""
    if pd.isna(subject_name):
        return ''

    return ' '.join(str(subject_name).split())


def _get_current_course_subjects(student: Dict[str, Any]) -> List[Dict[str, str]]:
    """Return current-course subjects in a unified dictionary format."""
    # CSV parser output: current-course subjects are already filtered into `subjects`.
    if 'subjects' in student:
        subjects = []
        for subject in student.get('subjects', []):
            subject_name = _normalize_subject_name(subject.get('subject', ''))
            if not subject_name:
                continue

            subjects.append({
                'subject': subject_name,
                'qualification': str(subject.get('qualification', '')).strip(),
                'comment': str(subject.get('comment', '')).strip()
            })
        return subjects

    # Fallback for normalized JSON-like objects.
    subjects = []
    for materia in student.get('materies', []):
        subject_name = _normalize_subject_name(materia.get('materia', ''))
        if not subject_name:
            continue

        subjects.append({
            'subject': subject_name,
            'qualification': str(materia.get('qualificacio', '')).strip(),
            'comment': str(materia.get('comentari', '')).strip()
        })

    return subjects


def get_current_course_subject_enrollment(students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return subjects sorted by enrolled-student count (desc) then by subject name."""
    subject_student_ids: Dict[str, set] = {}

    for student in students:
        student_id = str(student.get('id', '')).strip()
        seen_subjects = set()

        for subject in _get_current_course_subjects(student):
            subject_name = subject['subject']
            if subject_name in seen_subjects:
                continue

            seen_subjects.add(subject_name)
            subject_student_ids.setdefault(subject_name, set()).add(student_id)

    sorted_subjects = sorted(
        subject_student_ids.keys(),
        key=lambda subject_name: (
            -len(subject_student_ids[subject_name]),
            subject_name.lower()
        )
    )

    return [
        {
            'subject': subject_name,
            'student_count': len(subject_student_ids[subject_name])
        }
        for subject_name in sorted_subjects
    ]


def build_term_export_dataframe(students: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Build a wide export table for one term:
    - one row per student
    - one subject block per subject (qualification + comment)
    - subjects ordered by enrolled student count (desc)
    """
    base_columns = ['Nom complet', 'ID alumne', 'Grup']
    if not students:
        return pd.DataFrame(columns=base_columns)

    ordered_subjects = get_current_course_subject_enrollment(students)

    export_columns = list(base_columns)
    for subject_info in ordered_subjects:
        subject_name = subject_info['subject']
        export_columns.append(f"{subject_name} - Qualificació")
        export_columns.append(f"{subject_name} - Comentari")

    export_rows = []
    for student in students:
        row = {
            'Nom complet': str(student.get('nom', student.get('nom_cognoms', ''))).strip(),
            'ID alumne': str(student.get('id', '')).strip(),
            'Grup': str(student.get('grup', student.get('grup_codi', ''))).strip()
        }

        student_subject_map: Dict[str, Dict[str, str]] = {}
        for subject in _get_current_course_subjects(student):
            subject_name = subject['subject']
            existing = student_subject_map.get(subject_name, {'qualification': '', 'comment': ''})

            if subject['qualification'] and not existing['qualification']:
                existing['qualification'] = subject['qualification']
            if subject['comment'] and not existing['comment']:
                existing['comment'] = subject['comment']

            student_subject_map[subject_name] = existing

        for subject_info in ordered_subjects:
            subject_name = subject_info['subject']
            value = student_subject_map.get(subject_name, {'qualification': '', 'comment': ''})
            row[f"{subject_name} - Qualificació"] = value['qualification']
            row[f"{subject_name} - Comentari"] = value['comment']

        export_rows.append(row)

    return pd.DataFrame(export_rows, columns=export_columns)
