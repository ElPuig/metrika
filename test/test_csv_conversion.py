"""
High-priority tests for CSV to JSON conversion functionality
"""
import pytest
import json
import os
import tempfile
import pandas as pd
from unittest.mock import Mock, patch

from utils.csv_to_json import process_csv_to_json
from utils.constants import DataConfig, AppConfig


class TestCSVToJSONConversion:
    """Test CSV to JSON conversion functionality"""
    
    def test_basic_csv_conversion(self, temp_test_dir, sample_csv_data):
        """Test basic CSV to JSON conversion"""
        # Create test CSV file
        csv_file = os.path.join(temp_test_dir, "test_data.csv")
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(sample_csv_data)
        
        # Define output file
        output_file = os.path.join(temp_test_dir, "test_output.json")
        
        # Convert CSV to JSON
        success, message, json_data = process_csv_to_json(csv_file, output_file, "T1")
        
        # Assertions
        assert success is True
        assert "conversió completada" in message.lower()
        
        # Load and validate JSON
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check structure
        assert isinstance(data, dict)
        assert 'estudiants' in data
        assert 'grup' in data
        assert 'trimestre' in data
        assert 'metrika_version' in data
        
        # Check students
        students = data['estudiants']
        assert len(students) == 2
        
        # Check first student
        student1 = students[0]
        assert student1['id'] == "12345"
        assert student1['nom_cognoms'] == "Joan Pérez García"
        assert len(student1['materies']) == 5  # 5 subjects
        
        # Check subjects
        subjects = [m['materia'] for m in student1['materies']]
        assert "Matemàtiques" in subjects
        assert "Català" in subjects
        assert "Història" in subjects
        assert "Física" in subjects
        assert "Anglès" in subjects
    
    def test_csv_conversion_with_old_format(self, temp_test_dir):
        """Test CSV conversion with old format (direct array output)"""
        csv_data = """id|nom_cognoms|numero_avaluacio|m1|q1|c1|m2|q2|c2|comentari general
12345|Joan Pérez García|1|Matemàtiques|Assoliment notable|Bon treball|Català|Assoliment satisfactori|Millora expressió|Bon treball en general"""
        
        # Create test CSV file
        csv_file = os.path.join(temp_test_dir, "old_format.csv")
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(csv_data)
        
        # Define output file
        output_file = os.path.join(temp_test_dir, "old_format_output.json")
        
        # Convert CSV to JSON with old format
        success, message, json_data = process_csv_to_json(csv_file, output_file, "T1", new_format=False)
        
        # Assertions
        assert success is True
        
        # Load and validate JSON
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Should be direct array (old format)
        assert isinstance(data, list)
        assert len(data) == 1
        
        # Check student data
        student = data[0]
        assert student['id'] == "12345"
        assert student['nom_cognoms'] == "Joan Pérez García"
        assert len(student['materies']) == 2
    
    def test_csv_conversion_with_missing_columns(self, temp_test_dir):
        """Test CSV conversion with missing columns"""
        csv_data = """id|nom_cognoms|numero_avaluacio|m1|q1|c1|comentari general
12345|Joan Pérez García|1|Matemàtiques|Assoliment notable|Bon treball|Bon treball en general"""
        
        # Create test CSV file
        csv_file = os.path.join(temp_test_dir, "missing_columns.csv")
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(csv_data)
        
        # Define output file
        output_file = os.path.join(temp_test_dir, "missing_columns_output.json")
        
        # Convert CSV to JSON
        success, message, json_data = process_csv_to_json(csv_file, output_file, "T1")
        
        # Should still succeed with partial data
        assert success is True
        
        # Load and validate JSON
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check structure
        assert 'estudiants' in data
        students = data['estudiants']
        assert len(students) == 1
        
        # Check student has at least one subject
        student = students[0]
        assert len(student['materies']) >= 1
    
    def test_csv_conversion_with_empty_file(self, temp_test_dir):
        """Test CSV conversion with empty file"""
        # Create empty CSV file
        csv_file = os.path.join(temp_test_dir, "empty.csv")
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        # Define output file
        output_file = os.path.join(temp_test_dir, "empty_output.json")
        
        # Convert CSV to JSON
        success, message, json_data = process_csv_to_json(csv_file, output_file, "T1")
        
        # Should fail gracefully
        assert success is False
        assert "error" in message.lower() or "problema" in message.lower()
    
    def test_csv_conversion_with_invalid_delimiter(self, temp_test_dir):
        """Test CSV conversion with invalid delimiter"""
        csv_data = """id,nom_cognoms,numero_avaluacio,m1,q1,c1,comentari general
12345,Joan Pérez García,1,Matemàtiques,Assoliment notable,Bon treball,Bon treball en general"""
        
        # Create test CSV file with comma delimiter
        csv_file = os.path.join(temp_test_dir, "comma_delimiter.csv")
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(csv_data)
        
        # Define output file
        output_file = os.path.join(temp_test_dir, "comma_output.json")
        
        # Convert CSV to JSON
        success, message, json_data = process_csv_to_json(csv_file, output_file, "T1")
        
        # Should fail due to wrong delimiter
        assert success is False
    
    def test_csv_conversion_with_special_characters(self, temp_test_dir):
        """Test CSV conversion with special characters and accents"""
        csv_data = """id|nom_cognoms|numero_avaluacio|m1|q1|c1|comentari general
12345|Joan Pérez-García|1|Matemàtiques|Assoliment excel·lent|Excel·lent treball|Bon treball en general"""
        
        # Create test CSV file
        csv_file = os.path.join(temp_test_dir, "special_chars.csv")
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(csv_data)
        
        # Define output file
        output_file = os.path.join(temp_test_dir, "special_chars_output.json")
        
        # Convert CSV to JSON
        success, message, json_data = process_csv_to_json(csv_file, output_file, "T1")
        
        # Should succeed
        assert success is True
        
        # Load and validate JSON
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check special characters are preserved
        student = data['estudiants'][0]
        assert student['nom_cognoms'] == "Joan Pérez-García"
        assert student['materies'][0]['qualificacio'] == "Assoliment excel·lent"
        assert "Excel·lent" in student['materies'][0]['comentari']
    
    def test_csv_conversion_with_null_values(self, temp_test_dir):
        """Test CSV conversion with NULL values"""
        csv_data = """id|nom_cognoms|numero_avaluacio|m1|q1|c1|m2|q2|c2|comentari general
12345|Joan Pérez García|1|Matemàtiques|Assoliment notable|Bon treball|||NULL|Bon treball en general"""
        
        # Create test CSV file
        csv_file = os.path.join(temp_test_dir, "null_values.csv")
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(csv_data)
        
        # Define output file
        output_file = os.path.join(temp_test_dir, "null_values_output.json")
        
        # Convert CSV to JSON
        success, message, json_data = process_csv_to_json(csv_file, output_file, "T1")
        
        # Should succeed
        assert success is True
        
        # Load and validate JSON
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check that only valid subjects are included
        student = data['estudiants'][0]
        assert len(student['materies']) == 1  # Only Matemàtiques should be included
        assert student['materies'][0]['materia'] == "Matemàtiques"


