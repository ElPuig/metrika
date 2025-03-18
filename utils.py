import csv
import re
from tabula import read_pdf
import pandas as pd
import os
 

def trim_csv(input_file:str, output_file:str):
    marks = ["NA", "AS", "AN", "AE"]
    with open(input_file, 'r', newline='', encoding='utf-8') as infile, \
        open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        for row in reader:
            print(f"Raw row:\t{row}")
            # cleaned_row = [cell.strip().replace('\n', '').replace('\r', '') for cell in row]
            for mark in marks:
                pattern = rf"(?<=;)[^;]*{mark}[^;]*(?=;)"
                print(pattern)
                cleaned_row = [re.sub(pattern, mark, cell) for cell in row]
            print(f"Digested row:\t{cleaned_row}")
            writer.writerow(cleaned_row)


def extract_table(pdf_file:str, column_names:list = None, save_file:bool = False):
    if column_names == None:
        column_names = [
            """N.""",
        """Identificador de
l'alumne/a""",
        """Nom i cognoms de
l'alumne/a""",
        "MAE",
        "PI",
        "Ll. Cat.",
        "PI",
        "Aranès",
        "PI",
        "Ll. Cast.",
        "PI",
        "Ll. Estr.",
        "PI",
        "Mat.",
        "PI",
        "BG",
        "PI",
        "FQ",
        "PI",
        "TD",
        "PI",
        "CS:GH",
        "PI",
        "Mús.",
        "PI",
        "EPVA",
        "PI",
        "Ed. Fís.",
        "PI",
        "Optativa",
        "PI",
        "PG_I",
        "PI",
        "PG_II",
        "PI",
        """Comp.
Dig.""",
        "PI",
        """Comp.
Pers.""",
        "PI",
        """Comp.
Ciut.""",
        ]

    pandas_options = {
        "header": 0,
        "names":column_names
    }

    # area=[y1, x1, y2, x2]
    area=[235, 54, 534, 804]

    # columns positions: [63.75, 103.26, 147.20, 184.15, 204.66, 213.99]
    columns_x=[63.75,103.26,147.2,173.38,184.15,204.66,213.99,235.11,245.18,265.55,276.68,297.03,307.23,327.58,338.28,358.13,368.83,387.93,397.96,418.91,428.15,448.75,460.44,479.65,489.6,510.41,521.15,540.65,551.01,574.76,584.29,611.66,622.25,649.01,659.71,680.26,690.19,711.11,720.81,740.9,751.86,773.86,782.99,803.3]

    print(len(columns_x))


    with open(pdf_file, 'rb') as file:
        # extract table from pages
        dfs = read_pdf(
            file,
            pages="1", # pages to extract table from
            area=area,
            columns=columns_x,
            pandas_options=pandas_options, # FAILS HERE
        )

        # concat all dfs to get one table
        data = pd.concat(
            dfs,
            axis=0,
            ignore_index=True
        )

        print(data.sample(5))

        # save pdf file
        if save_file:
            root, ext = os.path.splitext(pdf_file)
            csv_output_path = f"{root}.csv"
            data.to_csv(csv_output_path, index=False)
            print(f"Successfully saved PDF table contents into CSV file (path: {csv_output_path})")