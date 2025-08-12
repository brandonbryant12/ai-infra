#!/usr/bin/env python3
"""
Test script to verify LiteLLM callback is working
"""

import os
import sys
import litellm
from litellm import completion

# Set verbose mode
litellm.set_verbose = True

# Import our custom callback
from custom_langfuse_callback import CustomLangfuseLogger, custom_callback_function

def test_class_callback():
    """Test with class-based callback"""
    print("\n" + "="*60)
    print("Testing CLASS-BASED callback")
    print("="*60)
    
    # Create an instance of the logger
    logger = CustomLangfuseLogger()
    
    # Set callbacks
    litellm.success_callback = [logger]
    litellm.failure_callback = [logger]
    
    try:
        # Make a simple test call
        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'test' in one word"}],
            mock_response="test"  # Use mock response to avoid actual API call
        )
        print(f"\nResponse received: {response}")
    except Exception as e:
        print(f"Error: {e}")

def test_function_callback():
    """Test with function-based callback"""
    print("\n" + "="*60)
    print("Testing FUNCTION-BASED callback")
    print("="*60)
    
    # Set callbacks
    litellm.success_callback = [custom_callback_function]
    litellm.failure_callback = [custom_callback_function]
    
    try:
        # Make a simple test call
        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'test' in one word"}],
            mock_response="test"  # Use mock response to avoid actual API call
        )
        print(f"\nResponse received: {response}")
    except Exception as e:
        print(f"Error: {e}")

def test_simple_print_callback():
    """Test with simplest possible callback"""
    print("\n" + "="*60)
    print("Testing SIMPLE PRINT callback")
    print("="*60)
    
    def simple_callback(kwargs, response, start_time, end_time):
        print(f"\n[SIMPLE CALLBACK] Called!")
        print(f"[SIMPLE CALLBACK] Duration: {end_time - start_time}")
        print(f"[SIMPLE CALLBACK] Response type: {type(response)}")
        print(f"[SIMPLE CALLBACK] Kwargs keys: {list(kwargs.keys())}")
    
    # Set callbacks
    litellm.success_callback = [simple_callback]
    litellm.failure_callback = [simple_callback]
    
    try:
        # Make a simple test call
        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'test' in one word"}],
            mock_response="test"  # Use mock response to avoid actual API call
        )
        print(f"\nResponse received: {response}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Starting LiteLLM callback tests...")
    print(f"Python version: {sys.version}")
    print(f"LiteLLM version: {litellm.__version__ if hasattr(litellm, '__version__') else 'unknown'}")
    
    # Test different callback approaches
    test_simple_print_callback()
    test_function_callback()
    test_class_callback()
    
    print("\n" + "="*60)
    print("Tests completed!")
    print("="*60)