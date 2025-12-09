"""
Comments Manager - System to manage persistent comments across views and sessions
"""

import json
import os
import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

class CommentsManager:
    """Manages comments storage, retrieval and persistence"""
    
    def __init__(self, comments_file: str = "comments_data.json"):
        self.comments_file = Path(comments_file)
        self.comments_data = self._load_comments()
    
    def _load_comments(self) -> Dict[str, Any]:
        """Load comments from JSON file"""
        if self.comments_file.exists():
            try:
                with open(self.comments_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return self._get_empty_structure()
        return self._get_empty_structure()
    
    def _get_empty_structure(self) -> Dict[str, Any]:
        """Return empty comments structure"""
        return {
            "student_comments": {},    # {student_id: {subject: comment, "general": comment}}
            "subject_comments": {},    # {subject_name: comment}
            "group_comments": {},      # {group_code: comment}
            "session_comments": {},    # {session_id: comment}
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "version": "1.0.0"
            }
        }
    
    def _save_comments(self):
        """Save comments to JSON file"""
        self.comments_data["metadata"]["last_modified"] = datetime.now().isoformat()
        try:
            with open(self.comments_file, 'w', encoding='utf-8') as f:
                json.dump(self.comments_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"Error saving comments: {str(e)}")
    
    # Student-specific comments
    def add_student_comment(self, student_id: str, subject: str, comment: str):
        """Add comment for a specific student and subject"""
        if student_id not in self.comments_data["student_comments"]:
            self.comments_data["student_comments"][student_id] = {}
        self.comments_data["student_comments"][student_id][subject] = comment
        self._save_comments()
    
    def get_student_comment(self, student_id: str, subject: str) -> str:
        """Get comment for a specific student and subject"""
        return self.comments_data["student_comments"].get(student_id, {}).get(subject, "")
    
    def add_student_general_comment(self, student_id: str, comment: str):
        """Add general comment for a student"""
        self.add_student_comment(student_id, "general", comment)
    
    def get_student_general_comment(self, student_id: str) -> str:
        """Get general comment for a student"""
        return self.get_student_comment(student_id, "general")
    
    def get_all_student_comments(self, student_id: str) -> Dict[str, str]:
        """Get all comments for a student"""
        return self.comments_data["student_comments"].get(student_id, {})
    
    # Subject-specific comments
    def add_subject_comment(self, subject_name: str, comment: str):
        """Add comment for a specific subject"""
        self.comments_data["subject_comments"][subject_name] = comment
        self._save_comments()
    
    def get_subject_comment(self, subject_name: str) -> str:
        """Get comment for a specific subject"""
        return self.comments_data["subject_comments"].get(subject_name, "")
    
    # Group-specific comments
    def add_group_comment(self, group_code: str, comment: str):
        """Add comment for a specific group"""
        self.comments_data["group_comments"][group_code] = comment
        self._save_comments()
    
    def get_group_comment(self, group_code: str) -> str:
        """Get comment for a specific group"""
        return self.comments_data["group_comments"].get(group_code, "")
    
    # Session-specific comments
    def add_session_comment(self, session_id: str, comment: str):
        """Add comment for a specific session (trimester/group combination)"""
        self.comments_data["session_comments"][session_id] = comment
        self._save_comments()
    
    def get_session_comment(self, session_id: str) -> str:
        """Get comment for a specific session"""
        return self.comments_data["session_comments"].get(session_id, "")
    
    # Bulk operations
    def export_comments(self, export_path: str):
        """Export comments to a specific file"""
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(self.comments_data, f, ensure_ascii=False, indent=2)
    
    def import_comments(self, import_path: str, merge: bool = True):
        """Import comments from a file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            if merge:
                # Merge with existing data
                for key in ["student_comments", "subject_comments", "group_comments", "session_comments"]:
                    if key in imported_data:
                        self.comments_data[key].update(imported_data[key])
            else:
                # Replace existing data
                self.comments_data = imported_data
            
            self._save_comments()
            return True
        except Exception as e:
            st.error(f"Error importing comments: {str(e)}")
            return False
    
    def clear_all_comments(self):
        """Clear all comments"""
        self.comments_data = self._get_empty_structure()
        self._save_comments()
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about stored comments"""
        return {
            "student_comments": sum(len(comments) for comments in self.comments_data["student_comments"].values()),
            "subject_comments": len(self.comments_data["subject_comments"]),
            "group_comments": len(self.comments_data["group_comments"]),
            "session_comments": len(self.comments_data["session_comments"]),
        }


def get_session_id(students: List[Dict]) -> str:
    """Generate a unique session ID based on group and trimester"""
    if not students:
        return "unknown_session"
    
    first_student = students[0]
    group = first_student.get('grup_codi', first_student.get('grup', 'unknown_group'))
    trimester = first_student.get('trimestre', 'unknown_trimester')
    
    return f"{group}_{trimester}"


