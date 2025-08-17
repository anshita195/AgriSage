#!/usr/bin/env python3
"""
Gemini API diagnostic script to identify 404 issues
"""
import requests
import json
import os
from dotenv import load_dotenv
import time

load_dotenv()

def test_gemini_api():
    """Test Gemini API with verbose logging"""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Test different endpoints and models
    test_configs = [
        {
            "name": "Current (gemini-1.5-flash)",
            "url": f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
            "model": "gemini-1.5-flash"
        },
        {
            "name": "Alternative (gemini-pro)",
            "url": f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}",
            "model": "gemini-pro"
        },
        {
            "name": "List models",
            "url": f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
            "model": None
        }
    ]
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "AgriSage/1.0"
    }
    
    for config in test_configs:
        print(f"\n🔍 Testing: {config['name']}")
        print(f"URL: {config['url']}")
        
        if config['model']:
            # Test generateContent
            data = {
                "contents": [{
                    "parts": [{
                        "text": "Hello, respond with just 'API working' and confidence: 0.9"
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 50
                }
            }
            
            try:
                start_time = time.time()
                response = requests.post(
                    config['url'], 
                    headers=headers, 
                    json=data, 
                    timeout=30
                )
                latency = time.time() - start_time
                
                print(f"Status: {response.status_code}")
                print(f"Latency: {latency:.2f}s")
                print(f"Response headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ SUCCESS: {json.dumps(result, indent=2)}")
                    return True
                else:
                    print(f"❌ ERROR: {response.text}")
                    
            except Exception as e:
                print(f"❌ EXCEPTION: {e}")
        else:
            # Test list models
            try:
                response = requests.get(config['url'], headers=headers, timeout=30)
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    models = [m.get('name', 'unknown') for m in result.get('models', [])]
                    print(f"✅ Available models: {models[:5]}...")  # Show first 5
                else:
                    print(f"❌ ERROR: {response.text}")
                    
            except Exception as e:
                print(f"❌ EXCEPTION: {e}")
    
    return False

def generate_curl_command():
    """Generate curl command for manual testing"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "No API key found"
    
    curl_cmd = f'''curl -v -X POST \\
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "contents": [{{
      "parts": [{{
        "text": "Hello, respond with just API working"
      }}]
    }}],
    "generationConfig": {{
      "temperature": 0.3,
      "maxOutputTokens": 50
    }}
  }}'
'''
    
    return curl_cmd

if __name__ == "__main__":
    print("🚀 AgriSage Gemini API Diagnostic")
    print("=" * 50)
    
    success = test_gemini_api()
    
    print(f"\n📋 Manual curl command:")
    print(generate_curl_command())
    
    if not success:
        print("\n🔧 Troubleshooting checklist:")
        print("1. Verify API key is valid and not expired")
        print("2. Check if billing is enabled on Google Cloud")
        print("3. Verify API is enabled in Google Cloud Console")
        print("4. Check for IP restrictions or quotas")
        print("5. Try different model names")
