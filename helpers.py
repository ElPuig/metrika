import csv
import re
from tabula import read_pdf
import pandas as pd
import os
import pdfplumber
import tkinter as tk
from tkinter import filedialog
 
MARKS = ["NA", "AS", "AN", "AE"]
MARK_COUNTS = ["NA_COUNT", "AS_COUNT", "AN_COUNT", "AE_COUNT"]
SUBJ_NAMES = ["CAT", "CAST", "ANG", "MAT", "BG", "FQ", "TD", "CS", "MUS", "EDF", "OPT", "PG_I", "PG_II", "COMP_DIG", "COMP_PERS", "COMP_CIUT", "COMP_EMPR"]
COL_NAMES={
"Identificador de l'alumne/a": "id",
"Nom i cognoms de l'alumne/a": "NOM",
"Ll. Cat.": "CAT",
"Ll. Cast.": "CAST",
"Ll. Estr.": "ANG",
"Mat.": "MAT",
"BG": "BG",
"FQ": "FQ",
"TD": "TD",
"CS:GH": "CS",
"Mús.": "MUS",
"Ed. Fís.": "EDF",
"Optativa": "OPT",
"PG_I": "PG_I",
"PG_II": "PG_II",
"Comp. Dig.": "COMP_DIG",
"Comp. Pers.": "COMP_PERS",
"Comp. Ciut.": "COMP_CIUT",
"Comp. Empr.": "COMP_EMPR"
}

def save_csv(df:pd.DataFrame, file_path:str):
        """Guarda los datos de un pandas DataFrame en un archivo CSV con el mismo nombre que el archivo PDF original"""
        root, ext = os.path.splitext(file_path)
        csv_output_path = f"{root}.csv"
        df.to_csv(csv_output_path, index=False)
        print(f"Successfully saved PDF table contents into CSV file (path: {csv_output_path})")


def digest_data(df:pd.DataFrame)->pd.DataFrame:
    """Procesa y homogeniza datos extraídos del PDF del sistema Esfera"""
    # Trim and remove line breaks from dataframe content
    df = df.replace(r'\n',' ', regex=True) 
    df = df.replace(r'\s+,',',', regex=True) 
    # Remove line breaks in column names
    df.columns = df.columns.str.replace(r'\n',' ', regex=True)
    # Remove PI columns
    df = df[df.columns.drop(list(df.filter(regex='PI')))]
    # Rename columns using dictionary
    df.rename(COL_NAMES, axis=1, inplace=True)
    # Remove columns not present in dictionary
    df.drop(columns=[col for col in df.columns if col not in COL_NAMES.values()], inplace=True)
    # Mark consistency
    for col in df.columns:
        # consistency for any mark like NA, AS, AN or AE
        for mark in MARKS:
            df[col] = df[col].apply(
                lambda x: mark if mark in str(x) else x
            )
        # replace empty values in subjets by pd.NA
        if col in SUBJ_NAMES:
            df[col] = df[col].apply(
                lambda x: pd.NA if str(x) not in MARKS else x
            )
    # Add count columns
    df['NA_COUNT'] = (df == 'NA').sum(axis=1)
    df['AS_COUNT'] = (df == 'AS').sum(axis=1)
    df['AN_COUNT'] = (df == 'AN').sum(axis=1)
    df['AE_COUNT'] = (df == 'AE').sum(axis=1)
    return df


def pdf_to_table(pdf_file:str, digest=False):
    with pdfplumber.open(pdf_file) as pdf:
        dfs = list()
        for i in [0, 1]:            
            # Extract table from the first page
            page = pdf.pages[i]
            table = page.extract_table()
            # Convert to DataFrame and set first row as header
            if table:  # Check if table was extracted
                df = pd.DataFrame(table[1:], columns=table[0])
                print(df.columns)
                df = df.set_index('N.')
            else:
                df = pd.DataFrame()  # Empty DataFrame if no table found
            dfs.append(df)
        df = pd.concat(dfs)
        if digest:
            df = digest_data(df)
        save_csv(df, pdf_file)

        print(df.head())



def trim_csv(input_file:str, output_file:str):
    with open(input_file, 'r', newline='', encoding='utf-8') as infile, \
        open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        for row in reader:
            print(f"Raw row:\t{row}")
            # cleaned_row = [cell.strip().replace('\n', '').replace('\r', '') for cell in row]
            for mark in MARKS:
                pattern = rf"(?<=;)[^;]*{mark}[^;]*(?=;)"
                print(pattern)
                cleaned_row = [re.sub(pattern, mark, cell) for cell in row]
            print(f"Digested row:\t{cleaned_row}")
            writer.writerow(cleaned_row)


def select_folder():
   root = tk.Tk()
   root.withdraw()
   root.call('wm', 'attributes', '.', '-topmost', True)
   folder_path = filedialog.askdirectory(master=root)
   root.destroy()
   return folder_path

def highlight_max_row(s):
    is_max = s == s.max()
    return ['background-color: lightgreen' if v else '' for v in is_max]