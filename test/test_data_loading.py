"""
High-priority tests for data loading functionality
"""
import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch
import pandas as pd

from app import load_json_files, load_uploaded_json_files, compare_versions


class TestVersionComparison:
    """Test version comparison functionality"""
    
    def test_compare_versions_equal(self):
        """Test comparing equal versions"""
        assert compare_versions("1.0.0", "1.0.0") == 0
        assert compare_versions("2.1.3", "2.1.3") == 0
    
    def test_compare_versions_less_than(self):
        """Test comparing versions where first is less than second"""
        assert compare_versions("1.0.0", "1.0.1") == -1
        assert compare_versions("1.9.0", "2.0.0") == -1
        assert compare_versions("0.9.9", "1.0.0") == -1
    
    def test_compare_versions_greater_than(self):
        """Test comparing versions where first is greater than second"""
        assert compare_versions("1.0.1", "1.0.0") == 1
        assert compare_versions("2.0.0", "1.9.9") == 1
        assert compare_versions("1.1.0", "1.0.9") == 1
    
    def test_compare_versions_with_different_lengths(self):
        """Test comparing versions with different number of components"""
        assert compare_versions("1.0", "1.0.0") == -1
        assert compare_versions("1.0.0", "1.0") == 1
        assert compare_versions("1", "1.0.0") == -1


class TestJSONFileLoading:
    """Test JSON file loading functionality"""
    
    def test_load_new_structure_json(self, temp_test_dir, sample_json_structure):
        """Test loading JSON with new structure (grup, trimestre, estudiants)"""
        # Create test file
        test_file = os.path.join(temp_test_dir, "test_new.json")
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(sample_json_structure, f, ensure_ascii=False, indent=2)
        
        # Load file
        students, file_info, version_warnings = load_json_files(temp_test_dir, ["test_new.json"])
        
        # Assertions
        assert len(students) == 1
        assert students[0]['id'] == "12345"
        assert students[0]['nom_cognoms'] == "Joan Pérez García"
        assert students[0]['grup'] == "3B"
        assert students[0]['trimestre'] == "Primer trimestre"
        assert students[0]['file_display_name'] == "3B_Primer trimestre"
        assert len(students[0]['materies']) == 1
        
        # Check file info
        assert "test_new.json" in file_info
        assert file_info["test_new.json"]["display_name"] == "3B_Primer trimestre"
        assert file_info["test_new.json"]["grup"] == "3B"
        assert file_info["test_new.json"]["trimestre"] == "Primer trimestre"
        assert file_info["test_new.json"]["version"] == "1.0.0"
        
        # No version warnings for compatible version
        assert len(version_warnings) == 0
    
    def test_load_old_structure_json(self, temp_test_dir, sample_old_json_structure):
        """Test loading JSON with old structure (direct array)"""
        # Create test file
        test_file = os.path.join(temp_test_dir, "T1.json")
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(sample_old_json_structure, f, ensure_ascii=False, indent=2)
        
        # Load file
        students, file_info, version_warnings = load_json_files(temp_test_dir, ["T1.json"])
        
        # Assertions
        assert len(students) == 1
        assert students[0]['id'] == "12345"
        assert students[0]['grup'] == "Grup Antic"
        assert students[0]['trimestre'] == "T1"
        assert students[0]['file_display_name'] == "Grup_Antic_T1"
        
        # Check file info
        assert "T1.json" in file_info
        assert file_info["T1.json"]["display_name"] == "Grup_Antic_T1"
        assert file_info["T1.json"]["version"] == "0.0.0"
        
        # Should have warning for old format
        assert len(version_warnings) == 1
        assert "Format antic" in version_warnings[0]
    
    def test_load_json_with_null_students(self, temp_test_dir):
        """Test loading JSON with students having NULL IDs"""
        json_data = {
            "grup": "3B",
            "trimestre": "Primer trimestre",
            "estudiants": [
                {
                    "id": "NULL",
                    "nom_cognoms": "Student with NULL ID",
                    "materies": []
                },
                {
                    "id": "",
                    "nom_cognoms": "Student with empty ID",
                    "materies": []
                },
                {
                    "id": "12345",
                    "nom_cognoms": "Valid Student",
                    "materies": []
                }
            ],
            "metrika_version": "1.0.0"
        }
        
        # Create test file
        test_file = os.path.join(temp_test_dir, "test_null.json")
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        # Load file
        students, file_info, version_warnings = load_json_files(temp_test_dir, ["test_null.json"])
        
        # Should only load valid students
        assert len(students) == 1
        assert students[0]['id'] == "12345"
        assert students[0]['nom_cognoms'] == "Valid Student"
    
    def test_load_corrupted_json(self, temp_test_dir):
        """Test loading corrupted JSON file"""
        # Create corrupted file
        test_file = os.path.join(temp_test_dir, "corrupted.json")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("{ invalid json }")
        
        # Load file - should handle error gracefully
        students, file_info, version_warnings = load_json_files(temp_test_dir, ["corrupted.json"])
        
        # Should return empty results
        assert len(students) == 0
        assert len(file_info) == 0
    
    def test_load_nonexistent_file(self, temp_test_dir):
        """Test loading non-existent file"""
        students, file_info, version_warnings = load_json_files(temp_test_dir, ["nonexistent.json"])
        
        # Should return empty results
        assert len(students) == 0
        assert len(file_info) == 0
    
    def test_version_compatibility_warnings(self, temp_test_dir):
        """Test version compatibility warnings"""
        # Test old version
        old_version_data = {
            "grup": "3B",
            "trimestre": "Primer trimestre",
            "estudiants": [],
            "metrika_version": "0.9.0"
        }
        
        old_file = os.path.join(temp_test_dir, "old_version.json")
        with open(old_file, 'w', encoding='utf-8') as f:
            json.dump(old_version_data, f, ensure_ascii=False, indent=2)
        
        students, file_info, version_warnings = load_json_files(temp_test_dir, ["old_version.json"])
        
        # Should have warning for old version
        assert len(version_warnings) == 1
        assert "anterior a la versió mínima compatible" in version_warnings[0]
        
        # Test future version
        future_version_data = {
            "grup": "3B",
            "trimestre": "Primer trimestre",
            "estudiants": [],
            "metrika_version": "2.0.0"
        }
        
        future_file = os.path.join(temp_test_dir, "future_version.json")
        with open(future_file, 'w', encoding='utf-8') as f:
            json.dump(future_version_data, f, ensure_ascii=False, indent=2)
        
        students, file_info, version_warnings = load_json_files(temp_test_dir, ["future_version.json"])
        
        # Should have warning for future version
        assert len(version_warnings) == 1
        assert "posterior a la versió actual" in version_warnings[0]


