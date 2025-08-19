import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "tcc_secret_2024")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///tcc.db"
    ).replace("postgres://", "postgresql://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Para CORS o futuras integraciones
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
