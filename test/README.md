# Metrika Application Testing

This directory contains comprehensive tests for the Metrika Streamlit application, focusing on high-priority functionality including data loading, CSV conversion, visualization, and Streamlit integration.

## 🧪 Test Structure

### High-Priority Test Files

1. **`test_data_loading.py`** - Tests for JSON file loading, version compatibility, and data validation
2. **`test_csv_conversion.py`** - Tests for CSV to JSON conversion functionality
3. **`test_visualization.py`** - Tests for Plotly chart generation and statistical calculations
4. **`test_streamlit_app_integration.py`** - Tests using official Streamlit testing framework
5. **`test_utils.py`** - Tests for utility functions and helper modules

### Configuration Files

- **`conftest.py`** - Pytest configuration with fixtures and test data
- **`pytest.ini`** - Pytest configuration settings
- **`run_tests.py`** - Test runner script with various options

### Existing Test Files

- **`test_conversion.py`** - Original CSV conversion test (legacy)
- **`test_json_viewer.py`** - Original JSON viewer test (legacy)
- **`test_data.csv`** - Sample CSV data for testing
- **`test_with_version.json`** - Sample JSON data with version information

## 🚀 Quick Start

### 1. Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### 2. Run High-Priority Tests

```bash
# Run all high-priority tests with coverage
python test/run_tests.py

# Run specific test file
python test/run_tests.py --file test/test_data_loading.py

# Run without coverage
python test/run_tests.py --no-coverage

# Run in quiet mode
python test/run_tests.py --quiet
```

### 3. Run with Pytest Directly

```bash
# Run all high-priority tests
pytest test/test_data_loading.py test/test_csv_conversion.py test/test_visualization.py test/test_streamlit_app_integration.py test/test_utils.py -v

# Run with coverage
pytest test/ --cov=. --cov-report=html:htmlcov --cov-report=term-missing -v

# Run specific test class
pytest test/test_data_loading.py::TestVersionComparison -v

# Run specific test method
pytest test/test_data_loading.py::TestVersionComparison::test_compare_versions_equal -v
```

## 📊 Test Coverage

The tests are designed to achieve high coverage of critical functionality:

- **Data Loading**: JSON parsing, version compatibility, error handling
- **CSV Conversion**: File processing, data transformation, validation
- **Visualization**: Chart generation, statistical calculations, Plotly integration
- **Streamlit App Testing**: Real app testing using official Streamlit testing framework
- **Utilities**: Helper functions, constants, data validation

## 🎯 Test Categories

### Unit Tests
- Individual function testing
- Data validation
- Utility functions
- Configuration testing

### Integration Tests
- File loading and processing
- CSV to JSON conversion pipeline
- Streamlit app initialization
- Data flow between components

### High-Priority Tests
- Core application functionality
- Critical data processing
- Essential UI components
- Error handling scenarios

### Streamlit App Tests
- Real app testing using `streamlit.testing.v1.AppTest`
- Widget interactions
- App state management
- User interface validation

## 🔧 Test Fixtures

The `conftest.py` file provides reusable test fixtures:

- **`sample_students_data`** - Sample student data for testing
- **`sample_json_structure`** - New format JSON structure
- **`sample_old_json_structure`** - Old format JSON structure
- **`sample_csv_data`** - Sample CSV data
- **`temp_test_dir`** - Temporary directory for test files
- **`mock_uploaded_file`** - Mock uploaded file
- **`sample_dataframe`** - Sample pandas DataFrame

## 🐛 Debugging Tests

### Common Issues

1. **Import Errors**: Ensure you're running from the project root directory
2. **Missing Dependencies**: Install all requirements from `requirements-test.txt`
3. **File Path Issues**: Tests use relative paths, run from project root
4. **Streamlit Testing**: Requires Streamlit >= 1.32.0 for official testing framework

### Debug Mode

```bash
# Run with detailed output
pytest test/ -v -s --tb=long

# Run single test with debugger
pytest test/test_data_loading.py::TestVersionComparison::test_compare_versions_equal -v -s --pdb
```

### Coverage Analysis

```bash
# Generate detailed coverage report
python test/run_tests.py --coverage-only

# View HTML coverage report
open htmlcov/index.html
```

## 📋 Test Commands Reference

### Basic Commands

```bash
# Run high-priority tests
python test/run_tests.py

# Run all tests
python test/run_tests.py --type all

# Run unit tests only
python test/run_tests.py --type unit

# Run integration tests only
python test/run_tests.py --type integration
```

### Advanced Commands

```bash
# Run specific test file
python test/run_tests.py --file test/test_visualization.py

# Run without coverage
python test/run_tests.py --no-coverage

# Run in quiet mode
python test/run_tests.py --quiet

# Generate coverage report only
python test/run_tests.py --coverage-only
```

### Pytest Commands

```bash
# Run with markers
pytest test/ -m "high_priority"

# Run with specific markers
pytest test/ -m "unit and not slow"

# Run with parallel execution
pytest test/ -n auto

# Run with HTML report
pytest test/ --html=report.html --self-contained-html
```

### Streamlit App Testing

```bash
# Run Streamlit app tests using official framework
pytest test/test_streamlit_app_integration.py -v

# Run with Streamlit testing specific options
pytest test/test_streamlit_app_integration.py --tb=short -v
```

## 🏗️ Adding New Tests

### Test File Structure

```python
"""
Test description for the module
"""
import pytest

class TestClassName:
    """Test class description"""
    
    def test_method_name(self, fixture_name):
        """Test method description"""
        # Arrange
        # Act
        # Assert
        pass
```

### Test Naming Conventions

- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<method_name>_<scenario>`

### Adding Fixtures

Add new fixtures to `conftest.py`:

```python
@pytest.fixture
def new_fixture():
    """Fixture description"""
    # Setup
    yield data
    # Cleanup (if needed)
```

### Streamlit App Testing

For Streamlit app tests using the official framework:

```python
from streamlit.testing.v1 import AppTest

def test_app_functionality():
    at = AppTest.from_file("app.py")
    at.run()
    # Test app behavior
    assert not at.exception
```

## 📈 Continuous Integration

The tests are designed to work with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    pip install -r requirements-test.txt
    python test/run_tests.py --type high_priority
```

## 🔍 Test Results

### Success Indicators

- All tests pass (exit code 0)
- Coverage above 80%
- No critical warnings
- All high-priority functionality tested
- Streamlit app tests pass

### Failure Investigation

1. Check test output for specific error messages
2. Verify test data and fixtures
3. Check for dependency issues
4. Review code changes that might affect tests
5. Ensure Streamlit version compatibility for app tests

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Streamlit Testing](https://docs.streamlit.io/develop/api-reference/app-testing)
- [Streamlit App Testing Framework](https://docs.streamlit.io/develop/api-reference/app-testing)
- [Plotly Testing](https://plotly.com/python/testing/)
- [Pandas Testing](https://pandas.pydata.org/docs/development/contributing_codebase.html#testing)

## 🤝 Contributing

When adding new functionality:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain coverage above 80%
4. Update this README if needed
5. Add appropriate test markers
6. Use official Streamlit testing framework for app tests

## 📞 Support

For test-related issues:

1. Check the test output for error messages
2. Verify your environment matches requirements
3. Run tests in debug mode for detailed output
4. Review the test fixtures and data
5. Check Streamlit version compatibility for app tests 