import json
import random
import os

# Possible qualifications
qualifications = [
    "No assoliment",
    "Assoliment satisfactori",
    "Assoliment notable",
    "Assoliment excel·lent"
]

def randomize_qualifications(file_path):
    """Randomize qualifications in a JSON file for entries that already have a value."""
    # Read the JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Randomize qualifications for entries that already have a value
    for student in data:
        for materia in student['materies']:
            if materia['qualificacio']:  # If there's already a qualification
                materia['qualificacio'] = random.choice(qualifications)

    # Write back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # Get the current directory
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(current_dir, 'docs', 'data', 'T3.json')
    randomize_qualifications(file_path) 