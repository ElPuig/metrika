# Instal.lacio

## Requisits

- Python 3.12 o superior.
- pip actualitzat.

## Passos

1. Clona el repositori i entra al directori del projecte.
2. Crea i activa un entorn virtual.
3. Instal.la dependencies.

```bash
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
```

## Inici de l'aplicacio

```bash
streamlit run app.py
```

L'aplicacio quedara disponible a `http://localhost:8501`.

## Inici de la documentacio local

```bash
mkdocs serve
```

La guia quedara disponible a `http://127.0.0.1:8000`.
