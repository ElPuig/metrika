import pandas as pd

def load_data(file_path:str):
    return pd.read_csv(file_path, header=0, dtype=str, na_filter=False)