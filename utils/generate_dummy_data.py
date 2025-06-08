import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_random_grade():
    """Generate a random grade with weighted probabilities"""
    grades = ['No assoliment', 'Assoliment satisfactori', 'Assoliment notable', 'Assoliment excel·lent']
    weights = [0.3, 0.4, 0.2, 0.1]  # Adjust these weights as needed
    return random.choices(grades, weights=weights)[0]

def generate_random_comment():
    """Generate a random comment based on the grade"""
    comments = {
        'No assoliment': [
            "No ha assolit els objectius mínims de l'assignatura.",
            "Cal més esforç i dedicació per assolir els objectius.",
            "No ha treballat prou durant el trimestre."
        ],
        'Assoliment satisfactori': [
            "Ha assolit els objectius bàsics de l'assignatura.",
            "Bona feina, però hi ha marge de millora.",
            "Assoleix els objectius mínims amb esforç."
        ],
        'Assoliment notable': [
            "Excel·lent treball durant el trimestre.",
            "Ha demostrat un alt nivell de compromís.",
            "Destaca per la seva dedicació i bons resultats."
        ],
        'Assoliment excel·lent': [
            "Rendiment excepcional en tots els aspectes.",
            "Destaca per la seva excel·lència i dedicació.",
            "Resultats excel·lents en totes les avaluacions."
        ]
    }
    grade = generate_random_grade()
    return grade, random.choice(comments[grade])

def generate_dates():
    """Generate dates for T2 and Final trimesters"""
    t2_date = datetime(2025, 3, 12, 1, 0, 0)  # T2 date
    final_date = datetime(2025, 6, 20, 1, 0, 0)  # Final date
    return t2_date, final_date

def generate_dummy_data(input_file, output_t2, output_final):
    """Generate dummy data for T2 and Final trimesters"""
    # Read the original CSV
    df = pd.read_csv(input_file, sep='|')
    
    # Generate T2 data
    df_t2 = df.copy()
    df_t2['data_sessio_avaluacio'] = generate_dates()[0].strftime('%a %b %d %H:%M:%S CET %Y')
    df_t2['numero_avaluacio'] = 2
    
    # Generate Final data
    df_final = df.copy()
    df_final['data_sessio_avaluacio'] = generate_dates()[1].strftime('%a %b %d %H:%M:%S CET %Y')
    df_final['numero_avaluacio'] = 3
    
    # Update grades and comments for each subject
    for df_trim in [df_t2, df_final]:
        for col in df_trim.columns:
            if col.startswith('m') and col[1:].isdigit():
                grade, comment = generate_random_comment()
                # Keep the original subject name in 'm' column
                df_trim[col.replace('m', 'q')] = grade  # Put grade in 'q' column
                df_trim[col.replace('m', 'c')] = comment  # Put comment in 'c' column
    
    # Save the generated data
    df_t2.to_csv(output_t2, sep='|', index=False)
    df_final.to_csv(output_final, sep='|', index=False)

if __name__ == "__main__":
    input_file = "docs/dummy1.csv"
    output_t2 = "docs/dummy2.csv"
    output_final = "docs/dummy3.csv"
    
    generate_dummy_data(input_file, output_t2, output_final)
    print("Dummy data generated successfully!") 