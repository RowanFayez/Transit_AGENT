"""
Setup script for Alexandria Transit AI Agent
"""

import os
import subprocess
import sys

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        print("📝 Creating .env file...")
        with open('.env', 'w') as f:
            f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
            f.write("OTP_BASE_URL=http://localhost:8080\n")
            f.write("MEMORY_FILE=user_memory.json\n")
        print("✅ .env file created! Please edit it and add your Gemini API key.")
        return True
    else:
        print("✅ .env file already exists!")
        return True

def check_otp_connection():
    """Check if OTP is running"""
    print("🔍 Checking OTP connection...")
    try:
        import requests
        response = requests.get("http://localhost:8080/otp/routers/default", timeout=5)
        if response.status_code == 200:
            print("✅ OTP server is running!")
            return True
        else:
            print(f"⚠️  OTP server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  OTP server is not running: {e}")
        print("   Please start your OTP instance at http://localhost:8080")
        return False

def main():
    """Main setup function"""
    print("🚌 Alexandria Transit AI Agent Setup")
    print("=" * 40)
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Check OTP connection
    otp_running = check_otp_connection()
    
    print("\n" + "=" * 40)
    print("🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Edit .env file and add your Gemini API key")
    print("2. Start OTP server if not running")
    print("3. Run the agent:")
    print("   python agent.py")
    print("\nOr start the web interface:")
    print("   python web_interface.py")
    
    if not otp_running:
        print("\n⚠️  Note: OTP server is not running.")
        print("   The agent will work for geocoding but won't provide routes.")
    
    return True

if __name__ == "__main__":
    main()
