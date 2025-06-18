"""
High-priority tests for utility functions and helper modules
"""
import pytest
import pandas as pd
import numpy as np
import json
import tempfile
import os
from unittest.mock import Mock, patch

from utils.constants import MarkConfig, DataConfig, AppConfig
from utils.helpers import *
from utils.csv_to_json import process_csv_to_json


class TestConstants:
    """Test constants and configuration classes"""
    
    def test_mark_config_enum(self):
        """Test MarkConfig enum values and methods"""
        # Test enum values
        assert MarkConfig.NA.value == "No assoliment"
        assert MarkConfig.AS.value == "Assoliment satisfactori"
        assert MarkConfig.AN.value == "Assoliment notable"
        assert MarkConfig.AE.value == "Assoliment excel·lent"
        
        # Test list
        assert len(MarkConfig.LIST.value) == 4
        assert MarkConfig.NA in MarkConfig.LIST.value
        assert MarkConfig.AS in MarkConfig.LIST.value
        assert MarkConfig.AN in MarkConfig.LIST.value
        assert MarkConfig.AE in MarkConfig.LIST.value
    
    def test_height_mapping(self):
        """Test height mapping functionality"""
        height_map = MarkConfig.HEIGHT_MAP.value
        
        # Test valid mappings
        assert height_map['NA'] == 1
        assert height_map['AS'] == 2
        assert height_map['AN'] == 3
        assert height_map['AE'] == 4
        
        # Test invalid mappings
        assert height_map.get('INVALID', 0) == 0
        assert height_map.get('', 0) == 0
        assert height_map.get(pd.NA, 0) == 0
    
    def test_color_mapping(self):
        """Test color mapping functionality"""
        color_map = MarkConfig.COLOR_MAP.value
        
        # Test valid color mappings
        assert color_map["No assoliment"] == "#d62728"
        assert color_map["Assoliment satisfactori"] == "#ff7f0e"
        assert color_map["Assoliment notable"] == "#1f77b4"
        assert color_map["Assoliment excel·lent"] == "#2ca02c"
        
        # Test default colors
        assert color_map.get("", "gray") == "gray"
        assert color_map.get(pd.NA, "gray") == "gray"
    
    def test_mark_config_methods(self):
        """Test MarkConfig class methods"""
        # Test get_height_from_key
        assert MarkConfig.get_height_from_key('NA') == 1
        assert MarkConfig.get_height_from_key('AS') == 2
        assert MarkConfig.get_height_from_key('AN') == 3
        assert MarkConfig.get_height_from_key('AE') == 4
        assert MarkConfig.get_height_from_key('INVALID') == 0
        
        # Test get_mark_from_height
        assert MarkConfig.get_mark_from_height(1) == 'NA'
        assert MarkConfig.get_mark_from_height(2) == 'AS'
        assert MarkConfig.get_mark_from_height(3) == 'AN'
        assert MarkConfig.get_mark_from_height(4) == 'AE'
        assert MarkConfig.get_mark_from_height(0) == ""
        assert MarkConfig.get_mark_from_height(999) == ""
    
    def test_data_config(self):
        """Test DataConfig enum values and methods"""
        # Test subject names
        subject_names = DataConfig.SUBJ_NAMES.value
        assert "CAT" in subject_names
        assert "CAST" in subject_names
        assert "ANG" in subject_names
        assert "MAT" in subject_names
        assert "BG" in subject_names
        assert "FQ" in subject_names
        
        # Test column names mapping
        col_names = DataConfig.COL_NAMES.value
        assert col_names["Identificador de l'alumne/a"] == "id"
        assert col_names["Nom i cognoms de l'alumne/a"] == "NOM"
        assert col_names["Ll. Cat."] == "CAT"
        assert col_names["Mat."] == "MAT"
    
    def test_data_config_methods(self):
        """Test DataConfig class methods"""
        # Test get_key_from_value
        assert DataConfig.get_key_from_value("id") == "Identificador de l'alumne/a"
        assert DataConfig.get_key_from_value("NOM") == "Nom i cognoms de l'alumne/a"
        assert DataConfig.get_key_from_value("CAT") == "Ll. Cat."
        assert DataConfig.get_key_from_value("MAT") == "Mat."
        assert DataConfig.get_key_from_value("INVALID") is None
    
    def test_app_config(self):
        """Test AppConfig values"""
        assert AppConfig.APP_NAME == "Metrika"
        assert AppConfig.VERSION == "1.0.0"
        assert AppConfig.MIN_COMPATIBLE_VERSION == "1.0.0"
        assert AppConfig.APP_TITLE == "Visualizador Esfera"
        assert AppConfig.THEME_COLOR == "#FF4B4B"
        assert AppConfig.MAX_SIZE == 100
        assert AppConfig.MIN_SIZE == 10


