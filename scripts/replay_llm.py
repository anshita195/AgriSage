#!/usr/bin/env python3
"""
LLM request replay script for debugging failed requests
"""
import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from services.api.app import call_gemini_llm

def replay_failed_requests(log_file: str = "logs/llm_requests.jsonl"):
    """Replay failed LLM requests from log file"""
    log_path = Path(log_file)
    if not log_path.exists():
        print(f"Log file not found: {log_file}")
        return
    
    failed_requests = []
    
    with open(log_path, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if not entry.get('success', False):
                    failed_requests.append(entry)
            except json.JSONDecodeError:
                continue
    
    if not failed_requests:
        print("No failed requests found in logs")
        return
    
    print(f"Found {len(failed_requests)} failed requests")
    
    for i, req in enumerate(failed_requests[-5:]):  # Replay last 5 failures
        print(f"\n--- Replaying request {i+1} ---")
        print(f"Original timestamp: {req['timestamp']}")
        print(f"Original error: {req.get('error', 'Unknown')}")
        print(f"Request ID: {req['request_id']}")
        
        # Create a test prompt (we don't log full prompts for privacy)
        test_prompt = "Test agricultural question: How much water should I give to wheat crop?"
        
        print("Retrying with test prompt...")
        response, confidence = call_gemini_llm(test_prompt)
        
        if response:
            print(f"✅ SUCCESS: {response[:100]}...")
            print(f"Confidence: {confidence}")
        else:
            print("❌ STILL FAILING")

if __name__ == "__main__":
    replay_failed_requests()
