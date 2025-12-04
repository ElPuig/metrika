import pandas as pd
import re
from typing import Dict, List, Tuple

def is_main_subject(subject_name: str, qualification: str) -> bool:
    """
    Determine if a line is a main subject or a competency description.
    
    Main subjects are typically:
    - Longer names (more than 5 characters)
    - Have actual qualifications (numeric, Assolit-X, Pendent, No assolit, Convalidat)
    - Don't start with lowercase action verbs
    
    Competencies are typically:
    - Shorter descriptions starting with verbs (Selecciona, Acobla, Mesura, etc.)
    """
    if not subject_name or pd.isna(subject_name):
        return False
    
    subject_name = str(subject_name).strip()
    
    # Must have some length
    if len(subject_name) < 5:
        return False
    
    # Must have a qualification
    if not qualification or pd.isna(qualification) or str(qualification).strip() == '':
        return False
    
    qualification = str(qualification).strip()
    
    # Check if it has a valid qualification format
    # Valid formats: numbers (7, 8, 8.5), Assolit-X, No assolit, Convalidat, Pendent
    has_valid_qual = (
        re.match(r'^\d+(?:\.\d+)?$', qualification) or  # numeric (7, 8, 8.5)
        'Assolit' in qualification or
        'No assolit' in qualification or
        'Convalidat' in qualification or
        'Pendent' in qualification
    )
    
    if not has_valid_qual:
        return False
    
    # Filter out common competency action verbs that start the string
    competency_verbs = [
        'Selecciona', 'Acobla', 'Mesura', 'Manté', 'Instal·la', 'Reconeix', 
        'Desplega', 'Interconnecta', 'Compleix', 'Elabora', 'Manipula', 
        'Realitza', 'Crea', 'Aplica', 'Analitza', 'Caracteritza', 'Identifica',
        'Compara', 'Estableix', 'Proposa', 'Adquireix', 'Emet', 'Redacta',
        'Comprèn', 'Distingeix'
    ]
    
    for verb in competency_verbs:
        if subject_name.startswith(verb):
            return False
    
    return True


def parse_qualification(qual_text: str) -> Tuple[str, float]:
    """
    Parse qualification text and extract the grade.
    
    Supports multiple formats:
    - Numeric: 7, 8, 8.5
    - Assolit-X: Assolit-7, Assolit-8.5
    - No assolit: Not achieved
    - Convalidat: Convalidated
    - Pendent/Pendent de qualificar: Pending
    
    Returns:
        Tuple of (status, grade) where:
        - status: 'Assolit', 'No assolit', 'Convalidat', 'Pendent', etc.
        - grade: numeric grade (0-10) or 0 if not applicable
    """
    if not qual_text or qual_text == 'null' or str(qual_text).strip() == '':
        return ('Sense qualificar', 0.0)
    
    qual_text = str(qual_text).strip()
    
    # Check for numeric value (7, 8, 8.5)
    if re.match(r'^\d+(?:\.\d+)?$', qual_text):
        grade = float(qual_text)
        return ('Assolit', grade)
    
    # Check for "Assolit-X" pattern
    match = re.match(r'Assolit-(\d+(?:\.\d+)?)', qual_text)
    if match:
        grade = float(match.group(1))
        return ('Assolit', grade)
    
    # Check for "No assolit"
    if qual_text == 'No assolit':
        return ('No assolit', 0.0)
    
    # Check for "Convalidat"
    if qual_text == 'Convalidat':
        return ('Convalidat', 10.0)  # Consider as maximum grade for statistics
    
    # Check for "Pendent" or variations
    if 'Pendent' in qual_text:
        return ('Pendent', 0.0)
    
    # Fallback: try to extract any numeric grade
    numeric_match = re.search(r'(\d+(?:\.\d+)?)', qual_text)
    if numeric_match:
        grade = float(numeric_match.group(1))
        return ('Qualificat', grade)
    
    return (qual_text, 0.0)


