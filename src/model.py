# src/model.py
# Ce fichier contient les fonctions pour charger le modèle de prédiction et faire des prédictions.
import joblib
import pandas as pd
import os
from typing import Dict, Any

# Charger le modèle et les métadonnées
def load_model():
    model_path = os.path.join(os.path.dirname(__file__), "..", "models", "model_emissions_co2.joblib")
    metadata_path = os.path.join(os.path.dirname(__file__), "..", "models", "model_metadata.joblib")

    model = joblib.load(model_path)
    metadata = joblib.load(metadata_path)
    return model, metadata

# Faire une prédiction
def predict(input_data: Dict[str, Any]) -> float:
    model, metadata = load_model()
    input_df = pd.DataFrame([input_data])[metadata["feature_names"]]
    prediction = model.predict(input_df)[0]
    return float(prediction)

# Renvoyer infos sur le modèle
def get_model_info() -> Dict[str, Any]:
    _, metadata = load_model()
    return metadata
