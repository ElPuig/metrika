"""
Utility to normalize data from different sources (JSON, CSV) into a common format
"""

def normalize_student_data(student):
    """
    Normalize student data from CSV or JSON format into a common format.
    
    Returns a student dict with:
    - id: student ID
    - nom_cognoms: student name
    - materies: list of subjects (only current level 4t for CSV)
    - pending_subjects: list of pending subjects (only for CSV)
    - comentari_general: general comment (only for CSV)
    """
    
    # Check if it's CSV data (has 'subjects' key) or JSON data (has 'materies' key)
    if 'subjects' in student:
        # CSV format - normalize to JSON format
        normalized = {
            'id': student['id'],
            'nom_cognoms': student['nom'],
            'grup': student.get('grup_codi', ''),
            'trimestre': student.get('trimestre', ''),
            'materies': [],
            'pending_subjects': student.get('pending_subjects', []),
            'comentari_general': student.get('comentari_general', ''),
            'numero_avaluacio': student.get('numero_avaluacio', ''),
            'codi_ensenyament': student.get('codi_ensenyament', ''),
            'nom_ensenyament': student.get('nom_ensenyament', '')
        }
        
        # Convert subjects to materies format
        for subject in student.get('subjects', []):
            normalized['materies'].append({
                'materia': subject['subject'],
                'qualificacio': subject['qualification'],
                'comentari': subject['comment']
            })
        
        return normalized
    
    else:
        # Already in JSON format, just return as is
        return student


def get_current_level_subjects(student):
    """
    Get only the current level subjects (4t) from a student.
    For CSV: returns 'subjects'
    For JSON: filters 'materies' by those containing '4t' (or returns all if no level info)
    """
    
    if 'subjects' in student:
        # CSV format - subjects are already filtered to 4t
        return student['subjects']
    else:
        # JSON format - return all materies (assume they're current level)
        return student.get('materies', [])
