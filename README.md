# Metrika - Eina d'Extracció i Anàlisi d'Informes Acadèmics

Una aplicació web basada en Streamlit per analitzar i visualitzar dades del rendiment acadèmic dels estudiants a partir d'informes escolars.

## Com funciona

Metrika ofereix tres modes principals de treball:

1. **Actes CSV** (Visualització directa)
   - Carrega directament fitxers d'actes CSV exportats d'Esfera
   - Visualitza estadístiques globals, per matèria i per alumne
   - Suporta qualificacions en format "Assolit-X", "No assolit", "Convalidat" i "Pendent"
   - Analitza fins a 100 matèries per alumne (m1-m100, q1-q100, c1-c100)

2. **Convertir CSV a JSON**
   - Converteix fitxers CSV extrets de les actes d'Esfera a format JSON
   - Els fitxers JSON es poden utilitzar per a anàlisis més complexes
   - Manté l'històric per a comparacions entre trimestres

3. **Visualitzar Estadístiques**
   - Treballa amb fitxers JSON generats prèviament
   - Introdueix el path a la carpeta que conté els fitxers JSON (T1.json, T2.json, T3.json)
   - Visualitza evolució temporal i comparatives entre trimestres

## Característiques

### Implementades
- Visualització directa d'actes CSV exportades d'Esfera
- Suport per a qualificacions en format "Assolit-X", "No assolit", "Convalidat", "Pendent"
- Vista global amb estadístiques generals i distribució de qualificacions
- Vista per matèria amb estadístiques específiques i llista d'alumnes
- Vista per alumne amb resum complet de qualificacions i comentaris
- Visualització interactiva del rendiment dels estudiants
- Anàlisi i estadístiques per matèria
- Seguiment individual del rendiment dels estudiants
- Visualització detallada de la distribució de notes
- Anàlisi comparatiu entre trimestres
- Seguiment de l'evolució dels estudiants
- Comentaris i retroalimentació detallada per matèria
- Filtre per curs (1r, 2n, 3r) en totes les visualitzacions
- Generació de dades aleatòries per a proves i simulacions

### No implementades
- Exportació de dades a altres formats
- Integració amb sistemes externs
- Gestió d'usuaris i permisos
- Filtres per 4t d'ESO
- Adaptació per Batxillerat i CCFF

## Estructura del Projecte

```
├── app.py         # Aplicació principal
├── requirements.txt       # Dependències del projecte
├── sections/            # Seccions principals de l'aplicació
│   ├── acta_viewer.py   # Visualització d'actes CSV
│   ├── evolution.py     # Visualitzacions d'evolució de notes
│   ├── student_marks.py # Visualització de notes per alumne
│   ├── student_selector.py # Selector d'alumnes
│   └── visualization.py # Visualitzacions generals i estadístiques
├── utils/               # Funcions i ajudants d'utilitat
│   ├── acta_loader.py   # Càrrega i processament d'actes CSV
│   ├── constants.py     # Constants i configuracions
│   ├── csv_to_json.py   # Conversió de CSV a JSON
│   ├── data_loader.py   # Càrrega de dades
│   ├── generate_dummy_data.py # Generació de dades de prova
│   └── helpers.py       # Funcions auxiliars
└── docs/               # Documentació i fitxers de dades (no traçat en el repositori)
```

## Instal·lació

1. Clona el repositori:
```bash
git clone [url-del-repositori]
cd metrika
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

### Visualització d'Actes CSV
- Càrrega directa de fitxers CSV d'actes exportats d'Esfera
- Suport per a format pipe-delimited amb fins a 100 matèries per alumne
- Processament automàtic de qualificacions:
  - **Assolit-X**: Qualificacions numèriques (0-10)
  - **No assolit**: Competència no assolida
  - **Convalidat**: Matèria convalidada
  - **Pendent**: Qualificació pendent
- **Vista Global**: Estadístiques generals, distribució de qualificacions, histograma de notes, rànquing d'alumnes
- **Vista per Matèria**: Estadístiques específiques, distribució, llista d'alumnes amb notes i comentaris
- **Vista per Alumne**: Resum complet, taxa d'èxit, mitjana, distribució i comentari general

### Visualització de Dades
- Taules de rendiment de l'aula
- Estadístiques per matèria
- Visualització de freqüència de notes
- Seguiment individual del rendiment
- Anàlisi comparatiu entre trimestres
- Filtre per curs en totes les visualitzacions

### Anàlisi d'Estudiants
- Seguiment individual del rendiment
- Visualització de l'evolució de notes
- Desglossament de notes per matèria
- Comentaris i retroalimentació detallada
- Evolució temporal per trimestre

### Generació de Dades
- Creació de dades aleatòries per a proves
- Generació de dades per diferents trimestres
- Manteniment de la coherència en les dades generades

## Dependències

El projecte utilitza diversos paquets Python clau:
- Streamlit per a la interfície web
- Pandas per a la manipulació de dades
- Plotly per a visualitzacions interactives
- Biblioteques de processament de PDF (pdfplumber)
- Diverses eines d'anàlisi i visualització de dades

## Contribució

1. Fes un fork del repositori
2. Crea una branca per a la teva funcionalitat
3. Fes commit dels teus canvis
4. Fes push a la branca
5. Crea una Pull Request

## Llicència

Copyright (C) 2024  Metrika

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
