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

- `00_grup_overview.png`
- `01_grup_resum_suspensos_alumne.png`
- `02_grup_assignatures_mes_suspeses.png`
- `03_grup_distribucio_qualificacions_assignatura.png`
- `04_grup_mapa_calor_alumnes_assignatures.png`
- `05_grup_ranking_mitjana_numerica.png`
- `00_materia_overview.png`
- `06_materia_comentaris_per_alumne.png`
- `07_materia_distribucio_qualificacions.png`
- `08_materia_aprovats_no_aprovats.png`
- `00_alumne_overview.png`
- `09_alumne_nota_mitjana.png`
- `10_alumne_flag_adaptacio.png`
- `11_alumne_distribucio_qualificacions.png`
- `12_alumne_materies_pendents.png` (opcional, només si n'hi ha)
- `13_comparador_evolucio_grup_grafica.png`
- `14_comparador_distribucio_qualificacions_trimestre.png`
- `15_comparador_evolucio_mitjana_materia.png`
- `16_comparador_alumnes_milloren.png`
- `17_comparador_alumnes_regressio.png`
- `18_comparador_evolucio_alumne_overview.png`
- `19_comparador_taula_comparacio_materia.png`
- `20_exportacio_overview.png`

## Parametres utiles

- `--url` per canviar URL de Streamlit (per defecte: `http://localhost:8501`)
- `--output-dir` per definir una carpeta diferent de sortida
- `--headless false` per veure el navegador en viu durant les captures

## Notes

- L'script espera que l'app estigui completament carregada.
- Si canvien els noms de pestanyes o l'estructura de la UI, cal actualitzar l'script.
