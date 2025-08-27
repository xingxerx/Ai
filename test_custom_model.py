"""
Test script for the custom AI model.
Shows available models and tests basic functionality.
"""

import asyncio
import sys
import os
from model_config import ModelConfig
from agi_agent.core.custom_model import CustomModelProvider


async def test_model_selection():
    """Test automatic model selection."""
    print("🔍 Testing Model Selection")
    print("=" * 50)
    
    # Show available models
    ModelConfig.print_model_info()
    
    print("\n🧪 Testing Model Initialization...")
    
    try:
        # Test with auto selection
        print("\n1. Testing auto model selection...")
        model = CustomModelProvider(model_name="auto", device="auto")
        
        print(f"✅ Selected model: {model.model_name}")
        print(f"✅ Using device: {model.device}")
        
        # Test basic generation
        print("\n2. Testing text generation...")
        test_prompt = "Hello! How are you today?"
        
        print(f"📝 Prompt: {test_prompt}")
        print("🔄 Generating response...")
        
        response = await model.generate_response(test_prompt)
        print(f"🤖 Response: {response}")
        
        # Show model info
        print("\n3. Model Information:")
        info = model.get_model_info()
        for key, value in info.items():
            print(f"   {key}: {value}")
        
        print("\n✅ Custom model test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing custom model: {e}")
        print("💡 This might be due to missing dependencies or insufficient resources.")
        print("   Try installing: pip install torch transformers")


async def test_different_models():
    """Test different model configurations."""
    print("\n🔬 Testing Different Models")
    print("=" * 50)
    
    # Test lightweight model
    test_models = ["distilgpt2", "microsoft/DialoGPT-small"]
    
    for model_name in test_models:
        try:
            print(f"\n📦 Testing {model_name}...")
            model = CustomModelProvider(model_name=model_name, device="auto")
            
            # Quick test
            response = await model.generate_response("Hi there!")
            print(f"✅ {model_name}: {response[:100]}...")
            
        except Exception as e:
            print(f"❌ Failed to test {model_name}: {e}")


def show_system_info():
    """Show system information relevant to model selection."""
    print("💻 System Information")
    print("=" * 50)
    
    import torch
    
    print(f"🐍 Python version: {sys.version}")
    print(f"🔥 PyTorch version: {torch.__version__}")
    print(f"🖥️  CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"🎮 CUDA device count: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            memory_gb = props.total_memory / 1e9
            print(f"   GPU {i}: {props.name} ({memory_gb:.1f}GB)")
    
    if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        print("🍎 Apple Silicon MPS available: Yes")
    else:
        print("🍎 Apple Silicon MPS available: No")
    
    print(f"\n🎯 Recommended device: {ModelConfig.get_device_recommendation()}")
    print(f"🤖 Recommended model: {ModelConfig.get_model_for_device(ModelConfig.get_device_recommendation())}")


async def interactive_test():
    """Interactive test mode."""
    print("\n💬 Interactive Test Mode")
    print("=" * 50)
    print("Type 'quit' to exit, 'models' to see available models")
    
    try:
        model = CustomModelProvider(model_name="auto", device="auto")
        print(f"🤖 Loaded model: {model.model_name}")
        
        while True:
            user_input = input("\n🧠 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            elif user_input.lower() == 'models':
                ModelConfig.print_model_info()
                continue
            elif not user_input:
                continue
            
            print("🔄 Thinking...")
            response = await model.generate_response(user_input)
            print(f"🤖 AI: {response}")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error in interactive mode: {e}")


async def main():
    """Main test function."""
    print("🤖 Custom AI Model Test Suite")
    print("=" * 60)
    
    # Show system info
    show_system_info()
    
    # Test model selection
    await test_model_selection()
    
    # Ask user what to do next
    print("\n" + "=" * 60)
    print("What would you like to do next?")
    print("1. Test different models")
    print("2. Interactive chat mode")
    print("3. Exit")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            await test_different_models()
        elif choice == "2":
            await interactive_test()
        elif choice == "3":
            print("👋 Goodbye!")
        else:
            print("Invalid choice. Exiting...")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())
