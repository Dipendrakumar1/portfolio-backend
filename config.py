import os
from dotenv import load_dotenv

# Load variables from a local .env file (development only).
# In production (Render), environment variables are set in the dashboard.
load_dotenv()

# =============================================================================
# ENVIRONMENT VARIABLES - Set these in your .env file or deployment platform
# =============================================================================
# See .env.example for a template

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")  # MongoDB connection string

# Flask Security
SECRET_KEY = os.getenv("SECRET_KEY")  # Secret key for session encryption

# CORS Configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")  # Frontend origin

# Environment
FLASK_ENV = os.getenv("FLASK_ENV", "production")  # Set to "development" for debug mode

class Config:
    MONGODB_SETTINGS = {
        'host': MONGO_URI
    }
    FLASK_ADMIN_SWATCH = 'slate'
    SECRET_KEY = SECRET_KEY
    
    @staticmethod
    def validate():
        """Validate required environment variables are set."""
        if not MONGO_URI:
            raise ValueError("MONGO_URI environment variable must be set")
        if not SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable must be set")
