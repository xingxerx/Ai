"""
Setup script for the custom AI model.
Helps users install dependencies and configure the system.
"""

import subprocess
import sys
import os
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    print("Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"Python version: {sys.version}")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("\nInstalling dependencies...")
    
    try:
        # Install basic requirements
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "torch", "transformers", "accelerate", "sentencepiece"
        ])
        
        print("Core dependencies installed successfully!")
        
        # Try to install additional dependencies from requirements.txt
        if Path("requirements.txt").exists():
            print("Installing from requirements.txt...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            print("All dependencies installed!")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        print("Try running: pip install torch transformers accelerate")
        return False

def check_system_resources():
    """Check system resources and provide recommendations."""
    print("\nChecking system resources...")
    
    try:
        import torch
        import psutil
        
        # Check RAM
        ram_gb = psutil.virtual_memory().total / (1024**3)
        print(f"RAM: {ram_gb:.1f} GB")
        
        if ram_gb < 4:
            print("Warning: Less than 4GB RAM detected. Consider using lightweight models.")
        elif ram_gb < 8:
            print("4-8GB RAM: Medium models recommended.")
        else:
            print("8GB+ RAM: Can run larger models.")
        
        # Check GPU
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            print(f"CUDA GPUs: {gpu_count}")
            
            for i in range(gpu_count):
                props = torch.cuda.get_device_properties(i)
                memory_gb = props.total_memory / (1024**3)
                print(f"   GPU {i}: {props.name} ({memory_gb:.1f}GB VRAM)")
                
                if memory_gb < 4:
                    print(f"   GPU {i}: Low VRAM, consider CPU inference")
                elif memory_gb < 8:
                    print(f"   GPU {i}: Medium VRAM, good for medium models")
                else:
                    print(f"   GPU {i}: High VRAM, can run large models")
        else:
            print("CUDA: Not available")
        
        # Check Apple Silicon
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print("Apple Silicon MPS: Available")
        else:
            print("Apple Silicon MPS: Not available")
        
        return True
        
    except ImportError:
        print("Cannot check system resources (torch not installed)")
        return False

def create_env_file():
    """Create environment configuration file."""
    print("\nCreating environment configuration...")
    
    env_content = """# Custom AI Model Configuration
AGI_MODEL_PROVIDER=custom
AGI_MODEL_NAME=auto
AGI_MAX_REASONING_DEPTH=10
AGI_SAFETY_LEVEL=high
AGI_LEARNING_ENABLED=true
AGI_AUTO_APPROVE_SAFE_ACTIONS=false

# Storage Configuration
AGI_KNOWLEDGE_BASE_PATH=./knowledge
AGI_TOOLS_CONFIG_PATH=./tools.yaml

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=agi_agent.log

# Model Configuration
CUSTOM_MODEL_DEVICE=auto
CUSTOM_MODEL_MAX_LENGTH=1024
CUSTOM_MODEL_TEMPERATURE=0.7
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("Created .env file with custom model configuration")
        return True
    except Exception as e:
        print(f"Failed to create .env file: {e}")
        return False

def test_installation():
    """Test if the installation works."""
    print("\nTesting installation...")
    
    try:
        # Test imports
        import torch
        import transformers
        print("Core libraries imported successfully")
        
        # Test model loading (lightweight test)
        from model_config import ModelConfig
        print("Model configuration loaded")
        
        # Show recommendations
        device = ModelConfig.get_device_recommendation()
        model = ModelConfig.get_model_for_device(device)
        print(f"Recommended setup: {model} on {device}")
        
        return True
        
    except Exception as e:
        print(f"Installation test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("Custom AI Model Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    if not install_dependencies():
        print("\nManual installation steps:")
        print("   1. pip install torch transformers accelerate")
        print("   2. pip install -r requirements.txt")
        return
    
    # Check system resources
    check_system_resources()
    
    # Create environment file
    create_env_file()
    
    # Test installation
    if test_installation():
        print("\nSetup completed successfully!")
        print("\nNext steps:")
        print("   1. Run: python test_custom_model.py")
        print("   2. Run: python example.py")
        print("   3. Enjoy your custom AI model!")
        
        print("\nTips:")
        print("   - First run will download the model (may take a few minutes)")
        print("   - Models are cached locally for faster subsequent runs")
        print("   - Use 'python model_config.py' to see available models")
    else:
        print("\nSetup incomplete. Please check the errors above.")


if __name__ == "__main__":
    main()