import gradio as gr
import requests
import os, sys
from datetime import datetime

# ---------- Config via variables d'environnement que j'ai sur render ----------
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
print(f"[Gradio] API_BASE_URL = {API_BASE_URL}", file=sys.stderr)

AUTHOR_NAME = os.getenv("AUTHOR_NAME", "Votre Nom")
AUTHOR_EMAIL = os.getenv("AUTHOR_EMAIL", "vous@example.com")
AUTHOR_LINKEDIN = os.getenv("AUTHOR_LINKEDIN", "https://www.linkedin.com/in/votre-profil/")
AUTHOR_GITHUB = os.getenv("AUTHOR_GITHUB", "https://github.com/votreuser/votre-repo")
AUTHOR_SITE = os.getenv("AUTHOR_SITE", "https://votre-site.com")

# ---------- Fonctions API ----------
def predict_co2(primary_property_type, year_built, number_of_buildings, 
                number_of_floors, largest_property_use_type, largest_property_use_type_gfa):
    payload = {
        "PrimaryPropertyType": primary_property_type,
        "YearBuilt": int(year_built),
        "NumberofBuildings": int(number_of_buildings),
        "NumberofFloors": int(number_of_floors),
        "LargestPropertyUseType": largest_property_use_type,
        "LargestPropertyUseTypeGFA": float(largest_property_use_type_gfa)
    }
    try:
        response = requests.post(f"{API_BASE_URL}/predict", json=payload, timeout=20)
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
        return "Impossible de se connecter à l'API. Vérifie que FastAPI est lancé et l'URL API_BASE_URL."
    except Exception as e:
        return f"Erreur : {str(e)}"

def fetch_model_info():
    try:
        r = requests.get(f"{API_BASE_URL}/model_info", timeout=15)
        r.raise_for_status()
        m = r.json()
        perf = m.get("performance", {})
        return (
            f"**Modèle :** {m.get('model_type','-')}\n"
            f"- RMSE : {perf.get('rmse','-')}\n"
            f"- MAE : {perf.get('mae','-')}\n"
            f"- WAPE : {perf.get('wape','-')}\n"
            f"- R² : {perf.get('r2_score','-')}\n\n"
            f"{m.get('description','')}"
        )
    except Exception as e:
        return f"Impossible de récupérer les infos modèle : {e}"

# ---------- Options UI ----------
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

# ---------- Interface Gradio ----------
with gr.Blocks(title="Prédiction CO₂ des Bâtiments") as demo:
    gr.Markdown("## Prédicteur d'Émissions de CO₂ des Bâtiments non Résidentiels de Seattle")

    # Bandeau de présentation + CTA contact
    with gr.Row():
        gr.Markdown(
            f"""
### CO₂ Predictor — Démo en ligne  
Projet ML : prédiction des émissions CO₂ (bâtiments non résidentiels Seattle)  
**Par {AUTHOR_NAME}** • [{AUTHOR_EMAIL}](mailto:{AUTHOR_EMAIL}?subject=Candidature%20—%20CO2%20Predictor)
            """
        )
        with gr.Row():
            gr.Button("Me contacter", link=f"mailto:{AUTHOR_EMAIL}?subject=Candidature%20—%20CO2%20Predictor")
            gr.Button("LinkedIn", link=AUTHOR_LINKEDIN)
            gr.Button("Voir le code", link=AUTHOR_GITHUB)
            gr.Button("Mon site", link=AUTHOR_SITE)

    with gr.Row():
        primary_type = gr.Dropdown(choices=property_types, label="Type de Propriété Principal", value="Small- and Mid-Sized Office")
        year_built = gr.Number(label="Année de Construction", value=2000, minimum=1800, maximum=datetime.now().year)
        num_buildings = gr.Number(label="Nombre de Bâtiments", value=1, minimum=1)
    
    with gr.Row():
        num_floors = gr.Number(label="Nombre d'Étages", value=5, minimum=1)
        largest_use_type = gr.Dropdown(choices=use_types, label="Plus Grand Type d'Usage", value="Office")
        gfa = gr.Number(label="Surface du Plus Grand Usage (ft²)", value=10000, minimum=10)
    
    with gr.Row():
        predict_btn = gr.Button("Prédire les Émissions de CO₂", variant="primary")
        info_btn = gr.Button("Infos modèle")

    prediction_result = gr.Markdown()
    info_box = gr.Markdown()

    predict_btn.click(
        predict_co2,
        inputs=[primary_type, year_built, num_buildings, num_floors, largest_use_type, gfa],
        outputs=prediction_result
    )
    info_btn.click(fetch_model_info, outputs=info_box)

    # Sections propreté/fiabilité
    with gr.Accordion("À propos du projet", open=False):
        gr.Markdown(
            f"""
- **Stack** : FastAPI, Gradio, scikit-learn/XGBoost, SQLAlchemy, PostgreSQL, Render  
- **Objectif** : prédire les émissions CO₂ à partir de caractéristiques bâtiment  
- **Persistance** : enregistrement des inputs & prédictions (PostgreSQL)  
- **Auteur** : {AUTHOR_NAME} — [{AUTHOR_EMAIL}](mailto:{AUTHOR_EMAIL})  
- [GitHub]({AUTHOR_GITHUB}) • [Site Web]({AUTHOR_SITE})
            """
        )

    with gr.Accordion("Vie privée & limites", open=False):
        gr.Markdown(
            """
**Vie privée**  
- Aucune donnée personnelle collectée par l'UI.  
- Les entrées (caractéristiques bâtiment) peuvent être enregistrées en base pour la démonstration.

**Limites**  
- Modèle entraîné sur des données **Seattle** : performance moindre hors distribution.  
- Prédictions indicatives ; ne remplacent pas un audit énergétique.
            """
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port, share=False, debug=True)
