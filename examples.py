#!/usr/bin/env python3
"""
Simple example of using the Grok LLM API Client
"""

from grok_client import GrokClient
from config import XAI_API_KEY
import os


def main():
    """Simple example of querying Grok."""
    print("Grok LLM API Simple Example")
    print("=" * 30)
    
    try:
        # Initialize the Grok client with API key from config
        grok = GrokClient(api_key=XAI_API_KEY)
        
        # Ask a simple question
        question = "Hello, how are you?"
        print(f"Question: {question}")
        
        # Try different models
        models_to_try = ["grok-2-latest", "grok-3-latest", "grok-4-latest"]
        
        for model in models_to_try:
            try:
                print(f"\nTrying model: {model}")
                response = grok.simple_query(question, model=model)
                print(f"Answer: {response}")
                break
            except Exception as e:
                print(f"Model {model} failed: {e}")
                continue
        
    except ValueError as e:
        print(f"Error: {e}")
        print("\nTo fix this:")
        print("1. Get an API key from https://console.x.ai/")
        print("2. Set the XAI_API_KEY environment variable:")
        print("   export XAI_API_KEY='your_api_key_here'")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
