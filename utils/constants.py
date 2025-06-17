from enum import Enum
import pandas as pd

# Constants classes
class MathConstants(Enum):
    PI = 3.14159

class MarkConfig(Enum):
    NA = "No assoliment"
    AS = "Assoliment satisfactori"
    AN = "Assoliment notable"
    AE = "Assoliment excel·lent"
    LIST = (NA, AS, AN, AE)
    """List of marks (tuple)"""
    
    HEIGHT_MAP = {'NA': 1, 'AS': 2, 'AN': 3, 'AE': 4, pd.NA: 0, '': 0} 
    """Assign height/weight to each mark"""
    
    
    COLOR_MAP = {
        "No assoliment": "#d62728",  # Red
        "Assoliment satisfactori": "#ff7f0e",  # Orange
        "Assoliment notable": "#1f77b4",  # Blue
        "Assoliment excel·lent": "#2ca02c",  # Green
        "": "gray",
        pd.NA: "gray"
    }
    """Define custom colors for each unique mark value"""

    
    @classmethod
    def get_height_from_key(cls, key):
        """Get the height from a key in HEIGHT_MAP dictionary.
        
        Args:
            key (str): The key to search for in HEIGHT_MAP
            
        Returns:
            int: The corresponding height if found, 0 otherwise
        """
        return cls.HEIGHT_MAP.get(key, 0)
    
    @classmethod
    def get_mark_from_height(cls, height):
        """Get the mark from a height in HEIGHT_MAP dictionary.
        
        Args:
            height (int): The height to search for in HEIGHT_MAP
            
        Returns:
            str: The corresponding mark if found, "" otherwise
        """
        # Invert the dictionary to get mark from height
        height_to_mark = {v: k for k, v in cls.HEIGHT_MAP.value.items()}
        return height_to_mark.get(height, "")


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

    @classmethod
    def get_key_from_value(cls, value):
        """Get the key from a value in COL_NAMES dictionary.
        
        Args:
            value (str): The value to search for in COL_NAMES
            
        Returns:
            str: The corresponding key if found, None otherwise
        """
        for key, val in cls.COL_NAMES.value.items():
            if val == value:
                return key
        return None


class AppConfig:
    """Application configuration and versioning"""
    
    # Application title and theme
    APP_TITLE = "Visualizador Esfera"
    THEME_COLOR = "#FF4B4B"
    MAX_SIZE = 100
    MIN_SIZE = 10

    # Application version (Semantic Versioning: MAJOR.MINOR.PATCH)
    VERSION = "1.0.0"
    
    # Application name
    APP_NAME = "Metrika"
    
    # Version description
    VERSION_DESCRIPTION = "Primera versió estable amb suport per a estructura JSON millorada"
    
    # Minimum compatible version (for backward compatibility)
    MIN_COMPATIBLE_VERSION = "1.0.0"


class TestConfig(Enum):
    TEST_CSV_FILE1_PATH="docs/dummy1.csv" # T1
    TEST_CSV_FILE2_PATH="docs/dummy2.csv" # T2
    TEST_JSON_FILE1_PATH="docs/dummy1.json" # T1
    TEST_JSON_FILE2_PATH="docs/dummy2.json" # T2

