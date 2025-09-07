# db_utils.py
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from create_db import engine, Input, Prediction

# Création d'une factory de sessions
SessionLocal = sessionmaker(bind=engine)

def save_input(data: dict) -> int:
    """
    Enregistre les données envoyées au modèle dans la table 'inputs'.
    Retourne l'ID de l'entrée.
    """
    with SessionLocal() as session:
        try:
            # Assure que created_at est timezone-aware UTC
            if "created_at" not in data:
                data["created_at"] = datetime.now(timezone.utc)
            new_input = Input(**data)
            session.add(new_input)
            session.commit()
            session.refresh(new_input)  # récupère l'id généré
            return new_input.id
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(f"Erreur lors de l'insertion input : {e}")

def save_prediction(input_id: int, co2_value: float):
    """
    Enregistre la prédiction du modèle dans la table 'predictions'.
    """
    with SessionLocal() as session:
        try:
            prediction = Prediction(
                input_id=input_id,
                predicted_co2=co2_value,
                created_at=datetime.now(timezone.utc)
            )
            session.add(prediction)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(f"Erreur lors de l'insertion prediction : {e}")

def get_predictions_json() -> list:
    """
    Récupère toutes les prédictions et renvoie une liste de dictionnaires (format JSON-friendly).
    """
    with SessionLocal() as session:
        preds = session.query(Prediction).all()
        return [
            {
                "id": p.id,
                "input_id": p.input_id,
                "predicted_co2": p.predicted_co2,
                "created_at": p.created_at.isoformat()
            }
            for p in preds
        ]

def get_inputs_json() -> list:
    """
    Récupère tous les inputs et renvoie une liste de dictionnaires.
    """
    with SessionLocal() as session:
        inputs = session.query(Input).all()
        return [
            {
                "id": i.id,
                "PrimaryPropertyType": i.PrimaryPropertyType,
                "YearBuilt": i.YearBuilt,
                "NumberofBuildings": i.NumberofBuildings,
                "NumberofFloors": i.NumberofFloors,
                "LargestPropertyUseType": i.LargestPropertyUseType,
                "LargestPropertyUseTypeGFA": i.LargestPropertyUseTypeGFA,
                "created_at": i.created_at.isoformat()
            }
            for i in inputs
        ]
