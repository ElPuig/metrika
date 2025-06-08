# Eina d'Extracció i Anàlisi d'Informes Acadèmics

Una aplicació web basada en Streamlit per analitzar i visualitzar dades del rendiment acadèmic dels estudiants a partir d'informes escolars.

## Característiques

### Implementades
- Visualització interactiva del rendiment dels estudiants
- Anàlisi i estadístiques per matèria
- Seguiment individual del rendiment dels estudiants
- Visualització detallada de la distribució de notes

### No implementades
- Anàlisi comparatiu entre trimestres
- Seguiment de l'evolució dels estudiants
- Comentaris i retroalimentació detallada per matèria

## Estructura del Projecte

```
├── json_viewer.py         # Utilitats de visualització de dades JSON
├── requirements.txt       # Dependències del projecte
├── components/           # Components d'interfície reutilitzables
├── sections/            # Seccions principals de l'aplicació
├── utils/               # Funcions i ajudants d'utilitat
└── docs/               # Documentació i fitxers de dades (no traçat en el repositori)
```

## Instal·lació

1. Clona el repositori:
```bash
git clone [url-del-repositori]
cd esfextraction
```

2. Crea i activa un entorn virtual:
```bash
python -m venv venv
source venv/bin/activate  # A Windows: venv\Scripts\activate
```

3. Instal·la les dependències:
```bash
pip install -r requirements.txt
```

## Ús

1. Inicia l'aplicació Streamlit:
```bash
streamlit run app.py
```

2. Accedeix a l'aplicació a través del teu navegador web a `http://localhost:8501`

## Característiques Principals

### Visualització de Dades
- Taules de rendiment de l'aula
- Estadístiques per matèria
- Visualització de freqüència de notes
- Seguiment individual del rendiment
- Anàlisi comparatiu entre trimestres

### Anàlisi d'Estudiants
- Seguiment individual del rendiment
- Visualització de l'evolució de notes
- Desglossament de notes per matèria
- Comentaris i retroalimentació detallada

## Dependències

El projecte utilitza diversos paquets Python clau:
- Streamlit per a la interfície web
- Pandas per a la manipulació de dades
- Altair i Plotly per a visualitzacions
- Biblioteques de processament de PDF (pdf2image, pdfplumber)
- Diverses eines d'anàlisi i visualització de dades

## Contribució

1. Fes un fork del repositori
2. Crea una branca per a la teva funcionalitat
3. Fes commit dels teus canvis
4. Fes push a la branca
5. Crea una Pull Request

## Llicència

[Especifica la teva llicència aquí]

## Contacte

[La teva informació de contacte] 