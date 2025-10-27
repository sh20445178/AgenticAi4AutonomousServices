#!/usr/bin/env python3
"""
AgenticAI4DB ML Setup Script
Installs dependencies and initializes ML models
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MLSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.models_dir = self.project_root / "trained_models"
        self.ml_requirements_path = self.project_root / "ml_requirements.txt"
        
    def check_python_version(self):
        """Check if Python version is compatible"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            logger.error(f"Python 3.8+ required, found {version.major}.{version.minor}")
            return False
        logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    
    def install_ml_dependencies(self):
        """Install ML dependencies from requirements file"""
        if not self.ml_requirements_path.exists():
            logger.error(f"❌ ML requirements file not found: {self.ml_requirements_path}")
            return False
        
        try:
            logger.info("📦 Installing ML dependencies...")
            cmd = [sys.executable, "-m", "pip", "install", "-r", str(self.ml_requirements_path)]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info("✅ ML dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install ML dependencies: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error installing dependencies: {e}")
            return False
    
    def verify_ml_imports(self):
        """Verify that ML libraries can be imported"""
        required_libs = [
            'numpy', 'pandas', 'scikit-learn', 'tensorflow', 
            'joblib', 'matplotlib', 'seaborn', 'mlflow'
        ]
        
        failed_imports = []
        for lib in required_libs:
            try:
                if lib == 'scikit-learn':
                    import sklearn
                else:
                    __import__(lib)
                logger.info(f"✅ {lib} import successful")
            except ImportError as e:
                logger.error(f"❌ Failed to import {lib}: {e}")
                failed_imports.append(lib)
        
        if failed_imports:
            logger.error(f"❌ Failed to import: {', '.join(failed_imports)}")
            return False
        
        logger.info("✅ All ML libraries imported successfully")
        return True
    
    def create_models_directory(self):
        """Create directory structure for trained models"""
        try:
            self.models_dir.mkdir(exist_ok=True)
            logger.info(f"✅ Models directory created: {self.models_dir}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create models directory: {e}")
            return False
    
    def generate_sample_data_and_train(self):
        """Generate sample data and train initial models"""
        try:
            logger.info("🧠 Generating sample data and training initial models...")
            
            # Import after dependencies are installed
            sys.path.append(str(self.project_root))
            from ml_models.training_pipeline import MLTrainingPipeline
            from ml_models.data_preprocessing import DatabasePreprocessor
            
            # Initialize components
            preprocessor = DatabasePreprocessor()
            pipeline = MLTrainingPipeline(models_dir=str(self.models_dir))
            
            # Generate synthetic training data
            logger.info("🔧 Generating synthetic training data...")
            queries, performance_data = preprocessor.generate_synthetic_data(n_samples=1000)
            
            if len(queries) == 0:
                logger.error("❌ Failed to generate training data")
                return False
            
            logger.info(f"✅ Generated {len(queries)} training samples")
            
            # Run training pipeline
            logger.info("🚀 Training ML models...")
            results = pipeline.run_full_pipeline()
            
            if results.get('success', False):
                logger.info("✅ ML models trained successfully")
                logger.info(f"📊 Training results: {results.get('summary', {})}")
                return True
            else:
                logger.error("❌ Model training failed")
                return False
                
        except ImportError as e:
            logger.error(f"❌ Failed to import ML modules: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Training failed: {e}")
            return False
    
    def test_ml_server(self):
        """Test the ML-enhanced server"""
        try:
            sys.path.append(str(self.project_root))
            from ml_enhanced_server import MLEnhancedGeminiAPI
            
            # Test initialization
            api = MLEnhancedGeminiAPI(models_dir=str(self.models_dir))
            
            if api.ml_enabled:
                logger.info("✅ ML-enhanced server initialization successful")
                logger.info(f"🧠 Loaded {len(api.ml_models)} ML models")
                
                # Test prediction
                test_query = "SELECT * FROM users WHERE age > 25"
                result = api.predict_query_performance(test_query)
                
                if result.get('success'):
                    logger.info("✅ ML prediction test successful")
                    return True
                else:
                    logger.warning("⚠️ ML prediction test failed, but server initialized")
                    return True
            else:
                logger.warning("⚠️ ML server initialized but ML features disabled")
                return True
                
        except Exception as e:
            logger.error(f"❌ ML server test failed: {e}")
            return False
    
    def create_startup_script(self):
        """Create a startup script for the ML-enhanced server"""
        startup_script = self.project_root / "start_ml_server.py"
        
        script_content = '''#!/usr/bin/env python3
"""
Startup script for ML-Enhanced AgenticAI4DB Server
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def main():
    try:
        from ml_enhanced_server import start_ml_enhanced_server
        
        print("🚀 Starting ML-Enhanced AgenticAI4DB Server...")
        print("🔧 Make sure GOOGLE_API_KEY environment variable is set")
        print()
        
        # Check for API key
        if not os.getenv('GOOGLE_API_KEY'):
            print("❌ GOOGLE_API_KEY environment variable not set")
            print("Please run: export GOOGLE_API_KEY='your-api-key'")
            return
        
        # Start server
        start_ml_enhanced_server(port=8080)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please run: python setup_ml.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
'''
        
        try:
            with open(startup_script, 'w') as f:
                f.write(script_content)
            
            # Make executable on Unix-like systems
            if os.name != 'nt':
                os.chmod(startup_script, 0o755)
            
            logger.info(f"✅ Startup script created: {startup_script}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create startup script: {e}")
            return False
    
    def run_setup(self):
        """Run the complete ML setup process"""
        logger.info("🚀 Starting AgenticAI4DB ML Setup...")
        
        steps = [
            ("Checking Python version", self.check_python_version),
            ("Installing ML dependencies", self.install_ml_dependencies),
            ("Verifying ML imports", self.verify_ml_imports),
            ("Creating models directory", self.create_models_directory),
            ("Training initial models", self.generate_sample_data_and_train),
            ("Testing ML server", self.test_ml_server),
            ("Creating startup script", self.create_startup_script)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"🔧 {step_name}...")
            if not step_func():
                logger.error(f"❌ Setup failed at: {step_name}")
                return False
        
        logger.info("🎉 ML setup completed successfully!")
        logger.info("📋 Next steps:")
        logger.info("  1. Set GOOGLE_API_KEY environment variable")
        logger.info("  2. Run: python start_ml_server.py")
        logger.info("  3. Open http://localhost:8080 in your browser")
        
        return True


def main():
    """Main setup function"""
    print("🧠 AgenticAI4DB ML Setup")
    print("=" * 50)
    
    setup = MLSetup()
    success = setup.run_setup()
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("🚀 You can now start the ML-enhanced server with:")
        print("   python start_ml_server.py")
    else:
        print("\n❌ Setup failed. Please check the logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()