"""
High-priority tests for visualization functionality
"""
import pytest
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from unittest.mock import Mock, patch

from sections.visualization import (
    display_marks_pie_chart,
    display_group_statistics,
    group_failure_table,
    display_subjects_bar_chart,
    display_student_ranking,
    display_student_subject_heatmap,
    display_subject_statistics
)
from utils.constants import MarkConfig, DataConfig


class TestMarkConfiguration:
    """Test mark configuration and mapping functionality"""
    
    def test_mark_config_values(self):
        """Test MarkConfig enum values"""
        assert MarkConfig.NA.value == "No assoliment"
        assert MarkConfig.AS.value == "Assoliment satisfactori"
        assert MarkConfig.AN.value == "Assoliment notable"
        assert MarkConfig.AE.value == "Assoliment excel·lent"
    
    def test_height_mapping(self):
        """Test mark to height mapping"""
        assert MarkConfig.get_height_from_key('NA') == 1
        assert MarkConfig.get_height_from_key('AS') == 2
        assert MarkConfig.get_height_from_key('AN') == 3
        assert MarkConfig.get_height_from_key('AE') == 4
        assert MarkConfig.get_height_from_key('invalid') == 0
    
    def test_mark_from_height(self):
        """Test height to mark mapping"""
        assert MarkConfig.get_mark_from_height(1) == 'NA'
        assert MarkConfig.get_mark_from_height(2) == 'AS'
        assert MarkConfig.get_mark_from_height(3) == 'AN'
        assert MarkConfig.get_mark_from_height(4) == 'AE'
        assert MarkConfig.get_mark_from_height(0) == ""
        assert MarkConfig.get_mark_from_height(999) == ""
    
    def test_color_mapping(self):
        """Test mark to color mapping"""
        color_map = MarkConfig.COLOR_MAP.value
        assert color_map["No assoliment"] == "#d62728"
        assert color_map["Assoliment satisfactori"] == "#ff7f0e"
        assert color_map["Assoliment notable"] == "#1f77b4"
        assert color_map["Assoliment excel·lent"] == "#2ca02c"


class TestPieChartVisualization:
    """Test pie chart visualization functionality"""
    
    def test_display_marks_pie_chart(self, sample_students_data):
        """Test pie chart generation for student marks"""
        # Mock Streamlit
        with patch('sections.visualization.st') as mock_st:
            display_marks_pie_chart(sample_students_data)
            
            # Verify plotly_chart was called
            mock_st.plotly_chart.assert_called_once()
            
            # Get the figure that was passed to plotly_chart
            call_args = mock_st.plotly_chart.call_args
            fig = call_args[0][0]  # First argument of the call
            
            # Verify it's a Plotly figure
            assert isinstance(fig, go.Figure)
            
            # Verify it's a pie chart
            assert fig.data[0].type == 'pie'
    
    def test_pie_chart_with_empty_data(self):
        """Test pie chart with empty student data"""
        empty_data = []
        
        with patch('sections.visualization.st') as mock_st:
            display_marks_pie_chart(empty_data)
            
            # Should still call plotly_chart (with empty chart)
            mock_st.plotly_chart.assert_called_once()
    
    def test_pie_chart_with_missing_qualifications(self, sample_students_data):
        """Test pie chart with students missing qualifications"""
        # Remove qualifications from some subjects
        modified_data = sample_students_data.copy()
        modified_data[0]['materies'][0]['qualificacio'] = ""
        
        with patch('sections.visualization.st') as mock_st:
            display_marks_pie_chart(modified_data)
            
            # Should still generate chart
            mock_st.plotly_chart.assert_called_once()


class TestGroupStatistics:
    """Test group statistics functionality"""
    
    def test_display_group_statistics(self, sample_students_data):
        """Test group statistics display"""
        with patch('sections.visualization.st') as mock_st:
            display_group_statistics(sample_students_data)
            
            # Should call various Streamlit functions
            assert mock_st.subheader.called
            assert mock_st.metric.called
    
    def test_group_statistics_calculations(self, sample_students_data):
        """Test statistical calculations"""
        # Create a more diverse dataset for testing
        diverse_data = [
            {
                "id": "1",
                "nom_cognoms": "Student 1",
                "materies": [
                    {"materia": "MAT", "qualificacio": "Assoliment excel·lent", "comentari": ""},
                    {"materia": "CAT", "qualificacio": "Assoliment notable", "comentari": ""}
                ]
            },
            {
                "id": "2",
                "nom_cognoms": "Student 2",
                "materies": [
                    {"materia": "MAT", "qualificacio": "No assoliment", "comentari": ""},
                    {"materia": "CAT", "qualificacio": "Assoliment satisfactori", "comentari": ""}
                ]
            },
            {
                "id": "3",
                "nom_cognoms": "Student 3",
                "materies": [
                    {"materia": "MAT", "qualificacio": "Assoliment notable", "comentari": ""},
                    {"materia": "CAT", "qualificacio": "Assoliment excel·lent", "comentari": ""}
                ]
            }
        ]
        
        with patch('sections.visualization.st') as mock_st:
            display_group_statistics(diverse_data)
            
            # Should call metric multiple times for different statistics
            assert mock_st.metric.call_count >= 3  # At least 3 metrics (total, average, etc.)


