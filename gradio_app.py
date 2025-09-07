import gradio as gr
import requests
import os
from datetime import datetime

# URL de l'API FastAPI (modifiable via variable d'environnement)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def predict_co2(primary_property_type, year_built, number_of_buildings, 
                number_of_floors, largest_property_use_type, largest_property_use_type_gfa):
    """
    Envoie les données à l'API et retourne la prédiction formatée.
    """
    payload = {
        "PrimaryPropertyType": primary_property_type,
        "YearBuilt": int(year_built),
        "NumberofBuildings": int(number_of_buildings),
        "NumberofFloors": int(number_of_floors),
        "LargestPropertyUseType": largest_property_use_type,
        "LargestPropertyUseTypeGFA": float(largest_property_use_type_gfa)
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/predict", json=payload)
        if response.status_code == 200:
            result = response.json()
            return (
                f"**Prédiction CO₂ : {result['prediction']:.2f} {result['unit']}**\n\n"
                f"**Modèle :** {result['model_info']['model_type']}\n"
                f"- RMSE : {result['model_info']['RMSE']:.4f}\n"
                f"- MAE : {result['model_info']['MAE']:.4f}\n"
                f"- R² : {result['model_info']['performance_R2']:.4f}\n"
                f"- WAPE : {result['model_info']['WAPE']:.4f}\n\n"
                f"{result['description']}"
            )
        else:
            return f"Erreur API : {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return "Impossible de se connecter à l'API. Vérifie que FastAPI est lancé."
    except Exception as e:
        return f"Erreur : {str(e)}"


# Options pour les menus déroulants
property_types = [
    "Other", "Small- and Mid-Sized Office", "Large Office",
    "Warehouse", "Retail Store", "Mixed Use Property", "Hotel"
]
use_types = [
    "Office", "Other", "Non-Refrigerated Warehouse",
    "Retail Store", "Hotel", "Worship Facility", "Medical Office",
    "Supermarket/Grocery Store", "Distribution Center", "K-12 School",
    "Other - Recreation", "Senior Care Community", "Other - Entertainment/Public Assembly",
    "College/University", "Parking", "Self-Storage Facility"
]

# Interface Gradio
with gr.Blocks(title="Prédiction CO₂ des Bâtiments") as demo:
    gr.Markdown("## Prédicteur d'Émissions de CO₂ des Bâtiments non Résidentiels de Seattle")
    
    with gr.Row():
        primary_type = gr.Dropdown(choices=property_types, label="Type de Propriété Principal", value="Small- and Mid-Sized Office")
        year_built = gr.Number(label="Année de Construction", value=2000, minimum=1800, maximum=datetime.now().year)
        num_buildings = gr.Number(label="Nombre de Bâtiments", value=1, minimum=1)
    
    with gr.Row():
        num_floors = gr.Number(label="Nombre d'Étages", value=5, minimum=1)
        largest_use_type = gr.Dropdown(choices=use_types, label="Plus Grand Type d'Usage", value="Office")
        gfa = gr.Number(label="Surface du Plus Grand Usage (ft²)", value=10000, minimum=10)
    
    predict_btn = gr.Button("Prédire les Émissions de CO₂")
    prediction_result = gr.Markdown()
    
    predict_btn.click(
        predict_co2,
        inputs=[primary_type, year_built, num_buildings, num_floors, largest_use_type, gfa],
        outputs=prediction_result
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))  # Hugging Face = 7860 par défaut, Render fournit PORT
    demo.launch(server_name="0.0.0.0", server_port=port, share=False, debug=True)