class TestUploadedFileLoading:
    """Test uploaded file loading functionality"""
    
    def test_load_uploaded_json_files(self, mock_uploaded_file):
        """Test loading uploaded JSON files"""
        students, file_info, version_warnings = load_uploaded_json_files([mock_uploaded_file])
        
        # Assertions
        assert len(students) == 1
        assert students[0]['id'] == "12345"
        assert students[0]['nom_cognoms'] == "Joan Pérez García"
        assert students[0]['grup'] == "3B"
        assert students[0]['trimestre'] == "Primer trimestre"
        
        # Check file info
        assert "test_file.json" in file_info
        assert file_info["test_file.json"]["display_name"] == "3B_Primer trimestre"
    
    def test_load_multiple_uploaded_files(self):
        """Test loading multiple uploaded files"""
        # Create mock files
        mock_file1 = Mock()
        mock_file1.name = "T1.json"
        mock_file1.read.return_value = json.dumps({
            "grup": "3B",
            "trimestre": "Primer trimestre",
            "estudiants": [{"id": "1", "nom_cognoms": "Student 1", "materies": []}],
            "metrika_version": "1.0.0"
        }).encode('utf-8')
        mock_file1.seek = Mock()
        
        mock_file2 = Mock()
        mock_file2.name = "T2.json"
        mock_file2.read.return_value = json.dumps({
            "grup": "3B",
            "trimestre": "Segon trimestre",
            "estudiants": [{"id": "2", "nom_cognoms": "Student 2", "materies": []}],
            "metrika_version": "1.0.0"
        }).encode('utf-8')
        mock_file2.seek = Mock()
        
        students, file_info, version_warnings = load_uploaded_json_files([mock_file1, mock_file2])
        
        # Should load both files
        assert len(students) == 2
        assert len(file_info) == 2
        assert "T1.json" in file_info
        assert "T2.json" in file_info
    
    def test_load_uploaded_file_with_error(self):
        """Test loading uploaded file that causes an error"""
        mock_file = Mock()
        mock_file.name = "error.json"
        mock_file.read.side_effect = Exception("Test error")
        mock_file.seek = Mock()
        
        students, file_info, version_warnings = load_uploaded_json_files([mock_file])
        
        # Should handle error gracefully
        assert len(students) == 0
        assert len(file_info) == 0


class TestDataValidation:
    """Test data validation functionality"""
    
    def test_student_id_validation(self, temp_test_dir):
        """Test validation of student IDs"""
        json_data = {
            "grup": "3B",
            "trimestre": "Primer trimestre",
            "estudiants": [
                {"id": "12345", "nom_cognoms": "Valid", "materies": []},
                {"id": "NULL", "nom_cognoms": "Invalid NULL", "materies": []},
                {"id": "", "nom_cognoms": "Invalid empty", "materies": []},
                {"id": None, "nom_cognoms": "Invalid None", "materies": []}
            ],
            "metrika_version": "1.0.0"
        }
        
        test_file = os.path.join(temp_test_dir, "validation_test.json")
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        students, file_info, version_warnings = load_json_files(temp_test_dir, ["validation_test.json"])
        
        # Should only include valid students
        assert len(students) == 1
        assert students[0]['id'] == "12345"
    
    def test_required_fields_validation(self, temp_test_dir):
        """Test validation of required fields"""
        json_data = {
            "grup": "3B",
            "trimestre": "Primer trimestre",
            "estudiants": [
                {
                    "id": "12345",
                    "nom_cognoms": "Valid Student",
                    "materies": [
                        {
                            "materia": "Math",
                            "qualificacio": "Assoliment notable",
                            "comentari": "Good work"
                        }
                    ]
                }
            ],
            "metrika_version": "1.0.0"
        }
        
        test_file = os.path.join(temp_test_dir, "required_fields_test.json")
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        students, file_info, version_warnings = load_json_files(temp_test_dir, ["required_fields_test.json"])
        
        # Should load successfully with all required fields
        assert len(students) == 1
        student = students[0]
        assert 'id' in student
        assert 'nom_cognoms' in student
        assert 'materies' in student
        assert len(student['materies']) == 1
        assert 'materia' in student['materies'][0]
        assert 'qualificacio' in student['materies'][0]
        assert 'comentari' in student['materies'][0] 