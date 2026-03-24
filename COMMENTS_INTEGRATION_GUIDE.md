# Comments System Integration Guide

## Overview
The comments system has been successfully integrated into all major views of the application:

### Features Added:

1. **Persistent Comments Storage**
   - Comments are stored in `comments_data.json` 
   - Automatically saved and loaded across sessions
   - Supports import/export functionality

2. **Comment Types Supported**:
   - **Student Comments**: General comments about specific students
   - **Subject Comments**: Comments about specific subjects/assignments
   - **Group Comments**: Comments about entire groups/classes
   - **Session Comments**: Comments about specific trimester/group combinations

3. **Integration Points**:

   #### Student View (`student_marks.py`)
   - General student comments after the marks tables
   - Available for CSV acta data
   
   #### Subject View (`visualization.py` - `display_subject_statistics`)
   - Subject-specific comments after the statistics charts
   - Allows teachers to add notes about particular subjects
   
   #### Group View (`visualization.py` - `display_group_statistics`) 
   - Group-level comments after the group statistics
   - Comments about the entire class performance
   
   #### Evolution View (`evolution.py` - `display_evolution_dashboard`)
   - Session-specific comments for trimester comparisons
   - Evolution notes and observations

4. **UI Components**:
   - **Comment Input**: Text area with save button
   - **Comment Display**: Shows existing comments with info styling
   - **Comments Management Sidebar**: Statistics, import/export, clear all

5. **Management Features**:
   - Export comments to timestamped JSON files
   - Import comments from JSON files (with merge option)
   - Clear all comments functionality
   - Comments statistics display

## Usage Examples:

### Adding Student Comments:
1. Navigate to "Alumne" tab
2. Select a student
3. Scroll down to "Comentaris Adicionals" section
4. Type comment and click "Desar"

### Adding Subject Comments:
1. Navigate to "Materia" tab
2. Select a subject from the dropdown
3. Scroll down to "Comentaris sobre l'assignatura" section
4. Add comment about the subject performance

### Adding Group Comments:
1. Navigate to "Grup" tab 
2. Scroll down to "Comentaris del grup" section
3. Add observations about the entire group

### Managing Comments:
1. Use the sidebar "Gestió de Comentaris" section
2. View statistics of stored comments
3. Export/Import comments for backup or sharing
4. Clear all comments if needed

## Technical Implementation:

The system uses:
- `CommentsManager` class for data management
- JSON file persistence 
- Streamlit session state for the manager instance
- Unique identifiers for different comment types
- UI helper functions for consistent interface

All comments are automatically saved when the "Desar" button is clicked and persist across browser sessions.