class TestCSVDataValidation:
    """Test CSV data validation functionality"""
    
    def test_subject_mapping_validation(self, temp_test_dir):
        """Test validation of subject mapping"""
        csv_data = """id|nom_cognoms|numero_avaluacio|m1|q1|c1|m2|q2|c2|comentari general
12345|Joan Pérez García|1|Ll. Cat.|Assoliment notable|Bon treball|Mat.|Assoliment satisfactori|Millora expressió|Bon treball en general"""
        
        # Create test CSV file
        csv_file = os.path.join(temp_test_dir, "subject_mapping.csv")
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(csv_data)
        
        # Define output file
        output_file = os.path.join(temp_test_dir, "subject_mapping_output.json")
        
        # Convert CSV to JSON
        success, message, json_data = process_csv_to_json(csv_file, output_file, "T1")
        
        # Should succeed
        assert success is True
        
        # Load and validate JSON
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check subject mapping
        student = data['estudiants'][0]
        subjects = [m['materia'] for m in student['materies']]
        
        # Should map to short names
        assert "CAT" in subjects  # Ll. Cat. -> CAT
        assert "MAT" in subjects  # Mat. -> MAT
    
    def test_qualification_validation(self, temp_test_dir):
        """Test validation of qualification values"""
        csv_data = """id|nom_cognoms|numero_avaluacio|m1|q1|c1|m2|q2|c2|comentari general
12345|Joan Pérez García|1|Matemàtiques|Assoliment notable|Bon treball|Català|Assoliment satisfactori|Millora expressió|Bon treball en general
67890|Maria López|1|Matemàtiques|Invalid Grade|Bad grade|Català|Assoliment excel·lent|Good work|Bon treball en general"""
        
        # Create test CSV file
        csv_file = os.path.join(temp_test_dir, "qualification_validation.csv")
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(csv_data)
        
        # Define output file
        output_file = os.path.join(temp_test_dir, "qualification_validation_output.json")
        
        # Convert CSV to JSON
        success, message, json_data = process_csv_to_json(csv_file, output_file, "T1")
        
        # Should succeed (invalid grades should be handled gracefully)
        assert success is True
        
        # Load and validate JSON
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check that both students are processed
        assert len(data['estudiants']) == 2
        
        # Check valid qualifications are preserved
        student1 = data['estudiants'][0]
        student2 = data['estudiants'][1]
        
        # Valid qualifications should be preserved
        valid_qualifications = [m['qualificacio'] for m in student1['materies']]
        assert "Assoliment notable" in valid_qualifications
        assert "Assoliment satisfactori" in valid_qualifications
        
        # Invalid qualifications should be handled (either filtered out or marked as invalid)
        student2_qualifications = [m['qualificacio'] for m in student2['materies']]
        # The exact handling depends on the implementation, but should not crash


