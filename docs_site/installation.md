# Instal-lacio

## Requisits previs

- Python 3.12 o superior
- pip actualitzat

## Instal-lacio pas a pas (Windows)

1. Clona el repositori i entra al directori.
2. Crea i activa un entorn virtual.
3. Instal-la dependencies del projecte.

```bash
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
```

## Verificacio rapida

Engega l'aplicacio:

```bash
streamlit run app.py
```

URL esperada: http://localhost:8501

## Que has de veure en iniciar

- Pantalla de carrega de fitxers CSV.
- Missatge per arrossegar almenys un fitxer.
- Sidebar amb informacio de versio i enllac a guia.

!!! tip "Si algun paquet falla"
	Torna a executar la instal-lacio i comprova que l'entorn virtual estigui activat abans de llançar Streamlit.
