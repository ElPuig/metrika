"""
Basic test to verify the testing setup works correctly
"""
import pytest
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.constants import AppConfig, MarkConfig, DataConfig


class TestBasicSetup:
    """Test basic setup and imports"""
    
    def test_imports_work(self):
        """Test that all required modules can be imported"""
        # Test app imports
        try:
            from app import compare_versions, load_json_files
            assert compare_versions is not None
            assert load_json_files is not None
        except ImportError as e:
            pytest.fail(f"Failed to import app modules: {e}")
    
    def test_constants_available(self):
        """Test that constants are available and have correct values"""
        # Test AppConfig
        assert AppConfig.APP_NAME == "Metrika"
        assert AppConfig.VERSION == "1.0.0"
        assert AppConfig.MIN_COMPATIBLE_VERSION == "1.0.0"
        
        # Test MarkConfig
        assert MarkConfig.NA.value == "No assoliment"
        assert MarkConfig.AS.value == "Assoliment satisfactori"
        assert MarkConfig.AN.value == "Assoliment notable"
        assert MarkConfig.AE.value == "Assoliment excel·lent"
        
        # Test DataConfig
        assert "CAT" in DataConfig.SUBJ_NAMES.value
        assert "MAT" in DataConfig.SUBJ_NAMES.value
        assert "ANG" in DataConfig.SUBJ_NAMES.value
    
    def test_version_comparison(self):
        """Test version comparison function"""
        from app import compare_versions
        
        # Test equal versions
        assert compare_versions("1.0.0", "1.0.0") == 0
        
        # Test less than
        assert compare_versions("1.0.0", "1.0.1") == -1
        
        # Test greater than
        assert compare_versions("1.0.1", "1.0.0") == 1
    
    def test_mark_config_methods(self):
        """Test MarkConfig methods"""
        # Test height mapping
        assert MarkConfig.get_height_from_key('NA') == 1
        assert MarkConfig.get_height_from_key('AS') == 2
        assert MarkConfig.get_height_from_key('AN') == 3
        assert MarkConfig.get_height_from_key('AE') == 4
        
        # Test mark from height
        assert MarkConfig.get_mark_from_height(1) == 'NA'
        assert MarkConfig.get_mark_from_height(2) == 'AS'
        assert MarkConfig.get_mark_from_height(3) == 'AN'
        assert MarkConfig.get_mark_from_height(4) == 'AE'
    
    def test_data_config_methods(self):
        """Test DataConfig methods"""
        # Test column mapping
        assert DataConfig.get_key_from_value("id") == "Identificador de l'alumne/a"
        assert DataConfig.get_key_from_value("NOM") == "Nom i cognoms de l'alumne/a"
        assert DataConfig.get_key_from_value("CAT") == "Ll. Cat."
        assert DataConfig.get_key_from_value("MAT") == "Mat."
    
    def test_pytest_working(self):
        """Test that pytest is working correctly"""
        assert True  # This should always pass
    
    def test_fixtures_available(self, sample_students_data):
        """Test that fixtures are available"""
        assert sample_students_data is not None
        assert isinstance(sample_students_data, list)
        assert len(sample_students_data) > 0
        
        # Test first student structure
        first_student = sample_students_data[0]
        assert 'id' in first_student
        assert 'nom_cognoms' in first_student
        assert 'materies' in first_student
        assert isinstance(first_student['materies'], list)


class TestEnvironment:
    """Test environment setup"""
    
    def test_python_version(self):
        """Test Python version compatibility"""
        version = sys.version_info
        assert version.major == 3
        assert version.minor >= 8  # Require Python 3.8+
    
    def test_working_directory(self):
        """Test that we're in the correct working directory"""
        # Should be able to find the app.py file
        app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.py')
        assert os.path.exists(app_path), f"app.py not found at {app_path}"
    
    def test_test_directory_structure(self):
        """Test that test directory has required files"""
        test_dir = os.path.dirname(__file__)
        
        # Check for required test files
        required_files = [
            'conftest.py',
            'test_basic_setup.py',
            'test_data_loading.py',
            'test_csv_conversion.py',
            'test_visualization.py',
            'test_streamlit_integration.py',
            'test_utils.py'
        ]
        
        for file_name in required_files:
            file_path = os.path.join(test_dir, file_name)
            assert os.path.exists(file_path), f"Required test file {file_name} not found"
    
    def test_sample_data_files(self):
        """Test that sample data files exist"""
        test_dir = os.path.dirname(__file__)
        
        # Check for sample data files
        sample_files = [
            'test_data.csv',
            'test_with_version.json'
        ]
        
        for file_name in sample_files:
            file_path = os.path.join(test_dir, file_name)
            assert os.path.exists(file_path), f"Sample data file {file_name} not found"


if __name__ == "__main__":
    # Run basic tests
    print("🧪 Running basic setup tests...")
    
    # Test imports
    try:
        from utils.constants import AppConfig, MarkConfig, DataConfig
        print("✅ Imports successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        sys.exit(1)
    
    # Test constants
    try:
        assert AppConfig.APP_NAME == "Metrika"
        assert MarkConfig.NA.value == "No assoliment"
        print("✅ Constants test passed")
    except AssertionError as e:
        print(f"❌ Constants test failed: {e}")
        sys.exit(1)
    
    # Test version comparison
    try:
        from app import compare_versions
        assert compare_versions("1.0.0", "1.0.0") == 0
        print("✅ Version comparison test passed")
    except Exception as e:
        print(f"❌ Version comparison test failed: {e}")
        sys.exit(1)
    
    print("🎉 All basic tests passed!") 