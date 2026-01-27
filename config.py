import os

class Config:
    MONGODB_SETTINGS = {
        'host': os.getenv("MONGO_URI", "mongodb://localhost:27017/portfolio")
    }
    FLASK_ADMIN_SWATCH = 'slate'
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
