#!/usr/bin/env python3
"""
Quick Start Script for Book Writing AI Chatbot

This script automatically sets up the environment and launches the application.
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'torch', 'transformers', 'flask', 'nltk', 'numpy', 'pandas'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return len(missing_packages) == 0, missing_packages

def main():
    """Main startup function."""
    print("🚀 Book Writing AI Chatbot - Quick Start")
    print("=" * 50)
    
    # Check if dependencies are installed
    deps_installed, missing = check_dependencies()
    
    if not deps_installed:
        print(f"⚠️  Missing dependencies: {', '.join(missing)}")
        print("🔧 Installing dependencies...")
        
        if not install_dependencies():
            print("❌ Failed to install dependencies. Please run:")
            print("   pip install -r requirements.txt")
            return
    
    print("✅ All dependencies are ready!")
    print("\n🎯 Choose how to start:")
    print("1. Web Interface (Recommended)")
    print("2. Command Line Interface")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            print("\n🌐 Starting web interface...")
            print("📖 Upload .txt book files to train the AI")
            print("💬 Chat with the AI for writing assistance")
            print("🔗 Access at: http://localhost:5000")
            print("\nPress Ctrl+C to stop the server")
            
            try:
                # Import and run the web app
                from app import app, init_chatbot, create_template_files
                init_chatbot()
                create_template_files()
                app.run(host='0.0.0.0', port=5000, debug=False)
            except KeyboardInterrupt:
                print("\n👋 Web server stopped. Goodbye!")
            except Exception as e:
                print(f"❌ Error starting web interface: {e}")
            break
            
        elif choice == "2":
            print("\n💻 Starting command line interface...")
            print("Type 'help' for available commands")
            print("Type 'sample' to create sample books and train")
            print("Type 'quit' to exit")
            
            try:
                # Import and run CLI
                from cli import BookWritingCLI
                cli = BookWritingCLI()
                cli.interactive_chat()
            except Exception as e:
                print(f"❌ Error starting CLI: {e}")
            break
            
        elif choice == "3":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()