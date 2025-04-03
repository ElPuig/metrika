from enum import Enum
import pandas as pd

# Constants classes
class MathConstants(Enum):
    PI = 3.14159

class MarkConfig(Enum):
    NA = "NA"
    AS = "AS"
    AN = "AN"
    AE = "AE"
    LIST = (NA, AS, AN, AE)
    """List of marks (tuple)"""
    
    HEIGHT_MAP = {'NA': 1, 'AS': 2, 'AN': 3, 'AE': 4, pd.NA: 0, '': 0} 
    """Assign height/weight to each mark"""
    
    
    COLOR_MAP = {
        "NA": "#d62728",  # Red
        "AS": "#ff7f0e",  # Orange
        "AN": "#1f77b4",  # Blue
        "AE": "#2ca02c",  # Green
        "": "gray",
        pd.NA: "gray"
    }
    """Define custom colors for each unique mark value"""


class DataConfig(Enum):
    """This class contains constant values ralted to PDF data extracted from Esfera."""

    SUBJ_NAMES = ("CAT", "CAST", "ANG", "MAT", "BG", "FQ", "TD", "CS", "MUS", "EDF", "OPT", "PG_I", "PG_II", "COMP_DIG", "COMP_PERS", "COMP_CIUT", "COMP_EMPR")
    """Subject short names"""

    COL_NAMES={
        "Identificador de l'alumne/a": "id",
        "Nom i cognoms de l'alumne/a": "NOM",
        "Ll. Cat.": "CAT",
        "Ll. Cast.": "CAST",
        "Ll. Estr.": "ANG",
        "Mat.": "MAT",
        "BG": "BG",
        "FQ": "FQ",
        "TD": "TD",
        "CS:GH": "CS",
        "Mús.": "MUS",
        "Ed. Fís.": "EDF",
        "Optativa": "OPT",
        "PG_I": "PG_I",
        "PG_II": "PG_II",
        "Comp. Dig.": "COMP_DIG",
        "Comp. Pers.": "COMP_PERS",
        "Comp. Ciut.": "COMP_CIUT",
        "Comp. Empr.": "COMP_EMPR"
    }
    """Dictionary to relate actual column name with short name."""


class AppConfig(Enum):
    APP_TITLE = "Visualizador Esfera"
    THEME_COLOR = "#FF4B4B"
    MAX_SIZE = 100
    MIN_SIZE = 10


class TestConfig(Enum):
    TEST_CSV_FILE_PATH="docs/ActaAvaluacioGraella_ESO LOE (Modificada)_3_ESO 3B_T1.csv"

