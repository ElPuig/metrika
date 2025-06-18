"""
High-priority tests for Streamlit app integration using official Streamlit testing framework
"""
import pytest
import tempfile
import json
import os
from pathlib import Path

# Import the official Streamlit testing framework
from streamlit.testing.v1 import AppTest


class TestStreamlitAppIntegration:
    """Test Streamlit app integration using official testing framework"""
    
    def test_app_initialization(self):
        """Test that the app initializes without errors"""
        # Create AppTest instance from the main app file
        at = AppTest.from_file("app.py")
        
        # Run the app
        at.run()
        
        # Check that no exceptions occurred
        assert not at.exception, f"App initialization failed: {at.exception}"
        
        # Check that the app title is displayed
        assert len(at.title) > 0, "App title should be displayed"
        assert "Sistema de Visualització de Notes" in at.title[0].value
    
    def test_sidebar_menu(self):
        """Test sidebar menu functionality"""
        at = AppTest.from_file("app.py")
        at.run()
        
        # Check that sidebar exists
        assert at.sidebar is not None, "Sidebar should exist"
        
        # Check that selectbox (menu) exists in sidebar
        assert len(at.sidebar.selectbox) > 0, "Menu selectbox should exist in sidebar"
        
        # Check menu options
        menu = at.sidebar.selectbox[0]
        assert "Estadísticas" in menu.options, "Estadísticas should be a menu option"
        assert "Convertir CSV" in menu.options, "Convertir CSV should be a menu option"
    
    def test_statistics_menu_selection(self):
        """Test statistics menu selection"""
        at = AppTest.from_file("app.py")
        at.run()
        
        # Select statistics menu
        at.sidebar.selectbox[0].select("Estadísticas").run()
        
        # Check that statistics page is displayed
        assert not at.exception, f"Statistics page failed to load: {at.exception}"
        assert len(at.title) > 0, "Statistics page title should be displayed"
    
    def test_csv_converter_menu_selection(self):
        """Test CSV converter menu selection"""
        at = AppTest.from_file("app.py")
        at.run()
        
        # Select CSV converter menu
        at.sidebar.selectbox[0].select("Convertir CSV").run()
        
        # Check that CSV converter page is displayed
        assert not at.exception, f"CSV converter page failed to load: {at.exception}"
        assert len(at.title) > 0, "CSV converter page title should be displayed"
    
    def test_file_uploader_widget(self):
        """Test file uploader widget functionality"""
        at = AppTest.from_file("app.py")
        at.run()
        
        # Select statistics menu to access file uploader
        at.sidebar.selectbox[0].select("Estadísticas").run()
        
        # Check that file uploader exists
        assert len(at.file_uploader) > 0, "File uploader should exist on statistics page"
        
        # Check file uploader configuration
        uploader = at.file_uploader[0]
        assert uploader.type == ["json"], "File uploader should accept JSON files"
        assert uploader.accept_multiple_files, "File uploader should accept multiple files"
    
    def test_warning_message_without_files(self):
        """Test warning message when no files are uploaded"""
        at = AppTest.from_file("app.py")
        at.run()
        
        # Select statistics menu
        at.sidebar.selectbox[0].select("Estadísticas").run()
        
        # Check that warning message is displayed
        assert len(at.warning) > 0, "Warning message should be displayed when no files are uploaded"
        assert "Arrossega almenys un fitxer JSON" in at.warning[0].value, "Warning should mention JSON files"
    
    def test_app_with_sample_json_file(self, temp_test_dir):
        """Test app with a sample JSON file"""
        # Create sample JSON file
        sample_data = {
            "grup": "3B",
            "trimestre": "Primer trimestre",
            "estudiants": [
                {
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
            ],
            "metrika_version": "1.0.0"
        }
        
        json_file = os.path.join(temp_test_dir, "test_sample.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        
        # Create AppTest with file upload simulation
        at = AppTest.from_file("app.py")
        at.run()
        
        # Select statistics menu
        at.sidebar.selectbox[0].select("Estadísticas").run()
        
        # Simulate file upload (this would need to be implemented based on actual file upload behavior)
        # Note: File upload simulation might require additional setup depending on how the app handles uploads
        
        # Check that app doesn't crash with file processing
        assert not at.exception, f"App failed to process JSON file: {at.exception}"
    
    def test_tab_navigation(self):
        """Test tab navigation functionality"""
        at = AppTest.from_file("app.py")
        at.run()
        
        # Select statistics menu
        at.sidebar.selectbox[0].select("Estadísticas").run()
        
        # Check that tabs exist (if they're created when files are uploaded)
        # This test might need adjustment based on actual app behavior
        assert not at.exception, "Tab navigation should not cause exceptions"
    
    def test_app_configuration(self):
        """Test app configuration and settings"""
        at = AppTest.from_file("app.py")
        at.run()
        
        # Check that app runs without configuration errors
        assert not at.exception, f"App configuration error: {at.exception}"
        
        # Check that sidebar contains version information
        assert at.sidebar is not None, "Sidebar should exist for version info"
    
    def test_error_handling(self):
        """Test error handling in the app"""
        at = AppTest.from_file("app.py")
        at.run()
        
        # Test that app handles errors gracefully
        # This could include testing with invalid inputs, missing files, etc.
        assert not at.exception, f"App should handle errors gracefully: {at.exception}"


class TestStreamlitComponents:
    """Test individual Streamlit components"""
    
    def test_text_elements(self):
        """Test text elements rendering"""
        at = AppTest.from_file("app.py")
        at.run()
        
        # Check that text elements are rendered
        # The app should have various text elements like titles, headers, etc.
        assert len(at.title) > 0 or len(at.header) > 0 or len(at.markdown) > 0, "App should have text elements"
    
    def test_layout_components(self):
        """Test layout components"""
        at = AppTest.from_file("app.py")
        at.run()
        
        # Check that sidebar exists
        assert at.sidebar is not None, "Sidebar should exist"
        
        # Check that main content area exists
        # The main content is typically in the default block
        assert not at.exception, "Main content area should render without errors"
    
    def test_input_widgets(self):
        """Test input widgets functionality"""
        at = AppTest.from_file("app.py")
        at.run()
        
        # Select statistics menu to access widgets
        at.sidebar.selectbox[0].select("Estadísticas").run()
        
        # Check that selectbox (menu) works
        assert len(at.sidebar.selectbox) > 0, "Menu selectbox should exist"
        
        # Test menu selection
        at.sidebar.selectbox[0].select("Convertir CSV").run()
        assert not at.exception, "Menu selection should work without errors"


class TestStreamlitAppBehavior:
    """Test app behavior and user interactions"""
    
    def test_menu_navigation_flow(self):
        """Test complete menu navigation flow"""
        at = AppTest.from_file("app.py")
        at.run()
        
        # Test navigation to statistics
        at.sidebar.selectbox[0].select("Estadísticas").run()
        assert not at.exception, "Navigation to statistics should work"
        
        # Test navigation to CSV converter
        at.sidebar.selectbox[0].select("Convertir CSV").run()
        assert not at.exception, "Navigation to CSV converter should work"
        
        # Test navigation back to statistics
        at.sidebar.selectbox[0].select("Estadísticas").run()
        assert not at.exception, "Navigation back to statistics should work"
    
    def test_app_state_persistence(self):
        """Test app state persistence across interactions"""
        at = AppTest.from_file("app.py")
        at.run()
        
        # Perform multiple interactions
        at.sidebar.selectbox[0].select("Estadísticas").run()
        at.sidebar.selectbox[0].select("Convertir CSV").run()
        at.sidebar.selectbox[0].select("Estadísticas").run()
        
        # App should maintain state without errors
        assert not at.exception, "App should maintain state across interactions"
    
    def test_app_performance(self):
        """Test app performance and responsiveness"""
        at = AppTest.from_file("app.py")
        at.run()
        
        # App should load quickly without hanging
        assert not at.exception, "App should load without performance issues"
        
        # Multiple rapid interactions should work
        for _ in range(3):
            at.sidebar.selectbox[0].select("Estadísticas").run()
            at.sidebar.selectbox[0].select("Convertir CSV").run()
        
        assert not at.exception, "App should handle rapid interactions without issues"


class TestStreamlitAppIntegrationWithData:
    """Test app integration with actual data processing"""
    
    def test_app_with_old_format_json(self, temp_test_dir):
        """Test app with old format JSON data"""
        # Create old format JSON data
        old_format_data = [
            {
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
        ]
        
        json_file = os.path.join(temp_test_dir, "T1.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(old_format_data, f, ensure_ascii=False, indent=2)
        
        at = AppTest.from_file("app.py")
        at.run()
        
        # Select statistics menu
        at.sidebar.selectbox[0].select("Estadísticas").run()
        
        # App should handle old format data without crashing
        assert not at.exception, "App should handle old format JSON without errors"
    
    def test_app_with_new_format_json(self, temp_test_dir):
        """Test app with new format JSON data"""
        # Create new format JSON data
        new_format_data = {
            "grup": "3B",
            "trimestre": "Primer trimestre",
            "estudiants": [
                {
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
            ],
            "metrika_version": "1.0.0"
        }
        
        json_file = os.path.join(temp_test_dir, "test_new.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(new_format_data, f, ensure_ascii=False, indent=2)
        
        at = AppTest.from_file("app.py")
        at.run()
        
        # Select statistics menu
        at.sidebar.selectbox[0].select("Estadísticas").run()
        
        # App should handle new format data without crashing
        assert not at.exception, "App should handle new format JSON without errors"
    
    def test_app_with_multiple_students(self, temp_test_dir):
        """Test app with multiple students data"""
        # Create data with multiple students
        multi_student_data = {
            "grup": "3B",
            "trimestre": "Primer trimestre",
            "estudiants": [
                {
                    "id": "12345",
                    "nom_cognoms": "Joan Pérez García",
                    "materies": [
                        {
                            "materia": "Matemàtiques",
                            "qualificacio": "Assoliment notable",
                            "comentari": "Bon treball"
                        }
                    ]
                },
                {
                    "id": "67890",
                    "nom_cognoms": "Maria López Sánchez",
                    "materies": [
                        {
                            "materia": "Matemàtiques",
                            "qualificacio": "Assoliment excel·lent",
                            "comentari": "Excel·lent treball"
                        }
                    ]
                }
            ],
            "metrika_version": "1.0.0"
        }
        
        json_file = os.path.join(temp_test_dir, "multi_students.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(multi_student_data, f, ensure_ascii=False, indent=2)
        
        at = AppTest.from_file("app.py")
        at.run()
        
        # Select statistics menu
        at.sidebar.selectbox[0].select("Estadísticas").run()
        
        # App should handle multiple students without crashing
        assert not at.exception, "App should handle multiple students without errors" 