class TestFailureTable:
    """Test failure table functionality"""
    
    def test_group_failure_table(self, sample_students_data):
        """Test failure table generation"""
        with patch('sections.visualization.st') as mock_st:
            group_failure_table(sample_students_data)
            
            # Should call dataframe to display table
            mock_st.dataframe.assert_called()
    
    def test_failure_table_with_no_failures(self):
        """Test failure table with no failing students"""
        no_failures_data = [
            {
                "id": "1",
                "nom_cognoms": "Student 1",
                "materies": [
                    {"materia": "MAT", "qualificacio": "Assoliment excel·lent", "comentari": ""},
                    {"materia": "CAT", "qualificacio": "Assoliment notable", "comentari": ""}
                ]
            }
        ]
        
        with patch('sections.visualization.st') as mock_st:
            group_failure_table(no_failures_data)
            
            # Should still display table (even if empty)
            mock_st.dataframe.assert_called()


class TestBarChartVisualization:
    """Test bar chart visualization functionality"""
    
    def test_display_subjects_bar_chart(self, sample_students_data):
        """Test subjects bar chart generation"""
        with patch('sections.visualization.st') as mock_st:
            display_subjects_bar_chart(sample_students_data)
            
            # Should call plotly_chart
            mock_st.plotly_chart.assert_called_once()
            
            # Get the figure
            call_args = mock_st.plotly_chart.call_args
            fig = call_args[0][0]
            
            # Verify it's a bar chart
            assert isinstance(fig, go.Figure)
            assert fig.data[0].type == 'bar'
    
    def test_bar_chart_with_single_subject(self):
        """Test bar chart with only one subject"""
        single_subject_data = [
            {
                "id": "1",
                "nom_cognoms": "Student 1",
                "materies": [
                    {"materia": "MAT", "qualificacio": "Assoliment excel·lent", "comentari": ""}
                ]
            }
        ]
        
        with patch('sections.visualization.st') as mock_st:
            display_subjects_bar_chart(single_subject_data)
            
            # Should still generate chart
            mock_st.plotly_chart.assert_called_once()


class TestStudentRanking:
    """Test student ranking functionality"""
    
    def test_display_student_ranking(self, sample_students_data):
        """Test student ranking display"""
        with patch('sections.visualization.st') as mock_st:
            display_student_ranking(sample_students_data)
            
            # Should call dataframe to display ranking
            mock_st.dataframe.assert_called()
    
    def test_ranking_with_equal_scores(self):
        """Test ranking with students having equal scores"""
        equal_scores_data = [
            {
                "id": "1",
                "nom_cognoms": "Student 1",
                "materies": [
                    {"materia": "MAT", "qualificacio": "Assoliment notable", "comentari": ""},
                    {"materia": "CAT", "qualificacio": "Assoliment notable", "comentari": ""}
                ]
            },
            {
                "id": "2",
                "nom_cognoms": "Student 2",
                "materies": [
                    {"materia": "MAT", "qualificacio": "Assoliment notable", "comentari": ""},
                    {"materia": "CAT", "qualificacio": "Assoliment notable", "comentari": ""}
                ]
            }
        ]
        
        with patch('sections.visualization.st') as mock_st:
            display_student_ranking(equal_scores_data)
            
            # Should still display ranking
            mock_st.dataframe.assert_called()


