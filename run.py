#!/usr/bin/env python3
"""
LinkedIn Scheduler - Application Runner

This script initializes and runs the LinkedIn Scheduler application.
It handles database initialization and starts the Flask development server.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import init_db

def main():
    """Initialize and run the application"""
    
    print("🚀 Starting LinkedIn Scheduler...")
    print("=" * 50)
    
    # Check for required environment variables
    required_env_vars = [
        'LINKEDIN_CLIENT_ID',
        'LINKEDIN_CLIENT_SECRET',
        'SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        print("See README.md for setup instructions.")
        sys.exit(1)
    
    # Initialize database
    try:
        print("🗄️  Initializing database...")
        init_db(app)
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)
    
    # Print configuration info
    print("\n📋 Configuration:")
    print(f"   - Client ID: {os.getenv('LINKEDIN_CLIENT_ID')[:10]}...")
    print(f"   - Redirect URI: {os.getenv('LINKEDIN_REDIRECT_URI', 'http://localhost:5000/auth/linkedin/callback')}")
    print(f"   - Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    print("\n🌐 Starting server...")
    print("   - Local: http://localhost:5000")
    print("   - Network: http://0.0.0.0:5000")
    print("\n💡 Tips:")
    print("   - Make sure your LinkedIn app redirect URI matches the one above")
    print("   - Press Ctrl+C to stop the server")
    print("   - Check the README.md for detailed setup instructions")
    print("=" * 50)
    
    # Start the Flask application
    try:
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
