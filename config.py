import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "clave_por_defecto"
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI") or "sqlite:///tcc.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
