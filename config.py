import os

class Config:
    MONGODB_SETTINGS = {
        'host': os.getenv("MONGO_URI", "mongodb+srv://dipendrayadav299:dipendra1922@atlascluster.yy7vz.mongodb.net/portfolio_db?appName=AtlasCluster")
    }
    FLASK_ADMIN_SWATCH = 'slate'
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
