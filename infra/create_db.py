# create_db.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

# Chargement des variables d'environnement
load_dotenv()

def _build_engine_from_env():
    """Construit un engine SQLAlchemy à partir des variables d'env.
    - Priorise DATABASE_URL (Render/Postgres managé)
    - Sinon, reconstruit depuis DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD
    """
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Uniformiser le schéma: accepter postgres:// et convertir vers postgresql+psycopg2://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return create_engine(database_url, echo=False)

    # Fallback variables séparées
    password = os.getenv("DB_PASSWORD")
    user = os.getenv("DB_USER")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME")
    if not all([user, password, dbname]):
        raise RuntimeError("Configuration DB manquante: définissez DATABASE_URL ou DB_USER/DB_PASSWORD/DB_NAME")
    return create_engine(
        f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}",
        echo=False
    )

engine = _build_engine_from_env()
Base = declarative_base()

# Notre Table inputs
class Input(Base):
    __tablename__ = "inputs"
    id = Column(Integer, primary_key=True)
    PrimaryPropertyType = Column(String, nullable=False)
    YearBuilt = Column(Integer, nullable=False)
    NumberofBuildings = Column(Integer, nullable=False)
    NumberofFloors = Column(Integer, nullable=False)
    LargestPropertyUseType = Column(String, nullable=False)
    LargestPropertyUseTypeGFA = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    predictions = relationship("Prediction", back_populates="input_data")

# Notre Table predictions
class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True)
    input_id = Column(Integer, ForeignKey("inputs.id"))
    predicted_co2 = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    input_data = relationship("Input", back_populates="predictions")


# Crée toutes les tables
Base.metadata.create_all(engine)

print("Tables créées avec succès !")
