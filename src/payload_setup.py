# payload_setup.py
# Dans ce fichier nous definissons toutes les fonctions et imports nécessaires 
from sklearn.preprocessing import LabelEncoder
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

# Fonction pour l'encodage des colonnes catégorielles
def label_encode_columns(df):
    df_encoded = df.copy()
    for col in df_encoded.columns:
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
    return df_encoded



# Classe Pydantic pour valider les données d'entrée de l'API
class PredictPayload(BaseModel):
    PrimaryPropertyType: str = Field(..., description="Type de propriété principal")
    YearBuilt: int = Field(..., ge=1800, le=datetime.now().year, description="Année de construction")
    NumberofBuildings: int = Field(..., ge=0, description="Nombre de bâtiments sur le site")
    NumberofFloors: int = Field(..., ge=0, description="Nombre d'étages")
    LargestPropertyUseType: str = Field(..., description="Type d'usage principal")
    LargestPropertyUseTypeGFA: float = Field(..., ge=0, description="Surface utile du type d’usage majeur (en sqft ou m² selon tes données)")

    @field_validator('PrimaryPropertyType', 'LargestPropertyUseType')
    def non_empty_str(cls, v):
        if not str(v).strip():
            raise ValueError("La valeur ne doit pas être vide.")
        return v
