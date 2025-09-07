# api.py
import warnings
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from infra.db_utils import save_input, save_prediction, get_predictions_json, get_inputs_json
from src.payload_setup import PredictPayload, label_encode_columns
from src.model import predict, get_model_info, load_model
warnings.filterwarnings("ignore")


app = FastAPI(
    title="API Prédiction CO₂",
    description="API pour prédire les émissions de CO₂ des bâtiments non résidentiels de Seattle.",
    version="1.0.0"
)

# CORS pour autoriser l'UI Gradio hébergée séparément à appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Optionnel: restreindre au domaine Render de l'UI
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def home():
    return {
        "message": "Bienvenue sur l'API de prédiction CO₂",
        "endpoints": ["/predictions", "/model_info", "/health"]
    }


@app.post("/predict")
async def predict_endpoint(payload: PredictPayload):
    try:
        input_data = payload.model_dump()
        prediction_value = predict(input_data)
        metadata = get_model_info()
        
        input_id = save_input(input_data)
        save_prediction(input_id, prediction_value)
        return {
            "prediction": prediction_value,
            "unit": "Metric Tons CO2e",
            "description": (
                "Total greenhouse gas emissions (CO2, CH4, N2O) from energy consumption, "
                "expressed in CO2-equivalent using 2023 utility-specific emissions factors."
            ),
            "model_info": {
                "model_type": metadata["model_type"],
                "RMSE": metadata["performance"]["rmse"],
                "MAE": metadata["performance"]["mae"],
                "WAPE": metadata["performance"]["wape"],
                "performance_R2": metadata["performance"]["r2_score"],
                "description": metadata["description"]
            },
            "input_features": input_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction : {str(e)}")


@app.get("/model_info")
async def model_info_endpoint():
    try:
        return get_model_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des infos modèle : {str(e)}")


@app.get("/health")
async def health():
      try:
          load_model()
          loaded = True
      except FileNotFoundError:
          loaded = False
      return {"status": "healthy", "model_loaded": loaded}


# j'ai ajouté cette route pour récupérer l'historique des prédictions
@app.get("/predictions")
async def get_predictions_history():
    """Récupère l'historique des prédictions"""
    try:
        predictions = get_predictions_json()
        inputs = get_inputs_json()
        
        # Associer les prédictions avec leurs données d'entrée
        history = []
        for pred in predictions:
            # Trouver l'input correspondant
            input_data = next((inp for inp in inputs if inp['id'] == pred['input_id']), None)
            
            if input_data:
                history.append({
                    "prediction_id": pred['id'],
                    "input_id": pred['input_id'],
                    "predicted_co2": pred['predicted_co2'],
                    "prediction_date": pred['created_at'],
                    "input_data": {
                        "PrimaryPropertyType": input_data['PrimaryPropertyType'],
                        "YearBuilt": input_data['YearBuilt'],
                        "NumberofBuildings": input_data['NumberofBuildings'],
                        "NumberofFloors": input_data['NumberofFloors'],
                        "LargestPropertyUseType": input_data['LargestPropertyUseType'],
                        "LargestPropertyUseTypeGFA": input_data['LargestPropertyUseTypeGFA']
                    }
                })
        
        return {
            "total_predictions": len(history),
            "predictions": history
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de l'historique : {str(e)}")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join("src", "favicon.ico"))