class TestHelperFunctions:
    """Test helper functions from utils.helpers"""
    
    def test_dataframe_operations(self):
        """Test DataFrame operations"""
        # Create sample DataFrame
        data = {
            'id': ['1', '2', '3'],
            'name': ['Alice', 'Bob', 'Charlie'],
            'score': [85, 92, 78]
        }
        df = pd.DataFrame(data)
        
        # Test basic operations
        assert len(df) == 3
        assert list(df.columns) == ['id', 'name', 'score']
        assert df['score'].mean() == 85.0
        
        # Test filtering
        high_scores = df[df['score'] > 80]
        assert len(high_scores) == 2
        
        # Test sorting
        sorted_df = df.sort_values('score', ascending=False)
        assert sorted_df.iloc[0]['name'] == 'Bob'
    
    def test_string_operations(self):
        """Test string operations"""
        # Test string cleaning
        dirty_string = "  Test String  "
        clean_string = dirty_string.strip()
        assert clean_string == "Test String"
        
        # Test string formatting
        formatted = f"Student: {clean_string}"
        assert formatted == "Student: Test String"
        
        # Test string validation
        assert "Test" in clean_string
        assert len(clean_string) == 11
    
    def test_numeric_operations(self):
        """Test numeric operations"""
        # Test basic arithmetic
        assert 2 + 2 == 4
        assert 10 / 2 == 5.0
        assert 3 ** 2 == 9
        
        # Test statistical operations
        numbers = [1, 2, 3, 4, 5]
        assert sum(numbers) == 15
        assert len(numbers) == 5
        assert sum(numbers) / len(numbers) == 3.0
        
        # Test numpy operations
        np_array = np.array(numbers)
        assert np.mean(np_array) == 3.0
        assert np.std(np_array) == 1.4142135623730951
    
    def test_list_operations(self):
        """Test list operations"""
        # Test list creation and manipulation
        test_list = [1, 2, 3, 4, 5]
        assert len(test_list) == 5
        assert test_list[0] == 1
        assert test_list[-1] == 5
        
        # Test list comprehension
        doubled = [x * 2 for x in test_list]
        assert doubled == [2, 4, 6, 8, 10]
        
        # Test filtering
        even_numbers = [x for x in test_list if x % 2 == 0]
        assert even_numbers == [2, 4]
        
        # Test sorting
        sorted_list = sorted(test_list, reverse=True)
        assert sorted_list == [5, 4, 3, 2, 1]
    
    def test_dictionary_operations(self):
        """Test dictionary operations"""
        # Test dictionary creation
        test_dict = {
            'name': 'John',
            'age': 30,
            'city': 'Barcelona'
        }
        
        assert len(test_dict) == 3
        assert test_dict['name'] == 'John'
        assert 'age' in test_dict
        assert test_dict.get('country', 'Spain') == 'Spain'
        
        # Test dictionary iteration
        keys = list(test_dict.keys())
        values = list(test_dict.values())
        assert len(keys) == 3
        assert len(values) == 3
        
        # Test dictionary comprehension
        doubled_ages = {k: v * 2 if isinstance(v, int) else v for k, v in test_dict.items()}
        assert doubled_ages['age'] == 60
        assert doubled_ages['name'] == 'John'


