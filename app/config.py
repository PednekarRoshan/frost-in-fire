import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'frost-in-fire-super-secret-key-2026')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'frostinfire.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB max upload limit

    # Hyperlocal business variables
    DELIVERY_PINCODE = os.environ.get('DELIVERY_PINCODE', '400011')
    STORE_WHATSAPP_NUMBER = os.environ.get('STORE_WHATSAPP_NUMBER', '919876543210')
