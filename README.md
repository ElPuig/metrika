# Metrika - Eina d'Extracció i Anàlisi d'Informes Acadèmics

Una aplicació web basada en Streamlit per analitzar i visualitzar dades del rendiment acadèmic dels estudiants a partir d'informes escolars.

## Com funciona

Metrika funciona en dos passos principals:

1. **Convertir CSV a JSON**
   - Primer, has d'anar a la secció "Convertir CSV" del menú lateral
   - Aquí podràs convertir el fitxer CSV extret de les actes d'Esfera a format JSON
   - Aquests fitxers JSON són els que Metrika utilitza per mostrar les estadístiques

2. **Visualitzar Estadístiques**
   - Un cop tinguis els fitxers JSON, ves a la secció "Estadístiques"
   - Introdueix el path a la carpeta que conté els fitxers JSON (T1.json, T2.json, T3.json)
   - Podràs veure totes les estadístiques i visualitzacions disponibles

## Característiques

### Implementades
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

## Estructura del Projecte

```
├── json_viewer.py         # Utilitats de visualització de dades JSON
├── requirements.txt       # Dependències del projecte
├── sections/            # Seccions principals de l'aplicació
│   ├── evolution.py     # Visualitzacions d'evolució de notes
│   ├── student_marks.py # Visualització de notes per alumne
│   ├── student_selector.py # Selector d'alumnes
│   └── visualization.py # Visualitzacions generals i estadístiques
├── utils/               # Funcions i ajudants d'utilitat
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
streamlit run json_viewer.py
```

2. Accedeix a l'aplicació a través del teu navegador web a `http://localhost:8501`

## Característiques Principals

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

## Contacte

[La teva informació de contacte] 