#!/usr/bin/env python3
import os
import subprocess
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Run the Streamlit application"""
    print("Starting Card Admin Panel...")
    
    # Check if Streamlit is installed
    try:
        import streamlit
        print(f"Streamlit version: {streamlit.__version__}")
    except ImportError:
        print("Error: Streamlit is not installed. Please run 'pip install -r requirements.txt'")
        sys.exit(1)
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("Warning: .env file not found. Creating from template...")
        if os.path.exists(".env.example"):
            with open(".env.example", "r") as example, open(".env", "w") as env:
                env.write(example.read())
            print("Created .env file from template. Please edit it with your Supabase credentials.")
        else:
            print("Error: .env.example file not found. Please create a .env file manually.")
            sys.exit(1)
    
    # Get Streamlit port from .env or use default
    port = os.getenv("STREAMLIT_SERVER_PORT", "8501")
    
    # Run Streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", port]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nStopping Card Admin Panel...")
    except Exception as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 