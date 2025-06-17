#!/usr/bin/env python3
"""
Test script for CSV to JSON conversion functionality
"""

import sys
import os
import json

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.csv_to_json import process_csv_to_json

def test_csv_conversion():
    """Test the CSV to JSON conversion with fake data"""
    
    # Paths
    test_csv_file = os.path.join(os.path.dirname(__file__), 'test_data.csv')
    test_output_file = os.path.join(os.path.dirname(__file__), 'test_output.json')
    
    print("🧪 Iniciant test de conversió CSV a JSON...")
    print(f"📁 Fitxer CSV d'entrada: {test_csv_file}")
    print(f"📁 Fitxer JSON de sortida: {test_output_file}")
    print("-" * 50)
    
    # Check if test CSV file exists
    if not os.path.exists(test_csv_file):
        print(f"❌ Error: No s'ha trobat el fitxer de test: {test_csv_file}")
        return False
    
    try:
        # Convert CSV to JSON
        print("🔄 Convertint CSV a JSON...")
        success, message, json_data = process_csv_to_json(test_csv_file, test_output_file, "T1")
        
        if success:
            print("✅ Conversió completada amb èxit!")
            print(f"📝 Missatge: {message}")
            
            # Load and display the JSON data
            with open(test_output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"\n📊 Dades convertides:")
            
            # Handle both new and old structures
            if isinstance(data, dict) and 'estudiants' in data:
                # New structure
                print(f"   - Grup: {data.get('grup', 'No especificat')}")
                print(f"   - Trimestre: {data.get('trimestre', 'No especificat')}")
                print(f"   - Nombre d'estudiants: {len(data['estudiants'])}")
                
                # Display first student details
                if data['estudiants']:
                    first_student = data['estudiants'][0]
                    print(f"\n👤 Primer estudiant:")
                    print(f"   - ID: {first_student['id']}")
                    print(f"   - Nom: {first_student['nom_cognoms']}")
                    print(f"   - Nombre de matèries: {len(first_student['materies'])}")
                    
                    print(f"\n📚 Matèries del primer estudiant:")
                    for i, materia in enumerate(first_student['materies'], 1):
                        print(f"   {i}. {materia['materia']}")
                        print(f"      Qualificació: {materia['qualificacio']}")
                        print(f"      Comentari: {materia['comentari']}")
                        print()
            else:
                # Old structure (direct array)
                print(f"   - Nombre d'estudiants: {len(data)}")
                
                # Display first student details
                if data:
                    first_student = data[0]
                    print(f"\n👤 Primer estudiant:")
                    print(f"   - ID: {first_student['id']}")
                    print(f"   - Nom: {first_student['nom_cognoms']}")
                    print(f"   - Nombre de matèries: {len(first_student['materies'])}")
                    
                    print(f"\n📚 Matèries del primer estudiant:")
                    for i, materia in enumerate(first_student['materies'], 1):
                        print(f"   {i}. {materia['materia']}")
                        print(f"      Qualificació: {materia['qualificacio']}")
                        print(f"      Comentari: {materia['comentari']}")
                        print()
            
            # Validate structure
            print("🔍 Validant estructura del JSON...")
            validation_errors = []
            
            # Check if it's the new structure (with grup, trimestre, students) or old structure
            if isinstance(data, dict) and 'estudiants' in data:
                # New structure
                print("📋 Estructura nova detectada (grup, trimestre, estudiants)")
                
                # Check top-level fields
                top_level_fields = ['grup', 'trimestre', 'estudiants', 'metrika_version']
                for field in top_level_fields:
                    if field not in data:
                        validation_errors.append(f"Falta el camp de nivell superior '{field}'")
                
                # Check version
                if 'metrika_version' in data:
                    print(f"   - Versió del fitxer: {data['metrika_version']}")
                
                # Check students array
                if 'estudiants' in data and isinstance(data['estudiants'], list):
                    students = data['estudiants']
                    print(f"   - Nombre d'estudiants: {len(students)}")
                    
                    for i, student in enumerate(students):
                        # Check required fields for each student
                        required_fields = ['id', 'nom_cognoms']
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
                else:
                    validation_errors.append("El camp 'estudiants' no és una llista vàlida")
            else:
                # Old structure (direct array of students)
                print("📋 Estructura antiga detectada (array directa d'estudiants)")
                
                for i, student in enumerate(data):
                    # Check required fields
                    required_fields = ['id', 'nom_cognoms']
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
                print("✅ Estructura del JSON vàlida!")
            
            print(f"\n💾 Fitxer JSON guardat a: {test_output_file}")
            return True
            
        else:
            print(f"❌ Error en la conversió: {message}")
            return False
            
    except Exception as e:
        print(f"❌ Excepció durant el test: {str(e)}")
        return False

def cleanup_test_files():
    """Clean up test output files"""
    test_output_file = os.path.join(os.path.dirname(__file__), 'test_output.json')
    if os.path.exists(test_output_file):
        try:
            os.remove(test_output_file)
            print(f"🧹 Fitxer de test eliminat: {test_output_file}")
        except Exception as e:
            print(f"⚠️ No s'ha pogut eliminar el fitxer de test: {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TEST DE CONVERSIÓ CSV A JSON")
    print("=" * 60)
    
    # Run test
    success = test_csv_conversion()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEST COMPLETAT AMB ÈXIT!")
        print("✅ La conversió CSV a JSON funciona correctament")
    else:
        print("💥 TEST FALLIT!")
        print("❌ Hi ha hagut problemes en la conversió")
    
    # Ask if user wants to keep test files
    response = input("\n¿Vols eliminar el fitxer JSON de test? (s/n): ").lower().strip()
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        cleanup_test_files()
    else:
        print("💾 Fitxer JSON de test mantingut per a inspecció manual")
    
    print("=" * 60) 