# UI Components for comments
def render_comment_input(
    comment_manager: CommentsManager,
    comment_type: str,
    identifier: str,
    label: str = "Comentari adicional",
    key_suffix: str = "",
    placeholder: str = "Escriu un comentari adicional..."
) -> str:
    """Render a comment input widget and handle saving"""
    
    # Create unique key for the text area
    text_area_key = f"comment_{comment_type}_{identifier}_{key_suffix}"
    form_key = f"comment_form_{comment_type}_{identifier}_{key_suffix}"
    
    # Get existing comment
    if comment_type == "student":
        parts = identifier.split("_", 1)
        if len(parts) == 2:
            student_id, subject = parts
            existing_comment = comment_manager.get_student_comment(student_id, subject)
        else:
            existing_comment = comment_manager.get_student_general_comment(identifier)
    elif comment_type == "subject":
        existing_comment = comment_manager.get_subject_comment(identifier)
    elif comment_type == "group":
        existing_comment = comment_manager.get_group_comment(identifier)
    elif comment_type == "session":
        existing_comment = comment_manager.get_session_comment(identifier)
    else:
        existing_comment = ""

    # Use a form to avoid re-running the whole app on every keystroke
    with st.form(form_key):
        col1, col2 = st.columns([4, 1])
        with col1:
            comment = st.text_area(
                label,
                value=existing_comment,
                key=text_area_key,
                placeholder=placeholder,
                height=80
            )

        with col2:
            st.write("")  # Add spacing
            st.write("")
            submitted = st.form_submit_button("💾 Desar", help="Desar comentari")

        if submitted:
            # Save comment based on type
            if comment_type == "student":
                parts = identifier.split("_", 1)
                if len(parts) == 2:
                    student_id, subject = parts
                    comment_manager.add_student_comment(student_id, subject, comment)
                else:
                    comment_manager.add_student_general_comment(identifier, comment)
            elif comment_type == "subject":
                comment_manager.add_subject_comment(identifier, comment)
            elif comment_type == "group":
                comment_manager.add_group_comment(identifier, comment)
            elif comment_type == "session":
                comment_manager.add_session_comment(identifier, comment)

            st.success("Comentari desat!")
            # st.info(f"💬 **Comentari:** {comment}")

    return comment


def render_comment_display(
    comment_manager: CommentsManager,
    comment_type: str,
    identifier: str,
    show_empty: bool = False
) -> Optional[str]:
    """Display a saved comment if it exists"""
    
    if comment_type == "student":
        parts = identifier.split("_", 1)
        if len(parts) == 2:
            student_id, subject = parts
            comment = comment_manager.get_student_comment(student_id, subject)
        else:
            comment = comment_manager.get_student_general_comment(identifier)
    elif comment_type == "subject":
        comment = comment_manager.get_subject_comment(identifier)
    elif comment_type == "group":
        comment = comment_manager.get_group_comment(identifier)
    elif comment_type == "session":
        comment = comment_manager.get_session_comment(identifier)
    else:
        comment = ""
    
    # if comment or show_empty:
    #     if comment:
    #         # st.info(f"💬 **Comentari:** {comment}")
    #         pass
    #     elif show_empty:
    #         # st.info("💬 Sense comentaris adicionals")
    #         pass
    #     return comment
    
    return None


def render_comments_management_sidebar(comment_manager: CommentsManager):
    """Render comments management options in sidebar"""
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 💬 Gestió de Comentaris")
        
        # Statistics
        stats = comment_manager.get_stats()
        total_comments = sum(stats.values())
        st.metric("Total comentaris", total_comments)
        
        # Show breakdown if there are comments
        if total_comments > 0:
            for key, count in stats.items():
                if count > 0:
                    label = {
                        "student_comments": "Alumnes",
                        "subject_comments": "Matèries", 
                        "group_comments": "Grups",
                        "session_comments": "Sessions"
                    }.get(key, key)
                    st.caption(f"• {label}: {count}")
        
        # Export/Import section
        with st.expander("📂 Importar/Exportar"):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📥 Exportar", help="Exportar comentaris a JSON"):
                    export_path = f"comments_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    comment_manager.export_comments(export_path)
                    st.success(f"Exportat a {export_path}")
            
            with col2:
                uploaded_file = st.file_uploader("📤 Importar", type=['json'], help="Importar comentaris des d'un JSON")
                if uploaded_file:
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w+b', suffix='.json', delete=False) as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp.flush()
                        if comment_manager.import_comments(tmp.name, merge=True):
                            st.success("Comentaris importats!")
                            st.rerun()
        
        # Clear all comments
        if st.button("🗑️ Esborrar tots", help="Esborrar tots els comentaris", type="secondary"):
            comment_manager.clear_all_comments()
            st.success("Comentaris esborrats!")
            st.rerun()