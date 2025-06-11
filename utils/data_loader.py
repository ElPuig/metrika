import pandas as pd

def load_data(file_path:str):
    # Primero cargamos todos los datos como string
    data = pd.read_csv(file_path, header=0, na_filter=False)
    
    # Convertimos las columnas de conteo a numéricas
    count_columns = ['NA_COUNT', 'AS_COUNT', 'AN_COUNT', 'AE_COUNT']
    for col in count_columns:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0).astype(int)
    
    return data