#!/usr/bin/env python3
"""
Simplified ML Setup for AgenticAI4DB
Installs dependencies one by one to handle network issues
"""

import subprocess
import sys
import os
from pathlib import Path

def install_package(package):
    """Install a single package"""
    print(f"📦 Installing {package}...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                              capture_output=True, text=True, check=True)
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Failed to install {package}: {e.stderr}")
        return False

def main():
    print("🧠 Simple ML Setup for AgenticAI4DB")
    print("=" * 50)
    
    # Essential packages only
    packages = [
        "numpy>=1.21.0",
        "pandas>=1.3.0", 
        "scikit-learn>=1.0.0",
        "joblib>=1.1.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0"
    ]
    
    # Optional packages (install if possible)
    optional_packages = [
        "tensorflow>=2.10.0",  # More flexible version
        "mlflow>=2.0.0"
    ]
    
    print("Installing essential packages...")
    essential_success = 0
    for package in packages:
        if install_package(package):
            essential_success += 1
    
    print(f"\n✅ Installed {essential_success}/{len(packages)} essential packages")
    
    print("\nInstalling optional packages...")
    optional_success = 0
    for package in optional_packages:
        if install_package(package):
            optional_success += 1
    
    print(f"✅ Installed {optional_success}/{len(optional_packages)} optional packages")
    
    # Create models directory
    models_dir = Path("trained_models")
    models_dir.mkdir(exist_ok=True)
    print(f"✅ Created models directory: {models_dir}")
    
    # Create startup script
    startup_content = '''#!/usr/bin/env python3
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

def main():
    try:
        from ml_enhanced_server import start_ml_enhanced_server
        
        print("🚀 Starting ML-Enhanced AgenticAI4DB Server...")
        
        if not os.getenv('GOOGLE_API_KEY'):
            print("❌ GOOGLE_API_KEY environment variable not set")
            print("Please run: export GOOGLE_API_KEY='your-api-key'")
            return
        
        start_ml_enhanced_server(port=8080)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Some ML features may be disabled due to missing dependencies")
        # Try to start basic server
        try:
            from web_server import start_server
            print("🔄 Starting basic server without ML features...")
            start_server(port=8080)
        except Exception as e2:
            print(f"❌ Error starting server: {e2}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
'''
    
    with open("start_ml_server.py", "w") as f:
        f.write(startup_content)
    
    os.chmod("start_ml_server.py", 0o755)
    print("✅ Created startup script: start_ml_server.py")
    
    print("\n🎉 Setup completed!")
    print("📋 Next steps:")
    print("  1. Set GOOGLE_API_KEY environment variable")
    print("  2. Run: python3 start_ml_server.py")
    print("  3. Open http://localhost:8080 in your browser")
    
    if essential_success < len(packages):
        print("\n⚠️  Some essential packages failed to install.")
        print("     ML features may be limited.")
    
    if optional_success < len(optional_packages):
        print("\n💡 Optional packages like TensorFlow couldn't be installed.")
        print("     Try installing manually: pip3 install tensorflow")

if __name__ == "__main__":
    main()