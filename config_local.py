import os
from datetime import timedelta

class Config:
    # Basic Flask configuration
    SECRET_KEY = 'zRZ3r1EwP5uhHYKXlTwNZbu9UikLkjR4ahH15fG8VZw'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///linkedin_scheduler.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # LinkedIn OAuth configuration
    LINKEDIN_CLIENT_ID = '86sf2mwklf3bar'
    LINKEDIN_CLIENT_SECRET = 'WPL_AP1.9r9ObArF82SufuIY.RAvHkg=='
    LINKEDIN_REDIRECT_URI = 'http://localhost:5000/auth/linkedin/callback'
    
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
