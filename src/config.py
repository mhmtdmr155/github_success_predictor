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

# Target Channels (Technology category - International + Turkish channels)
TARGET_CHANNELS = [
    # International Technology Channels
    'UC8butISFwT-Wl7EV0hUK0BQ',  # freeCodeCamp.org
    'UCWv7vMbMWH4-V0ZXdmDpPBA',  # Programming with Mosh
    'UCW5YeuERMmlnqo4oq8vwDeg',  # The Net Ninja
    'UCsBjURrPoezykLs9EqgamOA',  # Fireship
    'UC29ju8bIPu5jQf3bi3d67Zw',  # Traversy Media
    'UC8A0M0eDttdB11MHxX58vXQ',  # Corey Schafer
    'UCu1xbgCV5o48h_BYCQD7K1g',  # Sentdex
    'UCJ0-OtVpF0wOKEqT2Z1HEtA',  # Derek Banas
    
    # Turkish Technology Channels (Popüler ve Teknoloji Odaklı)
    'UC-gs6ml23jQKvLC86LzpQ0g',  # Technopat
    'UCzNu79N8Lq1wUY52MkhWKSA',  # ShiftDelete.Net
    'UC26buublzO30XpR-KP2TfAw',  # webtekno
    'UCZNZj3mkdCGJfCoKyl4bSYQ',  # Yazılım Bilimi
    'UCq80ExEGpj3PQ9MCLMvpjtg',  # Sadık turan Şeylan
    'UCkkgrhDCJheXQNIFqUVw0_g',  # BilgisayarKavramlari
    'UCGNqBxR79QuNLja4VbSUR7w',  # Türk Teknoloji
    'UChI_JJN9aD-YKegn4q7EHHQ',  # Sanayi ve Teknoloji Bakanlığı
    'UCQ68rDQmMehUYntW4IU_ebQ',  # Turk Programlama
    'UCewVCW38rsfKdl0VwR7sxpA',  # Türkiye Yazılım
    'UCMPCc9hZ-YBZkEon9tzESVA',  # Tolga Özuygur
    'UCleeGHYm74udRpj3-krDfdA',  # iPhonedo Türkiye
    'UC8coOsD1DGLgDazU20oAw4Q',  # TurkDevs
    'UC5QF2dQylucdASZpTnFLe9g',  # Radikal Yazılım
    'UCX2uz7k2Z23aHCx209EY4vw',  # Go Türkiye
    'UC_d_W1uBdIKo-zcAZVBpE7w',  # Yazılım Türkiye
    'UCQKEJxT5iiHCWQqT68gOCOg',  # Kodlama Vakti
    'UCPEDp-NSaNKZGFcF0Ob8ySA',  # Python Turkiye
    'UCx8L3gTsZ6Qux28-xOtj_0g',  # Python Türkiye
    'UCSnIf-v95OSGIv9H7d2R2lw',  # Kodluyoruz
    'UC1VAnqF9VLHNXngLwpov4kA',  # PROTOTURK
    'UCZ6YpiVVgRS2-ToBrOt2hcA',  # Google Türkiye
    'UC9DkLqZvawpkU68oH9L3EZA',  # Teknoblog
    'UCOvHevuChCbqevJpGKvPYdQ',  # NewTechTurkey
    'UCPUhqqTRIHbDYeGF1V5vHBw',  # Teknoloji Dünyası
]

# Data Collection Settings
MAX_VIDEOS_PER_CHANNEL = 200  # Her kanaldan 200 video topla (maksimum veri için)
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


