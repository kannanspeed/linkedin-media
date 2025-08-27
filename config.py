import os
from datetime import timedelta

class Config:
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///linkedin_scheduler.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # LinkedIn OAuth configuration
    LINKEDIN_CLIENT_ID = os.environ.get('LINKEDIN_CLIENT_ID') or 'your-linkedin-client-id'
    LINKEDIN_CLIENT_SECRET = os.environ.get('LINKEDIN_CLIENT_SECRET') or 'your-linkedin-client-secret'
    LINKEDIN_REDIRECT_URI = os.environ.get('LINKEDIN_REDIRECT_URI') or 'http://localhost:5000/auth/linkedin/callback'
    
    # File upload configuration
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # LinkedIn API URLs
    LINKEDIN_AUTH_URL = 'https://www.linkedin.com/oauth/v2/authorization'
    LINKEDIN_TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
    LINKEDIN_API_BASE_URL = 'https://api.linkedin.com/v2'
    
    # Required LinkedIn scopes
    LINKEDIN_SCOPES = ['r_liteprofile', 'w_member_social']