def load_acta_csv(file_path: str) -> Dict:
    """
    Load an acta CSV file and parse it into a structured format.
    
    Returns:
        Dictionary with:
        - 'metadata': dict with file metadata
        - 'students': list of student dictionaries
        - 'subjects': list of all main subjects found
    """
    # Read CSV with pipe delimiter
    df = pd.read_csv(file_path, sep='|', dtype=str, na_values=['null', ''])
    
    # Extract metadata from first row
    metadata = {
        'grup_codi': df.iloc[0]['grup_codi'] if 'grup_codi' in df.columns else 'Unknown',
        'nom_ensenyament': df.iloc[0]['nom_ensenyament'] if 'nom_ensenyament' in df.columns else 'Unknown',
        'data_sessio': df.iloc[0]['data_sessio_avaluacio'] if 'data_sessio_avaluacio' in df.columns else 'Unknown',
        'numero_avaluacio': df.iloc[0]['numero_avaluacio'] if 'numero_avaluacio' in df.columns else 'Unknown'
    }
    
    students = []
    all_subjects = set()
    
    for idx, row in df.iterrows():
        # Skip if ID is null
        if pd.isna(row['id']) or row['id'] == 'null':
            continue
        
        student = {
            'id': str(row['id']),
            'nom_cognoms': row['nom_cognoms'],
            'materies': []
        }
        
        # Parse subjects (m1, q1, c1, m2, q2, c2, ...)
        for i in range(1, 101):
            m_col = f'm{i}'
            q_col = f'q{i}'
            c_col = f'c{i}'
            
            # Check if columns exist
            if m_col not in df.columns:
                break
            
            subject_name = row[m_col]
            
            # Skip if subject name is empty or null
            if pd.isna(subject_name) or subject_name == 'null' or str(subject_name).strip() == '':
                continue
            
            qualification = row[q_col] if q_col in df.columns and not pd.isna(row[q_col]) else ''
            comment = row[c_col] if c_col in df.columns and not pd.isna(row[c_col]) else ''
            
            # Skip if this is a competency description, not a main subject
            if not is_main_subject(subject_name, qualification):
                continue
            
            # Parse qualification
            status, grade = parse_qualification(qualification)
            
            materia_data = {
                'materia': subject_name,
                'qualificacio_raw': qualification,
                'qualificacio_status': status,
                'nota': grade,
                'comentari': str(comment) if comment else ''
            }
            
            student['materies'].append(materia_data)
            all_subjects.add(subject_name)
        
        # Add general comment if exists
        if 'comentari general' in df.columns and not pd.isna(row['comentari general']):
            student['comentari_general'] = str(row['comentari general'])
        else:
            student['comentari_general'] = ''
        
        students.append(student)
    
    return {
        'metadata': metadata,
        'students': students,
        'subjects': sorted(list(all_subjects))
    }


def calculate_subject_statistics(students: List[Dict], subject_name: str) -> Dict:
    """
    Calculate statistics for a specific subject across all students.
    
    Returns:
        Dictionary with statistics including:
        - count_assolit: number of students who passed
        - count_no_assolit: number of students who failed
        - count_pending: number of students with pending status
        - count_convalidat: number of students with convalidated subject
        - avg_grade: average grade (excluding pending/convalidated)
        - grades: list of all grades
    """
    stats = {
        'subject': subject_name,
        'count_assolit': 0,
        'count_no_assolit': 0,
        'count_pendent': 0,
        'count_convalidat': 0,
        'count_total': 0,
        'grades': [],
        'avg_grade': 0.0
    }
    
    for student in students:
        for materia in student['materies']:
            if materia['materia'] == subject_name:
                stats['count_total'] += 1
                status = materia['qualificacio_status']
                grade = materia['nota']
                
                if status == 'Assolit':
                    stats['count_assolit'] += 1
                    stats['grades'].append(grade)
                elif status == 'No assolit':
                    stats['count_no_assolit'] += 1
                elif status == 'Convalidat':
                    stats['count_convalidat'] += 1
                elif status == 'Pendent':
                    stats['count_pendent'] += 1
    
    # Calculate average grade
    if stats['grades']:
        stats['avg_grade'] = sum(stats['grades']) / len(stats['grades'])
    
    return stats


def get_student_summary(student: Dict) -> Dict:
    """
    Calculate summary statistics for a student.
    
    Returns:
        Dictionary with summary including:
        - total_subjects: total number of subjects evaluated
        - passed_count: number of passed subjects
        - failed_count: number of failed subjects
        - pending_count: number of pending subjects
        - avg_grade: average grade
        - success_rate: percentage of passed subjects
    """
    if not student['materies']:
        return {
            'total_subjects': 0,
            'passed_count': 0,
            'failed_count': 0,
            'pending_count': 0,
            'avg_grade': 0.0,
            'success_rate': 0.0
        }
    
    grades = []
    passed_count = 0
    failed_count = 0
    pending_count = 0
    
    for materia in student['materies']:
        status = materia['qualificacio_status']
        grade = materia['nota']
        
        if status == 'Assolit':
            passed_count += 1
            grades.append(grade)
        elif status == 'No assolit':
            failed_count += 1
        elif status == 'Pendent':
            pending_count += 1
    
    total_subjects = len(student['materies'])
    avg_grade = sum(grades) / len(grades) if grades else 0.0
    success_rate = (passed_count / total_subjects * 100) if total_subjects > 0 else 0.0
    
    return {
        'total_subjects': total_subjects,
        'passed_count': passed_count,
        'failed_count': failed_count,
        'pending_count': pending_count,
        'avg_grade': avg_grade,
        'success_rate': success_rate
    }
