"""
Model configuration for the custom AI model.
Defines available models and their settings.
"""

from typing import Dict, Any, List
import torch


class ModelConfig:
    """Configuration for different AI models."""
    
    # Available models with their configurations
    MODELS = {
        # Lightweight models (good for testing/development)
        "distilgpt2": {
            "name": "distilgpt2",
            "description": "Lightweight GPT-2 model, fast but basic capabilities",
            "size": "82MB",
            "memory_usage": "low",
            "capabilities": ["text_generation", "conversation"],
            "max_length": 1024,
            "recommended_for": ["testing", "development", "low_resource"]
        },
        
        "microsoft/DialoGPT-medium": {
            "name": "microsoft/DialoGPT-medium",
            "description": "Conversational AI model, good for dialogue",
            "size": "345MB", 
            "memory_usage": "medium",
            "capabilities": ["conversation", "dialogue", "chat"],
            "max_length": 1024,
            "recommended_for": ["conversation", "chat_bot"]
        },
        
        # More capable models (require more resources)
        "microsoft/DialoGPT-large": {
            "name": "microsoft/DialoGPT-large",
            "description": "Large conversational model with better responses",
            "size": "774MB",
            "memory_usage": "high", 
            "capabilities": ["conversation", "dialogue", "reasoning"],
            "max_length": 1024,
            "recommended_for": ["production", "better_quality"]
        },
        
        "gpt2": {
            "name": "gpt2",
            "description": "Original GPT-2 model, good general capabilities",
            "size": "548MB",
            "memory_usage": "medium",
            "capabilities": ["text_generation", "completion", "reasoning"],
            "max_length": 1024,
            "recommended_for": ["general_purpose", "text_generation"]
        },
        
        "gpt2-medium": {
            "name": "gpt2-medium",
            "description": "Medium GPT-2 model with better capabilities",
            "size": "1.5GB",
            "memory_usage": "high",
            "capabilities": ["text_generation", "reasoning", "analysis"],
            "max_length": 1024,
            "recommended_for": ["better_reasoning", "analysis"]
        },
        
        # Instruction-tuned models (better for following instructions)
        "microsoft/DialoGPT-small": {
            "name": "microsoft/DialoGPT-small",
            "description": "Small conversational model, very fast",
            "size": "117MB",
            "memory_usage": "low",
            "capabilities": ["conversation", "chat"],
            "max_length": 512,
            "recommended_for": ["fast_response", "low_resource"]
        }
    }
    
    @classmethod
    def get_model_info(cls, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        return cls.MODELS.get(model_name, {})
    
    @classmethod
    def list_models(cls) -> List[str]:
        """List all available models."""
        return list(cls.MODELS.keys())
    
    @classmethod
    def get_recommended_model(cls, use_case: str = "general") -> str:
        """Get recommended model for a specific use case."""
        recommendations = {
            "testing": "distilgpt2",
            "development": "microsoft/DialoGPT-small", 
            "conversation": "microsoft/DialoGPT-medium",
            "reasoning": "gpt2",
            "production": "microsoft/DialoGPT-large",
            "low_resource": "distilgpt2",
            "general": "microsoft/DialoGPT-medium"
        }
        return recommendations.get(use_case, "microsoft/DialoGPT-medium")
    
    @classmethod
    def get_device_recommendation(cls) -> str:
        """Get recommended device based on available hardware."""
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            if gpu_memory > 8:
                return "cuda"  # High-end GPU
            elif gpu_memory > 4:
                return "cuda"  # Mid-range GPU
            else:
                return "cpu"   # Low VRAM GPU, use CPU instead
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return "mps"  # Apple Silicon
        else:
            return "cpu"
    
    @classmethod
    def get_model_for_device(cls, device: str) -> str:
        """Get recommended model based on device capabilities."""
        if device == "cpu":
            return "distilgpt2"  # Lightweight for CPU
        elif device == "mps":
            return "microsoft/DialoGPT-medium"  # Good balance for Apple Silicon
        elif device == "cuda":
            # Check GPU memory
            try:
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
                if gpu_memory > 8:
                    return "gpt2-medium"  # Can handle larger models
                elif gpu_memory > 4:
                    return "microsoft/DialoGPT-large"
                else:
                    return "microsoft/DialoGPT-medium"
            except:
                return "microsoft/DialoGPT-medium"
        else:
            return "microsoft/DialoGPT-medium"
    
    @classmethod
    def print_model_info(cls):
        """Print information about all available models."""
        print("🤖 Available AI Models:")
        print("=" * 60)
        
        for model_name, info in cls.MODELS.items():
            print(f"\n📦 {model_name}")
            print(f"   Description: {info.get('description', 'N/A')}")
            print(f"   Size: {info.get('size', 'Unknown')}")
            print(f"   Memory Usage: {info.get('memory_usage', 'Unknown')}")
            print(f"   Capabilities: {', '.join(info.get('capabilities', []))}")
            print(f"   Recommended for: {', '.join(info.get('recommended_for', []))}")
        
        print(f"\n🖥️  Recommended device: {cls.get_device_recommendation()}")
        print(f"🎯 Recommended model for your system: {cls.get_model_for_device(cls.get_device_recommendation())}")


def main():
    """Demo function to show model information."""
    ModelConfig.print_model_info()


if __name__ == "__main__":
    main()
