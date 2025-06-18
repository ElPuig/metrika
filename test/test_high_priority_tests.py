#!/usr/bin/env python3
"""
Simple script to test the high-priority test setup
"""
import sys
import os
import subprocess

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        # Test basic imports
        from utils.constants import AppConfig, MarkConfig, DataConfig
        print("✅ Constants imported successfully")
        
        # Test app imports
        from app import compare_versions, load_json_files
        print("✅ App modules imported successfully")
        
        # Test visualization imports
        from sections.visualization import display_marks_pie_chart
        print("✅ Visualization modules imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_constants():
    """Test that constants have correct values"""
    print("🧪 Testing constants...")
    
    try:
        from utils.constants import AppConfig, MarkConfig, DataConfig
        
        # Test AppConfig
        assert AppConfig.APP_NAME == "Metrika"
        assert AppConfig.VERSION == "1.0.0"
        print("✅ AppConfig values correct")
        
        # Test MarkConfig
        assert MarkConfig.NA.value == "No assoliment"
        assert MarkConfig.AS.value == "Assoliment satisfactori"
        assert MarkConfig.AN.value == "Assoliment notable"
        assert MarkConfig.AE.value == "Assoliment excel·lent"
        print("✅ MarkConfig values correct")
        
        # Test DataConfig
        assert "CAT" in DataConfig.SUBJ_NAMES.value
        assert "MAT" in DataConfig.SUBJ_NAMES.value
        print("✅ DataConfig values correct")
        
        return True
    except AssertionError as e:
        print(f"❌ Constants test failed: {e}")
        return False

def test_version_comparison():
    """Test version comparison function"""
    print("🧪 Testing version comparison...")
    
    try:
        from app import compare_versions
        
        # Test equal versions
        assert compare_versions("1.0.0", "1.0.0") == 0
        
        # Test less than
        assert compare_versions("1.0.0", "1.0.1") == -1
        
        # Test greater than
        assert compare_versions("1.0.1", "1.0.0") == 1
        
        print("✅ Version comparison working correctly")
        return True
    except Exception as e:
        print(f"❌ Version comparison test failed: {e}")
        return False

def test_mark_config_methods():
    """Test MarkConfig methods"""
    print("🧪 Testing MarkConfig methods...")
    
    try:
        from utils.constants import MarkConfig
        
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
        
        print("✅ MarkConfig methods working correctly")
        return True
    except Exception as e:
        print(f"❌ MarkConfig methods test failed: {e}")
        return False

def test_file_structure():
    """Test that required files exist"""
    print("🧪 Testing file structure...")
    
    required_files = [
        'app.py',
        'utils/constants.py',
        'sections/visualization.py',
        'test/conftest.py',
        'test/test_data_loading.py',
        'test/test_csv_conversion.py',
        'test/test_visualization.py',
        'test/test_streamlit_integration.py',
        'test/test_utils.py',
        'test/test_basic_setup.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_pytest_installation():
    """Test that pytest is available"""
    print("🧪 Testing pytest installation...")
    
    try:
        import pytest
        print(f"✅ Pytest version: {pytest.__version__}")
        return True
    except ImportError:
        print("❌ Pytest not installed")
        return False

def run_basic_pytest():
    """Run a basic pytest to verify setup"""
    print("🧪 Running basic pytest...")
    
    try:
        # Run the basic setup test
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'test/test_basic_setup.py::TestBasicSetup::test_pytest_working',
            '-v'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Basic pytest test passed")
            return True
        else:
            print(f"❌ Basic pytest test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running pytest: {e}")
        return False

def main():
    """Main function to run all tests"""
    print("=" * 60)
    print("🧪 METRIKA HIGH-PRIORITY TESTS SETUP VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Pytest Installation", test_pytest_installation),
        ("Imports", test_imports),
        ("Constants", test_constants),
        ("Version Comparison", test_version_comparison),
        ("MarkConfig Methods", test_mark_config_methods),
        ("Basic Pytest", run_basic_pytest)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Setup is ready for high-priority testing.")
        print("\n🚀 Next steps:")
        print("1. Install test dependencies: pip install -r requirements-test.txt")
        print("2. Run high-priority tests: python test/run_tests.py")
        print("3. Run specific test: python test/run_tests.py --file test/test_data_loading.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the setup.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 