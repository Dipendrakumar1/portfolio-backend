import os

class Config:
    MONGODB_SETTINGS = {
        'host': os.getenv("MONGO_URI", "")
    }
    FLASK_ADMIN_SWATCH = 'slate'
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