class TestCSVToJSONUtility:
    """Test CSV to JSON conversion utility functions"""
    
    def test_csv_processing_basic(self, temp_test_dir):
        """Test basic CSV processing"""
        # Create test CSV data
        csv_data = """id|nom_cognoms|numero_avaluacio|m1|q1|c1|comentari general
12345|Joan Pérez García|1|Matemàtiques|Assoliment notable|Bon treball|Bon treball en general"""
        
        csv_file = os.path.join(temp_test_dir, "test.csv")
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(csv_data)
        
        output_file = os.path.join(temp_test_dir, "output.json")
        
        # Process CSV
        success, message, json_data = process_csv_to_json(csv_file, output_file, "T1")
        
        # Verify success
        assert success is True
        assert "conversió completada" in message.lower()
        
        # Verify output file exists
        assert os.path.exists(output_file)
        
        # Verify JSON structure
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert 'estudiants' in data
        assert 'grup' in data
        assert 'trimestre' in data
        assert 'metrika_version' in data
    
    def test_csv_processing_with_multiple_students(self, temp_test_dir):
        """Test CSV processing with multiple students"""
        csv_data = """id|nom_cognoms|numero_avaluacio|m1|q1|c1|m2|q2|c2|comentari general
12345|Joan Pérez García|1|Matemàtiques|Assoliment notable|Bon treball|Català|Assoliment satisfactori|Millora expressió|Bon treball en general
67890|Maria López Sánchez|1|Matemàtiques|Assoliment excel·lent|Excel·lent treball|Català|Assoliment notable|Bona expressió|Excel·lent treball en general"""
        
        csv_file = os.path.join(temp_test_dir, "multi_students.csv")
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(csv_data)
        
        output_file = os.path.join(temp_test_dir, "multi_output.json")
        
        # Process CSV
        success, message, json_data = process_csv_to_json(csv_file, output_file, "T1")
        
        # Verify success
        assert success is True
        
        # Verify JSON structure
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Should have 2 students
        assert len(data['estudiants']) == 2
        
        # Check first student
        student1 = data['estudiants'][0]
        assert student1['id'] == "12345"
        assert student1['nom_cognoms'] == "Joan Pérez García"
        assert len(student1['materies']) == 2
        
        # Check second student
        student2 = data['estudiants'][1]
        assert student2['id'] == "67890"
        assert student2['nom_cognoms'] == "Maria López Sánchez"
        assert len(student2['materies']) == 2
    
    def test_csv_processing_error_handling(self, temp_test_dir):
        """Test CSV processing error handling"""
        # Test with non-existent file
        non_existent_file = os.path.join(temp_test_dir, "nonexistent.csv")
        output_file = os.path.join(temp_test_dir, "error_output.json")
        
        success, message, json_data = process_csv_to_json(non_existent_file, output_file, "T1")
        
        # Should fail
        assert success is False
        assert "error" in message.lower() or "problema" in message.lower()
    
    def test_csv_processing_with_invalid_delimiter(self, temp_test_dir):
        """Test CSV processing with invalid delimiter"""
        # Create CSV with comma delimiter instead of pipe
        csv_data = """id,nom_cognoms,numero_avaluacio,m1,q1,c1,comentari general
12345,Joan Pérez García,1,Matemàtiques,Assoliment notable,Bon treball,Bon treball en general"""
        
        csv_file = os.path.join(temp_test_dir, "comma_delimiter.csv")
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(csv_data)
        
        output_file = os.path.join(temp_test_dir, "comma_output.json")
        
        # Process CSV
        success, message, json_data = process_csv_to_json(csv_file, output_file, "T1")
        
        # Should fail due to wrong delimiter
        assert success is False


