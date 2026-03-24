# Metrika - Eina d'Extracció i Anàlisi d'Informes Acadèmics

Una aplicació web basada en Streamlit per analitzar i visualitzar dades del rendiment acadèmic dels estudiants a partir d'informes escolars.

## Com funciona

Metrika treballa amb un únic flux principal:

1. **Anàlisi d'actes CSV (ESO)**
   - Carrega fitxers CSV d'actes exportats d'Esfera
   - Visualitza estadístiques globals, per matèria i per alumne
   - Analitza fins a 100 matèries per alumne
   - **Classificació automàtica de matèries:**
     - Matèries de 4t: Es compten a les estadístiques generals
     - Matèries pendents (1r, 2n, 3r): Es mostren separadament, NO es compten a l'estadística global
   - Suporta qualificacions: "No assoliment", "Assoliment satisfactori", "Assoliment notable", "Assoliment excel·lent"

## Característiques

### Implementades
- **Suport CSV d'actes (ESO)**: Carrega fitxers CSV d'actes
- **Classificació automàtica de matèries**: Separa matèries actuals (4t) de pendents (1r, 2n, 3r)
- **Vista de matèries pendents**: Taula separada per a matèries de cursos anteriors (només visible a vista alumne)
- **Normalització transparent**: Processament automàtic de CSV d'actes
- **Exportació CSV del trimestre seleccionat**: Una fila per alumne i dues columnes per matèria (qualificació/comentari), amb ordenació per nombre d'alumnes
- Visualització directa d'actes CSV exportades d'Esfera (ESO)
- Suport per a qualificacions: "No assoliment", "Assoliment satisfactori", "Assoliment notable", "Assoliment excel·lent"
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
- Filtre per curs (1r, 2n, 3r, 4t) en totes les visualitzacions
- Generació de dades aleatòries per a proves i simulacions

### No implementades
- Integració amb sistemes externs
- Gestió d'usuaris i permisos
- Adaptació específica per Batxillerat (es pot utilitzar la funcionalitat actual)

## Estructura del CSV d'Actes (ESO)

El sistema suporta fitxers CSV amb la següent estructura:

### Format
- **Separador**: `|` (pipe)
- **Codificació**: UTF-8
- **Estructura**: Columnes fixes + triplets de matèries (m/q/c)

### Columnes principals
- `id`: Identificador de l'estudiant
- `nom_cognoms`: Nom complet
- `grup_codi`: Codi del grup (ex: ESO LOEM401)
- `numero_avaluacio`: Número de l'avaluació (1, 2, 3)
- `nom_ensenyament`: Nom de l'ensenyament

### Columnes de matèries (fins a 100)
Cada matèria es representa amb 3 columnes:
- `m1`, `m2`, ..., `m100`: Nom de la matèria
- `q1`, `q2`, ..., `q100`: Qualificació
- `c1`, `c2`, ..., `c100`: Comentari

### Columna final
- `comentari general`: Comentari global de l'estudiant

### Classificació automàtica
El sistema classifica automàticament les matèries:
- **Matèries actuals (4t)**: Es compten a les estadístiques globals
- **Matèries pendents (1r, 2n, 3r)**: Es mostren separadament a la vista alumne, NO es compten a l'estadística global

## Estructura del Projecte

```
├── app.py         # Aplicació principal
├── requirements.txt       # Dependències del projecte
├── sections/            # Seccions principals de l'aplicació
│   ├── evolution.py     # Visualitzacions d'evolució de notes
│   ├── student_marks.py # Visualització de notes per alumne
│   ├── student_selector.py # Selector d'alumnes
│   └── visualization.py # Visualitzacions generals i estadístiques
├── utils/               # Funcions i ajudants d'utilitat
│   ├── acta_csv_loader.py # Càrrega i processament d'actes CSV (ESO)
│   ├── data_normalizer.py # Normalització de dades CSV
│   ├── constants.py     # Constants i configuracions
│   ├── data_loader.py   # Càrrega de dades
│   ├── generate_dummy_data.py # Generació de dades de prova
│   └── helpers.py       # Funcions auxiliars
└── docs/               # Documentació i fitxers de dades (no traçat en el repositori)
```

## Instal·lació

1. Clona el repositori:
```bash
git clone git@github.com:ElPuig/metrika.git
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

3. Selecciona el mode de treball:
   - Carrega fitxers CSV d'actes ESO
   - Tria el trimestre actiu
   - Navega per les pestanyes: Grup, Materia, Alumne, Comparador i Exportació

## Guia d'usuari (MkDocs)

La guia d'usuari de Metrika esta integrada amb MkDocs i el codi font viu a `docs_site/`.

### Execucio local de la guia

```bash
mkdocs serve
```

La guia quedara disponible a `http://127.0.0.1:8000`.

### Build de validacio

```bash
mkdocs build --strict
```

### Publicacio

La publicacio es fa automaticament amb GitHub Actions cap a GitHub Pages quan hi ha canvis a la branca `dev`.

## Característiques Principals

### Visualització d'Estadístiques (CSV d'actes)
- **Càrrega flexible**: Suporta fitxers CSV d'actes ESO
- **Classificació automàtica**:
  - Matèries de 4t: Comptabilitzades a l'estadística global
  - Matèries pendents (1r, 2n, 3r): Mostrades separadament, NO comptabilitzades
- **5 vistes principals**:
  1. **Vista Grup**: Estadístiques globals, distribució de qualificacions, resum de suspensos, gràfic de barres per assignatura, mapa de calor, rànquing d'alumnes
  2. **Vista Materia**: Estadístiques específiques, distribució, llista d'alumnes amb notes i comentaris
  3. **Vista Alumne**: 
     - Notes de 4t (Curs Actual)
     - ⚠️ Matèries Pendents (de cursos anteriors)
     - Comentari General
     - Taxa d'èxit i mitjana
  4. **Vista Evolució**: Comparació entre avaluacions, gràfics d'evolució
  5. **Vista Exportació**:
     - Exporta el trimestre seleccionat a CSV
     - Una fila per alumne
     - Dues columnes per matèria: qualificació i comentari
     - Matèries ordenades per nombre d'alumnes (de més a menys), deixant normalment les optatives al final

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

## Sistema de Comentaris

El sistema de comentaris està integrat a totes les vistes principals i desa la informació a `comments_data.json` per mantenir-la entre sessions.

**Funcionalitat clau**
- Tipus de comentari: alumnes, matèries, grups i sessions (trimestre+grup)
- Persistència automàtica i recuperació en iniciar l'aplicació
- Gestió des de la barra lateral: estadístiques, exportació/importació, esborrar-ho tot
- Suport d'importació/exportació amb fitxers de comentaris amb marca de temps

**On apareixen**
- Vista Alumne: comentaris generals després de les taules de notes
- Vista Materia: comentaris específics després de les estadístiques
- Vista Grup: comentaris globals sobre el grup
- Vista Evolució: comentaris per combinacions trimestre/grup

**Com utilitzar-los**
1. Escriu el comentari al text area corresponent i prem "Desar"; queda guardat al moment.
2. Per importar/exportar o netejar-los, obre la secció "Gestió de Comentaris" a la barra lateral.
3. Els comentaris importats es fusionen amb els existents; l'esborrat elimina totes les entrades.

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
