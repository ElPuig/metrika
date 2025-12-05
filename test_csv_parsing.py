"""
Test script to verify CSV parsing functionality
"""
from utils.acta_csv_loader import parse_acta_csv
import json

# Path to the test CSV file
csv_path = r"c:\Users\elpel\root\edu\metrika\docs\actes_csv\ActaAvaluacioGraella_ESO LOE (Modificada)_4_ESO 4A_1_477427.csv"

# Parse the CSV
students = parse_acta_csv(csv_path)

# Print results
print(f"Total students parsed: {len(students)}")
print("\n" + "="*80)

# Show first student details
if students:
    first_student = students[0]
    print(f"\nFirst student: {first_student['nom']}")
    print(f"ID: {first_student['id']}")
    print(f"Grup: {first_student['grup_codi']}")
    print(f"Avaluació: {first_student['numero_avaluacio']}")
    print(f"\nCurrent level subjects (4t): {len(first_student['subjects'])}")
    for subject in first_student['subjects'][:3]:  # Show first 3
        print(f"  - {subject['subject']}: {subject['qualification']}")
    
    print(f"\nPending subjects: {len(first_student['pending_subjects'])}")
    for subject in first_student['pending_subjects'][:3]:  # Show first 3
        print(f"  - {subject['subject']}: {subject['qualification']}")
    
    print(f"\nGeneral comment: {first_student['comentari_general'][:100]}...")

# Show statistics
print("\n" + "="*80)
print("\nStatistics:")
total_4t_subjects = sum(len(s['subjects']) for s in students)
total_pending = sum(len(s['pending_subjects']) for s in students)
print(f"Total 4t subjects: {total_4t_subjects}")
print(f"Total pending subjects: {total_pending}")

# Save as JSON for testing
output_json = {
    "grup": students[0]['grup_codi'] if students else "Unknown",
    "trimestre": f"T{students[0]['numero_avaluacio']}" if students else "T1",
    "nom_ensenyament": students[0]['nom_ensenyament'] if students else "Unknown",
    "metrika_version": "0.1.0-csv",
    "estudiants": students
}

output_path = r"c:\Users\elpel\root\edu\metrika\test_csv_output.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output_json, f, indent=2, ensure_ascii=False)

print(f"\nTest output saved to: {output_path}")
