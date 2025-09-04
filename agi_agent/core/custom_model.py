"""
Custom AI Model Provider for the AGI Agent.
Provides local AI model capabilities using Hugging Face transformers.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
import json
import re
import sys
import os

# Add parent directory to path to import model_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from model_config import ModelConfig


class CustomModelProvider:
    """
    Custom AI model provider using local Hugging Face models.
    Supports various open-source models like Llama, Mistral, etc.
    """
    
    def __init__(self, model_name: str = "auto", device: str = "auto"):
        """
        Initialize the custom model provider.

        Args:
            model_name: Name of the Hugging Face model to use, or "auto" for smart selection
            device: Device to run the model on ('cpu', 'cuda', 'mps', or 'auto')
        """
        self.device = self._get_device(device)
        self.model_name = self._select_model(model_name)
        self.logger = logging.getLogger(__name__)

        # Model components
        self.tokenizer = None
        self.model = None
        self.pipeline = None

        # Get model configuration
        self.model_config = ModelConfig.get_model_info(self.model_name)

        # Generation settings
        self.max_length = self.model_config.get("max_length", 1024)
        self.temperature = 0.7
        self.top_p = 0.9
        self.do_sample = True

        self.logger.info(f"Selected model: {self.model_name} on device: {self.device}")

        # Initialize the model
        self._initialize_model()
    
    def _get_device(self, device: str) -> str:
        """Determine the best device to use."""
        if device == "auto":
            return ModelConfig.get_device_recommendation()
        return device

    def _select_model(self, model_name: str) -> str:
        """Select the best model for the current device."""
        if model_name == "auto":
            return ModelConfig.get_model_for_device(self.device)
        return model_name
    
    def _initialize_model(self):
        """Initialize the tokenizer and model."""
        try:
            # Import heavy dependencies lazily so module import doesn't fail
            import torch  # type: ignore
            from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline  # type: ignore

            self.logger.info(f"Loading model: {self.model_name} on {self.device}")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                padding_side="left"
            )

            # Add pad token if it doesn't exist
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                low_cpu_mem_usage=True
            )

            if self.device != "cuda":
                self.model = self.model.to(self.device)

            # Create text generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )

            self.logger.info("Model loaded successfully")

        except ImportError as e:
            # Graceful fallback: no heavy deps, use simple local generator
            self.logger.warning(
                "Missing dependencies for custom model (%s). Falling back to simple local generator.",
                e,
            )
            self.tokenizer = None
            self.model = None
            self.pipeline = self._simple_pipeline()
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            # Fallback to a smaller model (requires transformers); if that fails, use simple
            try:
                self._initialize_fallback_model()
            except Exception:
                self.logger.warning("Fallback model load failed. Using simple local generator.")
                self.tokenizer = None
                self.model = None
                self.pipeline = self._simple_pipeline()

    def _initialize_fallback_model(self):
        """Initialize a smaller fallback model if the main model fails."""
        try:
            # transformers is required even for fallback
            from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline  # type: ignore

            fallback_model = "distilgpt2"
            self.logger.info(f"Loading fallback model: {fallback_model}")

            self.tokenizer = AutoTokenizer.from_pretrained(fallback_model)
            self.tokenizer.pad_token = self.tokenizer.eos_token

            self.model = AutoModelForCausalLM.from_pretrained(fallback_model)
            self.model = self.model.to(self.device)

            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1
            )

            self.logger.info("Fallback model loaded successfully")

        except ImportError as e:
            self.logger.warning("'transformers' not available for fallback (%s). Using simple local generator.", e)
            self.tokenizer = None
            self.model = None
            self.pipeline = self._simple_pipeline()
        except Exception as e:
            self.logger.warning(f"Failed to load fallback model: {e}. Using simple local generator.")
            self.tokenizer = None
            self.model = None
            self.pipeline = self._simple_pipeline()

    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate a response to the given prompt.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated response text
        """
        try:
            # Ensure we have some pipeline to use
            if self.pipeline is None:
                self.pipeline = self._simple_pipeline()

            # Prepare generation parameters
            generation_kwargs = {
                "max_length": kwargs.get("max_length", self.max_length),
                "temperature": kwargs.get("temperature", self.temperature),
                "top_p": kwargs.get("top_p", self.top_p),
                "do_sample": kwargs.get("do_sample", self.do_sample),
                "num_return_sequences": 1,
                "return_full_text": False
            }
            # Only include pad_token_id if tokenizer is available
            if getattr(self, "tokenizer", None) is not None and hasattr(self.tokenizer, "eos_token_id"):
                generation_kwargs["pad_token_id"] = self.tokenizer.eos_token_id

            # Run generation in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._generate_sync,
                prompt,
                generation_kwargs
            )

            return result

        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return f"Error: Unable to generate response - {str(e)}"
    
    def _generate_sync(self, prompt: str, generation_kwargs: Dict[str, Any]) -> str:
        """Synchronous generation method."""
        try:
            # Generate response via installed pipeline or simple fallback
            outputs = self.pipeline(
                prompt,
                **generation_kwargs
            )
            
            # Extract the generated text
            if outputs and len(outputs) > 0:
                generated_text = outputs[0]["generated_text"]
                
                # Clean up the response
                response = self._clean_response(generated_text, prompt)
                return response
            else:
                return "No response generated"
                
        except Exception as e:
            self.logger.error(f"Sync generation error: {e}")
            return f"Generation error: {str(e)}"
    
    def _clean_response(self, generated_text: str, original_prompt: str) -> str:
        """Clean and format the generated response."""
        # Remove the original prompt if it's included
        if generated_text.startswith(original_prompt):
            response = generated_text[len(original_prompt):].strip()
        else:
            response = generated_text.strip()
        
        # Remove any special tokens
        response = re.sub(r'<\|.*?\|>', '', response)
        response = re.sub(r'\[.*?\]', '', response)
        
        # Clean up whitespace
        response = ' '.join(response.split())
        
        return response if response else "I understand your request, but I need more context to provide a helpful response."

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "max_length": self.max_length,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "model_loaded": self.model is not None,
            "tokenizer_loaded": self.tokenizer is not None,
            "mode": "full" if self.model is not None else ("fallback" if self.pipeline and self.tokenizer else "simple")
        }

    def set_generation_params(self, **kwargs):
        """Update generation parameters."""
        if "max_length" in kwargs:
            self.max_length = kwargs["max_length"]
        if "temperature" in kwargs:
            self.temperature = kwargs["temperature"]
        if "top_p" in kwargs:
            self.top_p = kwargs["top_p"]
        if "do_sample" in kwargs:
            self.do_sample = kwargs["do_sample"]

    def _simple_pipeline(self):
        """Return a very lightweight, dependency-free text generation callable."""
        def _call(prompt: str, **kwargs):
            # A naive, dependency-free response that echoes intent
            max_len = int(kwargs.get("max_length", 256))
            # Strip and compress whitespace
            clean = " ".join(str(prompt).strip().split())
            summary = (clean[: max_len - 120] + "…") if len(clean) > max_len - 120 else clean
            response = (
                "[Local Simple Generator]\n"
                "This environment lacks torch/transformers; returning a concise reply.\n\n"
                f"You asked: {summary}\n\n"
                "Reply: I understand your request and can outline a high-level approach. "
                "To enable richer, model-generated responses, install torch and transformers."
            )
            return [{"generated_text": response}]
        return _call
