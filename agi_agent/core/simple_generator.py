"""
A simple fallback generator for when custom model dependencies are not met.
"""

import json

class SimpleLocalGenerator:
    """
    A fallback generator that provides a helpful message instead of processing a request.
    It is used when the main custom model dependencies (like torch) are not installed.
    """
    def __init__(self, *args, **kwargs):
        pass

    async def understand_request(self, user_input: str, context: dict) -> dict:
        """
        Returns a structured response indicating that dependencies are missing.
        """
        return {
            "objective": "inform_user",
            "requirements": ["Missing dependencies for the custom AI model."],
            "constraints": ["Cannot process the request due to missing 'torch' or 'transformers' packages.", "Please install them by running: pip install torch transformers accelerate"]
        }