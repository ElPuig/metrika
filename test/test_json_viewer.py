#!/usr/bin/env python3
"""
Test script for JSON viewer functionality with new structure
"""

import sys
import os
import json

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from json_viewer import load_json_files, get_json_files

def test_json_viewer():
    """Test the JSON viewer with new structure"""
    
    # Paths
    test_dir = os.path.dirname(__file__)
    
    print("🧪 Iniciant test del JSON viewer...")
    print(f"📁 Directori de test: {test_dir}")
    print("-" * 50)
    
    # Get JSON files in test directory
    json_files = get_json_files(test_dir)
    print(f"📄 Fitxers JSON trobats: {json_files}")
    
    if not json_files:
        print("❌ No s'han trobat fitxers JSON per testejar")
        return False
    
    try:
        # Load JSON files
        print("🔄 Carregant fitxers JSON...")
        students, file_info = load_json_files(test_dir, json_files)
        
        print(f"✅ S'han carregat {len(students)} estudiants")
        print(f"📋 Informació dels fitxers:")
        
        for filename, info in file_info.items():
            print(f"   - {filename}:")
            print(f"     Display name: {info['display_name']}")
            print(f"     Grup: {info['grup']}")
            print(f"     Trimestre: {info['trimestre']}")
            print(f"     Versió: {info['version']}")
        
        # Validate student data
        print(f"\n🔍 Validant dades dels estudiants...")
        validation_errors = []
        
        for i, student in enumerate(students):
            # Check required fields
            required_fields = ['id', 'nom_cognoms', 'trimestre', 'grup', 'file_display_name']
            for field in required_fields:
                if field not in student:
                    validation_errors.append(f"Estudiant {i}: Falta el camp '{field}'")
            
            # Check materies structure
            if 'materies' in student:
                for j, materia in enumerate(student['materies']):
                    materia_fields = ['materia', 'qualificacio', 'comentari']
                    for field in materia_fields:
                        if field not in materia:
                            validation_errors.append(f"Estudiant {i}, matèria {j}: Falta el camp '{field}'")
        
        if validation_errors:
            print("❌ Errors de validació trobats:")
            for error in validation_errors:
                print(f"   - {error}")
            return False
        else:
            print("✅ Dades dels estudiants vàlides!")
        
        # Show sample student data
        if students:
            print(f"\n👤 Mostra d'estudiant:")
            sample_student = students[0]
            print(f"   - ID: {sample_student['id']}")
            print(f"   - Nom: {sample_student['nom_cognoms']}")
            print(f"   - Grup: {sample_student['grup']}")
            print(f"   - Trimestre: {sample_student['trimestre']}")
            print(f"   - Display name: {sample_student['file_display_name']}")
            print(f"   - Nombre de matèries: {len(sample_student['materies'])}")
            
            if sample_student['materies']:
                print(f"   - Primera matèria: {sample_student['materies'][0]['materia']}")
        
        print(f"\n🎉 Test completat amb èxit!")
        return True
        
    except Exception as e:
        print(f"❌ Excepció durant el test: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TEST DEL JSON VIEWER")
    print("=" * 60)
    
    # Run test
    success = test_json_viewer()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEST COMPLETAT AMB ÈXIT!")
        print("✅ El JSON viewer funciona correctament amb la nova estructura")
    else:
        print("💥 TEST FALLIT!")
        print("❌ Hi ha hagut problemes amb el JSON viewer")
    
    print("=" * 60) 