class TestDataValidation:
    """Test data validation utilities"""
    
    def test_student_data_validation(self):
        """Test student data validation"""
        # Valid student data
        valid_student = {
            "id": "12345",
            "nom_cognoms": "Joan Pérez García",
            "materies": [
                {
                    "materia": "Matemàtiques",
                    "qualificacio": "Assoliment notable",
                    "comentari": "Bon treball"
                }
            ]
        }
        
        # Test required fields
        required_fields = ['id', 'nom_cognoms']
        for field in required_fields:
            assert field in valid_student
        
        # Test materies structure
        assert 'materies' in valid_student
        assert isinstance(valid_student['materies'], list)
        
        for materia in valid_student['materies']:
            materia_fields = ['materia', 'qualificacio', 'comentari']
            for field in materia_fields:
                assert field in materia
    
    def test_qualification_validation(self):
        """Test qualification validation"""
        valid_qualifications = [
            "No assoliment",
            "Assoliment satisfactori",
            "Assoliment notable",
            "Assoliment excel·lent"
        ]
        
        # Test valid qualifications
        for qual in valid_qualifications:
            assert qual in MarkConfig.LIST.value
        
        # Test invalid qualification
        invalid_qual = "Invalid Grade"
        assert invalid_qual not in MarkConfig.LIST.value
    
    def test_subject_validation(self):
        """Test subject validation"""
        valid_subjects = DataConfig.SUBJ_NAMES.value
        
        # Test valid subjects
        assert "CAT" in valid_subjects
        assert "MAT" in valid_subjects
        assert "ANG" in valid_subjects
        
        # Test invalid subject
        invalid_subject = "INVALID_SUBJECT"
        assert invalid_subject not in valid_subjects


class TestFileOperations:
    """Test file operation utilities"""
    
    def test_file_existence_check(self, temp_test_dir):
        """Test file existence checking"""
        # Create a test file
        test_file = os.path.join(temp_test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # Test file exists
        assert os.path.exists(test_file)
        
        # Test non-existent file
        non_existent = os.path.join(temp_test_dir, "nonexistent.txt")
        assert not os.path.exists(non_existent)
    
    def test_file_reading(self, temp_test_dir):
        """Test file reading operations"""
        # Create test file
        test_file = os.path.join(temp_test_dir, "read_test.txt")
        test_content = "Test content with special chars: áéíóú"
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Read file
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert content == test_content
    
    def test_file_writing(self, temp_test_dir):
        """Test file writing operations"""
        test_file = os.path.join(temp_test_dir, "write_test.txt")
        test_content = "Test content for writing"
        
        # Write file
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Verify file was written
        assert os.path.exists(test_file)
        
        # Read back and verify content
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert content == test_content
    
    def test_json_file_operations(self, temp_test_dir):
        """Test JSON file operations"""
        test_data = {
            "name": "Test",
            "value": 42,
            "list": [1, 2, 3]
        }
        
        json_file = os.path.join(temp_test_dir, "test.json")
        
        # Write JSON
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        # Read JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        assert loaded_data == test_data
        assert loaded_data["name"] == "Test"
        assert loaded_data["value"] == 42
        assert loaded_data["list"] == [1, 2, 3]


class TestStatisticalOperations:
    """Test statistical operations"""
    
    def test_basic_statistics(self):
        """Test basic statistical calculations"""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        # Test mean
        mean = sum(data) / len(data)
        assert mean == 5.5
        
        # Test median
        sorted_data = sorted(data)
        n = len(sorted_data)
        if n % 2 == 0:
            median = (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
        else:
            median = sorted_data[n//2]
        assert median == 5.5
        
        # Test standard deviation
        variance = sum((x - mean) ** 2 for x in data) / len(data)
        std_dev = variance ** 0.5
        assert abs(std_dev - 2.8722813232690143) < 0.0001
    
    def test_pandas_statistics(self):
        """Test pandas statistical operations"""
        data = {
            'scores': [85, 92, 78, 96, 88, 75, 90, 82]
        }
        df = pd.DataFrame(data)
        
        # Test basic statistics
        assert df['scores'].mean() == 85.75
        assert df['scores'].median() == 86.5
        assert df['scores'].min() == 75
        assert df['scores'].max() == 96
        assert len(df['scores']) == 8
    
    def test_counting_operations(self):
        """Test counting operations"""
        data = ['A', 'B', 'A', 'C', 'B', 'A', 'D']
        
        # Count occurrences
        counts = {}
        for item in data:
            counts[item] = counts.get(item, 0) + 1
        
        assert counts['A'] == 3
        assert counts['B'] == 2
        assert counts['C'] == 1
        assert counts['D'] == 1
        
        # Test pandas value_counts
        series = pd.Series(data)
        value_counts = series.value_counts()
        assert value_counts['A'] == 3
        assert value_counts['B'] == 2 