class TestCSVErrorHandling:
    """Test CSV conversion error handling"""
    
    def test_csv_conversion_with_missing_file(self, temp_test_dir):
        """Test CSV conversion with missing file"""
        missing_file = os.path.join(temp_test_dir, "nonexistent.csv")
        output_file = os.path.join(temp_test_dir, "output.json")
        
        # Convert CSV to JSON
        success, message, json_data = process_csv_to_json(missing_file, output_file, "T1")
        
        # Should fail
        assert success is False
        assert "error" in message.lower() or "no existeix" in message.lower()
    
    def test_csv_conversion_with_permission_error(self, temp_test_dir):
        """Test CSV conversion with permission error on output file"""
        csv_data = """id|nom_cognoms|numero_avaluacio|m1|q1|c1|comentari general
12345|Joan Pérez García|1|Matemàtiques|Assoliment notable|Bon treball|Bon treball en general"""
        
        # Create test CSV file
        csv_file = os.path.join(temp_test_dir, "permission_test.csv")
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(csv_data)
        
        # Create a directory as output file (will cause permission error)
        output_file = os.path.join(temp_test_dir, "output_dir")
        os.makedirs(output_file, exist_ok=True)
        
        # Convert CSV to JSON
        success, message, json_data = process_csv_to_json(csv_file, output_file, "T1")
        
        # Should fail due to permission error
        assert success is False
    
    def test_csv_conversion_with_encoding_error(self, temp_test_dir):
        """Test CSV conversion with encoding error"""
        # Create test CSV file with invalid encoding
        csv_file = os.path.join(temp_test_dir, "encoding_test.csv")
        with open(csv_file, 'wb') as f:
            f.write(b"id|nom_cognoms|numero_avaluacio|m1|q1|c1|comentari general\n")
            f.write(b"12345|Joan P\xe9rez Garc\xeda|1|Matem\xe0tiques|Assoliment notable|Bon treball|Bon treball en general\n")
        
        # Define output file
        output_file = os.path.join(temp_test_dir, "encoding_output.json")
        
        # Convert CSV to JSON
        success, message, json_data = process_csv_to_json(csv_file, output_file, "T1")
        
        # Should fail due to encoding error
        assert success is False 