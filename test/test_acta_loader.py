import pytest
import pandas as pd
from utils.acta_loader import (
    parse_qualification,
    load_acta_csv,
    calculate_subject_statistics,
    get_student_summary
)
import tempfile
import os


def test_parse_qualification_assolit():
    """Test parsing 'Assolit-X' format"""
    status, grade = parse_qualification('Assolit-7')
    assert status == 'Assolit'
    assert grade == 7.0
    
    status, grade = parse_qualification('Assolit-8.5')
    assert status == 'Assolit'
    assert grade == 8.5


def test_parse_qualification_no_assolit():
    """Test parsing 'No assolit' format"""
    status, grade = parse_qualification('No assolit')
    assert status == 'No assolit'
    assert grade == 0.0


def test_parse_qualification_convalidat():
    """Test parsing 'Convalidat' format"""
    status, grade = parse_qualification('Convalidat')
    assert status == 'Convalidat'
    assert grade == 10.0


def test_parse_qualification_pendent():
    """Test parsing 'Pendent' format"""
    status, grade = parse_qualification('Pendent de qualificar')
    assert status == 'Pendent'
    assert grade == 0.0
    
    status, grade = parse_qualification('Pendent')
    assert status == 'Pendent'
    assert grade == 0.0


def test_parse_qualification_empty():
    """Test parsing empty/null values"""
    status, grade = parse_qualification('')
    assert status == 'Sense qualificar'
    assert grade == 0.0
    
    status, grade = parse_qualification('null')
    assert status == 'Sense qualificar'
    assert grade == 0.0


def test_get_student_summary():
    """Test student summary calculation"""
    student = {
        'id': '123',
        'nom_cognoms': 'Test Student',
        'materies': [
            {'materia': 'Math', 'qualificacio_status': 'Assolit', 'nota': 8.0, 'comentari': ''},
            {'materia': 'Physics', 'qualificacio_status': 'Assolit', 'nota': 7.5, 'comentari': ''},
            {'materia': 'Chemistry', 'qualificacio_status': 'No assolit', 'nota': 0.0, 'comentari': ''},
            {'materia': 'Biology', 'qualificacio_status': 'Pendent', 'nota': 0.0, 'comentari': ''},
            {'materia': 'English', 'qualificacio_status': 'Convalidat', 'nota': 10.0, 'comentari': ''},
        ]
    }
    
    summary = get_student_summary(student)
    
    assert summary['total_subjects'] == 5
    assert summary['passed'] == 2
    assert summary['failed'] == 1
    assert summary['pending'] == 1
    assert summary['convalidated'] == 1
    assert summary['avg_grade'] == 7.75  # (8.0 + 7.5) / 2


def test_calculate_subject_statistics():
    """Test subject statistics calculation"""
    students = [
        {
            'id': '1',
            'nom_cognoms': 'Student 1',
            'materies': [
                {'materia': 'Math', 'qualificacio_status': 'Assolit', 'nota': 8.0, 'comentari': ''},
            ]
        },
        {
            'id': '2',
            'nom_cognoms': 'Student 2',
            'materies': [
                {'materia': 'Math', 'qualificacio_status': 'Assolit', 'nota': 9.0, 'comentari': ''},
            ]
        },
        {
            'id': '3',
            'nom_cognoms': 'Student 3',
            'materies': [
                {'materia': 'Math', 'qualificacio_status': 'No assolit', 'nota': 0.0, 'comentari': ''},
            ]
        },
    ]
    
    stats = calculate_subject_statistics(students, 'Math')
    
    assert stats['subject'] == 'Math'
    assert stats['count_total'] == 3
    assert stats['count_assolit'] == 2
    assert stats['count_no_assolit'] == 1
    assert stats['avg_grade'] == 8.5  # (8.0 + 9.0) / 2


def test_load_acta_csv_basic():
    """Test basic CSV loading"""
    # Create a temporary CSV file
    csv_content = """n|id|nom_cognoms|tipus_document|document_id|nivell|grup_codi|data_sessio_avaluacio|numero_avaluacio|codi_ensenyament|nom_ensenyament|m1|q1|c1|m2|q2|c2|m3|q3|c3|comentari general
1|123|Test Student|DNI|12345678A|1|DAW101|2025-06-19|4|DAW|Desenvolupament Aplicacions Web|Math|Assolit-8|Good work|Physics|Assolit-7|Average|Chemistry|No assolit|Needs improvement|Good student overall"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
        tmp_file.write(csv_content)
        tmp_path = tmp_file.name
    
    try:
        data = load_acta_csv(tmp_path)
        
        # Check metadata
        assert data['metadata']['grup_codi'] == 'DAW101'
        assert data['metadata']['numero_avaluacio'] == '4'
        
        # Check students
        assert len(data['students']) == 1
        student = data['students'][0]
        assert student['id'] == '123'
        assert student['nom_cognoms'] == 'Test Student'
        assert len(student['materies']) == 3
        
        # Check subjects
        assert 'Math' in data['subjects']
        assert 'Physics' in data['subjects']
        assert 'Chemistry' in data['subjects']
        
        # Check first subject details
        math = student['materies'][0]
        assert math['materia'] == 'Math'
        assert math['qualificacio_status'] == 'Assolit'
        assert math['nota'] == 8.0
        assert math['comentari'] == 'Good work'
        
    finally:
        os.unlink(tmp_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
