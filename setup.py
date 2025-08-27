#!/usr/bin/env python3
"""
LinkedIn Scheduler - Setup Script

This script helps set up the LinkedIn Scheduler application by:
1. Checking Python version
2. Creating virtual environment
3. Installing dependencies
4. Setting up environment variables
5. Initializing database
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        if platform.system() == "Windows":
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command.split(), check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def create_env_file():
    """Create .env file from template"""
    env_example = """# LinkedIn OAuth Credentials
# Get these from https://www.linkedin.com/developers/
LINKEDIN_CLIENT_ID=your_linkedin_client_id_here
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret_here
LINKEDIN_REDIRECT_URI=http://localhost:5000/auth/linkedin/callback

# Flask Secret Key (generate a secure random string)
SECRET_KEY=your_super_secret_key_here

# Database URL (optional - defaults to SQLite)
DATABASE_URL=sqlite:///linkedin_scheduler.db"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_example)
        print("✅ Created .env file")
        print("📝 Please edit .env file with your LinkedIn app credentials")
        return True
    else:
        print("ℹ️  .env file already exists")
        return True

def main():
    """Main setup function"""
    print("🚀 LinkedIn Scheduler Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("\n💡 It's recommended to use a virtual environment")
        print("Run these commands first:")
        print("  python -m venv venv")
        if platform.system() == "Windows":
            print("  venv\\Scripts\\activate")
        else:
            print("  source venv/bin/activate")
        print("  python setup.py")
        
        response = input("\nContinue anyway? (y/N): ").lower()
        if response != 'y':
            print("Setup cancelled.")
            sys.exit(0)
    else:
        print("✅ Virtual environment detected")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Create necessary directories
    directories = ['static/uploads', 'static/css', 'static/js', 'templates']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your LinkedIn app credentials")
    print("2. Create a LinkedIn app at https://www.linkedin.com/developers/")
    print("3. Set redirect URI to: http://localhost:5000/auth/linkedin/callback")
    print("4. Run the application: python run.py")
    print("\n📚 See README.md for detailed instructions")

if __name__ == '__main__':
    main()