class TestHeatmapVisualization:
    """Test heatmap visualization functionality"""
    
    def test_display_student_subject_heatmap(self, sample_students_data):
        """Test student-subject heatmap generation"""
        with patch('sections.visualization.st') as mock_st:
            display_student_subject_heatmap(sample_students_data)
            
            # Should call plotly_chart
            mock_st.plotly_chart.assert_called_once()
            
            # Get the figure
            call_args = mock_st.plotly_chart.call_args
            fig = call_args[0][0]
            
            # Verify it's a heatmap
            assert isinstance(fig, go.Figure)
            assert fig.data[0].type == 'heatmap'
    
    def test_heatmap_with_missing_data(self, sample_students_data):
        """Test heatmap with missing subject data"""
        # Remove some subjects from students
        modified_data = sample_students_data.copy()
        modified_data[0]['materies'] = modified_data[0]['materies'][:1]  # Only one subject
        
        with patch('sections.visualization.st') as mock_st:
            display_student_subject_heatmap(modified_data)
            
            # Should still generate heatmap
            mock_st.plotly_chart.assert_called_once()


class TestSubjectStatistics:
    """Test subject statistics functionality"""
    
    def test_display_subject_statistics(self, sample_students_data):
        """Test subject statistics display"""
        with patch('sections.visualization.st') as mock_st:
            display_subject_statistics(sample_students_data)
            
            # Should call various Streamlit functions
            assert mock_st.subheader.called
            assert mock_st.plotly_chart.called
    
    def test_subject_statistics_with_multiple_subjects(self):
        """Test subject statistics with multiple subjects"""
        multi_subject_data = [
            {
                "id": "1",
                "nom_cognoms": "Student 1",
                "materies": [
                    {"materia": "MAT", "qualificacio": "Assoliment excel·lent", "comentari": ""},
                    {"materia": "CAT", "qualificacio": "Assoliment notable", "comentari": ""},
                    {"materia": "ANG", "qualificacio": "Assoliment satisfactori", "comentari": ""}
                ]
            },
            {
                "id": "2",
                "nom_cognoms": "Student 2",
                "materies": [
                    {"materia": "MAT", "qualificacio": "Assoliment notable", "comentari": ""},
                    {"materia": "CAT", "qualificacio": "Assoliment excel·lent", "comentari": ""},
                    {"materia": "ANG", "qualificacio": "No assoliment", "comentari": ""}
                ]
            }
        ]
        
        with patch('sections.visualization.st') as mock_st:
            display_subject_statistics(multi_subject_data)
            
            # Should generate multiple charts (one per subject)
            assert mock_st.plotly_chart.call_count >= 3


class TestDataFrameOperations:
    """Test DataFrame operations used in visualizations"""
    
    def test_dataframe_creation_from_students(self, sample_students_data):
        """Test creating DataFrame from student data"""
        # This would be the logic used in visualization functions
        df_data = []
        for student in sample_students_data:
            row = {'id': student['id'], 'nom_cognoms': student['nom_cognoms']}
            for materia in student['materies']:
                row[materia['materia']] = materia['qualificacio']
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        
        # Verify DataFrame structure
        assert len(df) == 2
        assert 'id' in df.columns
        assert 'nom_cognoms' in df.columns
        assert 'Matemàtiques' in df.columns
        assert 'Català' in df.columns
    
    def test_qualification_counting(self, sample_students_data):
        """Test counting qualifications by type"""
        # Count qualifications
        qualification_counts = {
            "No assoliment": 0,
            "Assoliment satisfactori": 0,
            "Assoliment notable": 0,
            "Assoliment excel·lent": 0
        }
        
        for student in sample_students_data:
            for materia in student['materies']:
                qual = materia['qualificacio']
                if qual in qualification_counts:
                    qualification_counts[qual] += 1
        
        # Verify counts
        assert qualification_counts["Assoliment notable"] >= 1
        assert qualification_counts["Assoliment satisfactori"] >= 1
        assert qualification_counts["No assoliment"] >= 1


class TestPlotlyFigureValidation:
    """Test Plotly figure validation"""
    
    def test_figure_has_required_attributes(self):
        """Test that generated figures have required attributes"""
        # Create a sample figure (similar to what visualization functions would create)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=['A', 'B'], y=[1, 2]))
        fig.update_layout(title="Test Chart")
        
        # Verify figure structure
        assert hasattr(fig, 'data')
        assert hasattr(fig, 'layout')
        assert len(fig.data) > 0
        assert fig.layout.title.text == "Test Chart"
    
    def test_figure_data_types(self):
        """Test that figure data has correct types"""
        fig = go.Figure()
        fig.add_trace(go.Pie(labels=['A', 'B'], values=[1, 2]))
        
        # Verify data types
        assert fig.data[0].type == 'pie'
        assert isinstance(fig.data[0].labels, list)
        assert isinstance(fig.data[0].values, list) 