import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key_here')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'floodguard')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Email Configuration
    # IMPORTANT: Replace these with your actual Gmail credentials
    # 1. Enable 2-Step Verification on your Google Account.
    # 2. Go to https://myaccount.google.com/apppasswords to generate an App Password.
    # 3. Use that App Password below as MAIL_PASSWORD.
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 465))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'floodguard.system@gmail.com') # REPLACE WITH YOUR GMAIL
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'your_app_password_here').replace(' ', '') # Strips spaces if present
