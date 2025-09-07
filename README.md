# CO₂ Prediction API & Gradio UI

Ce projet fournit une **API FastAPI** et une **interface utilisateur Gradio** pour prédire les émissions de CO₂ des bâtiments non résidentiels à Seattle, à partir de leurs caractéristiques.
Les prédictions sont sauvegardées dans une base **PostgreSQL** via SQLAlchemy.

---

## Structure du projet

```
.
├── app/
│   └── API.py                # API FastAPI principale
├── infra/
│   ├── create_db.py          # Création des tables PostgreSQL
│   └── db_utils.py           # Fonctions utilitaires DB
├── models/
│   ├── model_emissions_co2.joblib   # Modèle ML entraîné
│   └── model_metadata.joblib        # Métadonnées du modèle
├── src/
│   ├── model.py              # Chargement du modèle & prédictions
│   ├── payload_setup.py      # Validation Pydantic & prétraitement
│   └── favicon.ico
├── gradio_app.py             # Interface utilisateur Gradio
├── requirements.txt          # Dépendances
├── render.yaml               # Déploiement Render (API + UI + DB)
└── .gitignore
```

---

## Fonctionnalités

- **API FastAPI** avec endpoints :

  - `GET /health` → vérifie l’état de l’API et du modèle
  - `POST /predict` → génère une prédiction CO₂
  - `GET /predictions` → retourne l’historique (inputs + résultats)
  - `GET /model_info` → infos sur le modèle (type, métriques, description)

- **Base PostgreSQL** pour stocker inputs et prédictions.

- **Interface Gradio** : formulaire simple pour saisir les caractéristiques et obtenir la prédiction en direct.

---

## Installation locale

### 1. Cloner le repo

```bash
git clone https://github.com/LyAbdourahmane/Render-deployment-api-CO2.git
cd Render-deployment-api-CO2
```

### 2. Créer un environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
```

### 3. Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Variables d’environnement

Créer un fichier `.env` à la racine :

```
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/ma_db
API_BASE_URL=http://localhost:8000
```

### 5. Initialiser la base

```bash
python infra/create_db.py
```

### 6. Lancer l’API

```bash
uvicorn app.API:app --reload
```

API dispo sur [http://localhost:8000](http://localhost:8000)

### 7. Lancer l’UI Gradio

Dans un autre terminal :

```bash
python gradio_app.py
```

UI dispo sur [http://localhost:7860](http://localhost:7860)

---

## Déploiement sur Render

Le projet est prêt avec **Blueprint Render** (`render.yaml`).

1. Pousser sur GitHub/GitLab avec `models/` inclus :

   ```bash
   git add -A
   git commit -m "Deploy on Render"
   git push origin main
   ```

2. Sur [Render](https://render.com) → **New → Blueprint**.

3. Choisir le repo, branche `main`.

4. Render crée automatiquement :

   - `co2-db` → base PostgreSQL
   - `co2-api` → API FastAPI (avec health check `/health`)
   - `co2-ui` → Interface Gradio reliée à l’API

5. URLs après déploiement :

   - API : `https://co2-api.onrender.com`
   - UI : `https://co2-ui.onrender.com`

---

## Exemple d’appel API

### Vérification santé

```bash
curl https://co2-api.onrender.com/health
```

### Prédiction

```bash
curl -X POST https://co2-api.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "PrimaryPropertyType": "Small- and Mid-Sized Office",
    "YearBuilt": 2000,
    "NumberofBuildings": 1,
    "NumberofFloors": 5,
    "LargestPropertyUseType": "Office",
    "LargestPropertyUseTypeGFA": 10000
  }'
```

---

## À savoir

- Les **modèles ML (`.joblib`)** sont versionnés dans `models/` et déployés avec le code.
- La **DB Render** est automatiquement liée grâce à `DATABASE_URL` injecté par `render.yaml`.
- L’UI consomme l’API via `API_BASE_URL` injecté automatiquement par `render.yaml`.

---
