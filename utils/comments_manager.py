"""
Comments Manager - System to manage persistent comments across views and sessions
"""

import json
import os
import tempfile
import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

class CommentsManager:
    """Manages comments storage, retrieval and persistence"""
    
    def __init__(self, comments_file: str = "comments_data.json"):
        self.comments_file = Path(comments_file)
        self.auto_export_path = None  # Path to auto-export/sync to (from last import)
        self.comments_data = self._load_comments()
    
    def _load_comments(self) -> Dict[str, Any]:
        """Load comments from JSON file - preferring auto-export path if available"""
        # Try to load from auto-export path first (if it exists and file is present)
        if self.auto_export_path and Path(self.auto_export_path).exists():
            try:
                with open(self.auto_export_path, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    return self._ensure_structure(loaded_data)
            except (json.JSONDecodeError, FileNotFoundError):
                pass  # Fall through to load from main file
        
        # Load from main comments file
        if self.comments_file.exists():
            try:
                with open(self.comments_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    # Ensure all required keys exist (migration support)
                    return self._ensure_structure(loaded_data)
            except (json.JSONDecodeError, FileNotFoundError):
                return self._get_empty_structure()
        return self._get_empty_structure()
    
    def _ensure_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure loaded data has all required keys"""
        required_keys = {
            "student_comments": {},
            "subject_comments": {},
            "group_comments": {},
            "session_comments": {},
            "student_adaptations": {},
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "version": "1.0.1"
            }
        }
        
        # Merge with existing data, preserving what's there
        for key, default_value in required_keys.items():
            if key not in data:
                data[key] = default_value
            elif key == "metadata" and isinstance(data[key], dict):
                # Preserve existing metadata but ensure version is updated
                if "version" not in data[key]:
                    data[key]["version"] = "1.0.1"
        
        return data
    
    def _get_empty_structure(self) -> Dict[str, Any]:
        """Return empty comments structure"""
        return {
            "student_comments": {},    # {student_id: {subject: comment, "general": comment}}
            "subject_comments": {},    # {subject_name: comment}
            "group_comments": {},      # {group_code: comment}
            "session_comments": {},    # {session_id: comment}
            "student_adaptations": {}, # {student_id: True/False}
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "version": "1.0.1"
            }
        }
    
    def _save_comments(self):
        """Save comments to JSON file (primary location based on auto-export)"""
        self.comments_data["metadata"]["last_modified"] = datetime.now().isoformat()
        try:
            # If auto-export is enabled, save ONLY to that file
            if self.auto_export_path and Path(self.auto_export_path).exists():
                with open(self.auto_export_path, 'w', encoding='utf-8') as f:
                    json.dump(self.comments_data, f, ensure_ascii=False, indent=2)
            else:
                # Otherwise save to main comments file
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
    
    # Student adaptations (accessibility/curriculum adjustments)
    def set_student_adaptation(self, student_id: str, has_adaptation: bool):
        """Mark a student as having adaptations (curriculum adjustments)"""
        if "student_adaptations" not in self.comments_data:
            self.comments_data["student_adaptations"] = {}
        
        if has_adaptation:
            self.comments_data["student_adaptations"][student_id] = True
        elif student_id in self.comments_data["student_adaptations"]:
            del self.comments_data["student_adaptations"][student_id]
        
        self._save_comments()
    
    def get_student_adaptation(self, student_id: str) -> bool:
        """Check if a student has adaptations"""
        if "student_adaptations" not in self.comments_data:
            self.comments_data["student_adaptations"] = {}
        return self.comments_data["student_adaptations"].get(student_id, False)
    
    def get_all_adapted_students(self) -> List[str]:
        """Get list of all students with adaptations"""
        if "student_adaptations" not in self.comments_data:
            self.comments_data["student_adaptations"] = {}
        return list(self.comments_data["student_adaptations"].keys())
    
    # Auto-export management
    def set_auto_export_path(self, path: Optional[str]):
        """Set the path to automatically export/sync comments to (from imported file)"""
        if path:
            self.auto_export_path = str(path)
            # Reload comments from the new auto-export path
            self.comments_data = self._load_comments()
        else:
            self.auto_export_path = None
    
    def get_auto_export_path(self) -> Optional[str]:
        """Get the current auto-export path"""
        return self.auto_export_path
    
    def restore_last_imported_file(self) -> bool:
        """Try to restore the last imported file automatically"""
        imported_dir = Path("imported_comments")
        if not imported_dir.exists():
            return False
        
        # Find the most recent JSON file in imported_comments
        json_files = sorted(imported_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        if json_files:
            latest_file = json_files[0]
            self.set_auto_export_path(str(latest_file))
            return True
        
        return False
    
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
            
            # Ensure imported data has correct structure
            imported_data = self._ensure_structure(imported_data)
            
            if merge:
                # Merge with existing data
                for key in ["student_comments", "subject_comments", "group_comments", "session_comments", "student_adaptations"]:
                    if key in imported_data and key in self.comments_data:
                        self.comments_data[key].update(imported_data[key])
            else:
                # Replace existing data but ensure structure is maintained
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
        if "student_adaptations" not in self.comments_data:
            self.comments_data["student_adaptations"] = {}
        
        return {
            "student_comments": sum(len(comments) for comments in self.comments_data["student_comments"].values()),
            "subject_comments": len(self.comments_data["subject_comments"]),
            "group_comments": len(self.comments_data["group_comments"]),
            "session_comments": len(self.comments_data["session_comments"]),
            "student_adaptations": len(self.comments_data["student_adaptations"]),
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


def render_student_adaptation_toggle(
    comment_manager: CommentsManager,
    student_id: str,
    student_name: str = "",
    key_suffix: str = ""
) -> bool:
    """Render a toggle to mark a student as having adaptations"""
    
    has_adaptation = comment_manager.get_student_adaptation(student_id)
    
    toggle_key = f"adaptation_toggle_{student_id}_{key_suffix}"
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**{student_name or student_id}**")
    with col2:
        new_value = st.checkbox(
            "Adaptació 🎯",
            value=has_adaptation,
            key=toggle_key,
            help="Marca si aquest alumne té adaptació curricular"
        )
    
    if new_value != has_adaptation:
        comment_manager.set_student_adaptation(student_id, new_value)
        st.success("✓ Adaptació actualitzada!")
    
    return new_value


def render_adaptation_badge(comment_manager: CommentsManager, student_id: str) -> str:
    """Return a badge string to display if student has adaptation"""
    if comment_manager.get_student_adaptation(student_id):
        return "🎯"
    return ""


def render_comments_management_sidebar(comment_manager: CommentsManager):
    """Render comments management options in sidebar"""
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 💬 Gestió de Comentaris i Adaptacions")
        
        # Statistics
        stats = comment_manager.get_stats()
        total_comments = sum(v for k, v in stats.items() if k != "student_adaptations")
        adapted_count = stats.get("student_adaptations", 0)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Comentaris", total_comments)
        with col2:
            st.metric("Alumnes adaptació 🎯", adapted_count)
        
        # Show auto-export status
        auto_path = comment_manager.get_auto_export_path()
        if auto_path:
            st.markdown("---")
            st.markdown("### 💾 Sincronització Automàtica")
            st.success("✅ Activa")
            st.caption(f"📍 Fitxer: `{Path(auto_path).name}`")
            st.caption("Els canvis es guarden automàticament")
        
        st.markdown("---")
        
        # Show breakdown if there are comments
        if total_comments > 0:
            st.caption("**Desglose comentaris:**")
            for key, count in stats.items():
                if key != "student_adaptations" and count > 0:
                    label = {
                        "student_comments": "Alumnes",
                        "subject_comments": "Matèries", 
                        "group_comments": "Grups",
                        "session_comments": "Sessions"
                    }.get(key, key)
                    st.caption(f"• {label}: {count}")
        
        # Show adapted students if any exist
        if adapted_count > 0:
            with st.expander(f"🎯 Alumnes amb adaptació ({adapted_count})"):
                adapted_students = comment_manager.get_all_adapted_students()
                for student_id in sorted(adapted_students):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.caption(f"📌 {student_id}")
                    with col2:
                        if st.button("❌", key=f"remove_adaptation_{student_id}", help="Treure marca d'adaptació"):
                            comment_manager.set_student_adaptation(student_id, False)
                            st.success("✓ Adaptació treta!")
                            st.rerun()
        
        # Quick adaptation add section
        with st.expander("➕ Marcar alumne amb adaptació"):
            student_id_input = st.text_input(
                "ID de l'alumne",
                placeholder="Entra ID de l'alumne (ex: 12345)",
                help="Entra l'ID de l'alumne per marcar-lo com a adaptació",
                key="add_adaptation_input"
            )
            if st.button("✅ Marcar", help="Marcar aquest alumne com a adaptació"):
                if student_id_input.strip():
                    comment_manager.set_student_adaptation(student_id_input.strip(), True)
                    st.success(f"✓ Alumne {student_id_input.strip()} marcat amb adaptació!")
                    st.rerun()
                else:
                    st.warning("Si us plau, entra un ID d'alumne")
        
        # Export/Import section
        with st.expander("📂 Importar/Exportar"):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📥 Exportar", help="Exportar comentaris i adaptacions a JSON"):
                    export_path = f"comments_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    comment_manager.export_comments(export_path)
                    st.success(f"Exportat a {export_path}")
            
            with col2:
                uploaded_file = st.file_uploader("📤 Importar", type=['json'], help="Importar comentaris des d'un JSON")
                if uploaded_file:
                    # Use session state to prevent re-importing the same file multiple times
                    if f"imported_file_{uploaded_file.name}" not in st.session_state:
                        try:
                            # Create imported_comments directory if it doesn't exist
                            imported_dir = Path("imported_comments")
                            imported_dir.mkdir(exist_ok=True)
                            
                            # Save uploaded file to persistent location
                            persistent_path = imported_dir / uploaded_file.name
                            with open(persistent_path, 'wb') as f:
                                f.write(uploaded_file.getvalue())
                            
                            # Import from persistent file
                            if comment_manager.import_comments(str(persistent_path), merge=True):
                                # Set auto-export path to the imported file
                                comment_manager.set_auto_export_path(str(persistent_path))
                                st.session_state[f"imported_file_{uploaded_file.name}"] = True
                                st.session_state['last_imported_file'] = str(persistent_path)
                                
                                st.success("✅ Comentaris importats correctament!")
                                st.info(f"📍 Fitxer guardat: {persistent_path}")
                                st.info(f"📊 Estadístiques: {comment_manager.get_stats()}")
                                st.info("💾 Els canvis es sincronitzaran automàticament en aquest fitxer")
                            else:
                                st.error("❌ Error important comentaris")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                    else:
                        # Show current auto-export status
                        auto_path = comment_manager.get_auto_export_path()
                        if auto_path:
                            st.info(f"✅ Fitxer '{uploaded_file.name}' ja importat")
                            st.caption(f"📍 Ubicació: {auto_path}")
                            st.caption("💾 Els canvis es sincronitzen automàticament")
                        else:
                            st.info(f"✅ Fitxer '{uploaded_file.name}' ja importat")
            
            # Option to clear auto-export
            st.markdown("---")
            if comment_manager.get_auto_export_path():
                if st.button("❌ Aturar sincronització", help="Deixar de sincronitzar automàticament"):
                    comment_manager.set_auto_export_path(None)
                    st.info("✓ Sincronització aturat")
                    st.rerun()
        
        # Clear all comments
        if st.button("🗑️ Esborrar tots", help="Esborrar tots els comentaris", type="secondary"):
            comment_manager.clear_all_comments()
            st.success("Comentaris esborrats!")
            st.rerun()