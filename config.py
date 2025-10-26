import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TMDB_API_KEY = os.getenv('TMDB_API_KEY', 'your_api_key_here')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-123')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')