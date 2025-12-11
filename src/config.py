"""
Configuration file for YouTube Success Predictor
"""
import os
from dotenv import load_dotenv

load_dotenv()

# YouTube API Configuration
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# Target Channels (Technology category - 10 popular channels)
TARGET_CHANNELS = [
    'UC8butISFwT-Wl7EV0hUK0BQ',  # freeCodeCamp.org
    'UCWv7vMbMWH4-V0ZXdmDpPBA',  # Programming with Mosh
    'UCW5YeuERMmlnqo4oq8vwDeg',  # The Net Ninja
    'UCsBjURrPoezykLs9EqgamOA',  # Fireship
    'UC29ju8bIPu5jQf3bi3d67Zw',  # Traversy Media
    'UC8A0M0eDttdB11MHxX58vXQ',  # Corey Schafer
    'UCu1xbgCV5o48h_BYCQD7K1g',  # Sentdex
    'UCJ0-OtVpF0wOKEqT2Z1HEtA',  # Derek Banas
    'UC8butISFwT-Wl7EV0hUK0BQ',  # TechWorld with Nana
    'UCsBjURrPoezykLs9EqgamOA'   # Web Dev Simplified
]

# Data Collection Settings
MAX_VIDEOS_PER_CHANNEL = 50
MAX_RESULTS_PER_REQUEST = 50

# Model Configuration
MODEL_DIR = 'models'
BEST_MODEL_NAME = 'best_model.pkl'
SCALER_NAME = 'scaler.pkl'
FEATURE_NAMES_NAME = 'feature_names.pkl'
MODEL_METADATA_NAME = 'model_metadata.pkl'

# Flask Configuration
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'


