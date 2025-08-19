import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "tcc_secret_2024")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///tcc.db").replace("postgres://", "postgresql://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt_supersecret_2024")
    SWAGGER_UI_DOC_EXPANSION = "list"
    RESTX_VALIDATE = True
    RESTX_MASK_SWAGGER = False
    ERROR_404_HELP = False
