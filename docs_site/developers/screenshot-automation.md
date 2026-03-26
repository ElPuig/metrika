# Automatitzar captures de pantalla

Aquesta guia explica com generar captures de les seccions de Metrika despres de carregar un CSV.

## Resum del flux

1. Engega Streamlit.
2. Llança l'script de captures amb el fitxer CSV.
3. L'script puja el CSV i captura les pestanyes principals.

## Requisits

- Dependencia Python: `playwright`
- Navegador Playwright instal-lat (Chromium)

Instal-lacio recomanada:

```bash
pip install -r requirements-test.txt
python -m playwright install chromium
```

## Comandes

En una terminal, inicia Metrika:

```bash
streamlit run app.py
```

En una altra terminal, executa:

```bash
python calc_scripts/capture_metrika_screenshots.py --csv "docs/data/el_teu_fitxer.csv" --output-dir "docs_site/assets/screenshots"
```

## Sortida

Per defecte, l'script guarda les captures a una ruta relativa (`docs_site/assets/screenshots/`) des del directori on l'executes.

Per publicar-les al site de MkDocs, han d'acabar a `docs_site/assets/screenshots/` de l'arrel del repositori.

Fitxers esperats:

- `01_grup.png`
- `02_materia.png`
- `03_alumne.png`
- `04_comparador.png`
- `04_comparador_grup.png`
- `05_comparador_alumne.png`
- `05_exportacio.png`
- `06_exportacio.png`

## Parametres utiles

- `--url` per canviar URL de Streamlit (per defecte: `http://localhost:8501`)
- `--output-dir` per definir una carpeta diferent de sortida
- `--headless false` per veure el navegador en viu durant les captures

## Notes

- L'script espera que l'app estigui completament carregada.
- Si canvien els noms de pestanyes o l'estructura de la UI, cal actualitzar l'script.
