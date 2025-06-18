"""
Pytest configuration and fixtures for Metrika application tests
"""
import pytest
import sys
import os
import json
import pandas as pd
from unittest.mock import Mock, MagicMock
import tempfile
import shutil

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import load_json_files, load_uploaded_json_files, compare_versions
from utils.constants import MarkConfig, DataConfig, AppConfig
from utils.csv_to_json import process_csv_to_json


@pytest.fixture
def sample_students_data():
    """Sample student data for testing"""
    return [
        {
            "id": "12345",
            "nom_cognoms": "Joan Pérez García",
            "materies": [
                {
                    "materia": "Matemàtiques",
                    "qualificacio": "Assoliment notable",
                    "comentari": "Bon treball en general"
                },
                {
                    "materia": "Català",
                    "qualificacio": "Assoliment satisfactori",
                    "comentari": "Ha de millorar l'expressió escrita"
                },
                {
                    "materia": "Anglès",
                    "qualificacio": "No assoliment",
                    "comentari": "Necessita més esforç"
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
                    "comentari": "Excel·lent domini de la matèria"
                },
                {
                    "materia": "Català",
                    "qualificacio": "Assoliment notable",
                    "comentari": "Bona expressió escrita"
                },
                {
                    "materia": "Anglès",
                    "qualificacio": "Assoliment satisfactori",
                    "comentari": "Progrés adequat"
                }
            ]
        }
    ]


@pytest.fixture
def sample_json_structure():
    """Sample JSON structure with new format"""
    return {
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
                        "comentari": "Bon treball en general"
                    }
                ]
            }
        ],
        "metrika_version": "1.0.0"
    }


@pytest.fixture
def sample_old_json_structure():
    """Sample JSON structure with old format (direct array)"""
    return [
        {
            "id": "12345",
            "nom_cognoms": "Joan Pérez García",
            "materies": [
                {
                    "materia": "Matemàtiques",
                    "qualificacio": "Assoliment notable",
                    "comentari": "Bon treball en general"
                }
            ]
        }
    ]


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing"""
    return """id|nom_cognoms|numero_avaluacio|m1|q1|c1|m2|q2|c2|m3|q3|c3|m4|q4|c4|m5|q5|c5|comentari general
12345|Joan Pérez García|1|Matemàtiques|Assoliment notable|Bon treball en general|Català|Assoliment satisfactori|Ha de millorar l'expressió escrita|Història|Assoliment excel·lent|Excel·lent comprensió dels conceptes|Física|Assoliment satisfactori|Treballa bé però ha de practicar més|Anglès|No assoliment|Necessita més esforç|Bon treball en general
67890|Maria López Sánchez|1|Matemàtiques|Assoliment excel·lent|Excel·lent domini de la matèria|Català|Assoliment notable|Bona expressió escrita|Biologia|Assoliment satisfactori|Comprensió adequada|Química|Assoliment notable|Bon treball de laboratori|Anglès|No assoliment|Necessita més esforç|Bon treball en general"""


@pytest.fixture
def temp_test_dir():
    """Create a temporary directory for test files"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components for testing"""
    mock_st = Mock()
    
    # Mock common Streamlit functions
    mock_st.set_page_config = Mock()
    mock_st.title = Mock()
    mock_st.subheader = Mock()
    mock_st.write = Mock()
    mock_st.error = Mock()
    mock_st.warning = Mock()
    mock_st.success = Mock()
    mock_st.info = Mock()
    mock_st.file_uploader = Mock()
    mock_st.selectbox = Mock()
    mock_st.button = Mock()
    mock_st.tabs = Mock(return_value=[Mock(), Mock(), Mock(), Mock()])
    mock_st.columns = Mock(return_value=[Mock(), Mock()])
    mock_st.expander = Mock()
    mock_st.dataframe = Mock()
    mock_st.plotly_chart = Mock()
    mock_st.metric = Mock()
    mock_st.markdown = Mock()
    mock_st.sidebar = Mock()
    mock_st.session_state = {}
    
    return mock_st


@pytest.fixture
def mock_uploaded_file():
    """Mock uploaded file for testing"""
    mock_file = Mock()
    mock_file.name = "test_file.json"
    mock_file.read.return_value = json.dumps({
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
                        "comentari": "Bon treball en general"
                    }
                ]
            }
        ],
        "metrika_version": "1.0.0"
    }).encode('utf-8')
    mock_file.seek = Mock()
    return mock_file


@pytest.fixture
def sample_dataframe():
    """Sample pandas DataFrame for testing visualizations"""
    data = {
        'id': ['12345', '67890'],
        'nom_cognoms': ['Joan Pérez García', 'Maria López Sánchez'],
        'MAT': ['Assoliment notable', 'Assoliment excel·lent'],
        'CAT': ['Assoliment satisfactori', 'Assoliment notable'],
        'ANG': ['No assoliment', 'Assoliment satisfactori']
    }
    return pd.DataFrame(data)


@pytest.fixture
def corrupted_json_data():
    """Corrupted JSON data for error testing"""
    return "{ invalid json data }"


@pytest.fixture
def empty_json_data():
    """Empty JSON data for testing"""
    return "{}" 