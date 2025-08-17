#!/usr/bin/env python3
"""
SMS Emulator for AgriSage - simulates SMS-based queries for low-connectivity demo
"""
import requests
import json

class SMSEmulator:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
        
    def send_query(self, message, location=""):
        """Send SMS-like query to AgriSage API"""
        try:
            response = requests.post(
                f"{self.api_url}/ask",
                json={
                    "user_id": "sms_user",
                    "question": message,
                    "location": location
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self.format_sms_response(data)
            else:
                return f"ERROR: Server returned {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return f"ERROR: Could not connect to server - {e}"
    
    def format_sms_response(self, data):
        """Format API response for SMS-like display"""
        answer = data.get('answer', 'No answer received')
        confidence = data.get('confidence', 0)
        escalate = data.get('escalate', False)
        
        # Truncate for SMS (160 char limit simulation)
        if len(answer) > 140:
            answer = answer[:137] + "..."
        
        response = f"AgriSage: {answer}"
        
        if escalate:
            response += "\n⚠️ CONSULT EXPERT"
        
        response += f"\n[Confidence: {int(confidence*100)}%]"
        
        return response
    
    def interactive_mode(self):
        """Interactive SMS emulator"""
        print("=== AgriSage SMS Emulator ===")
        print("Type your agricultural questions (or 'quit' to exit)")
        print("Format: QUESTION [LOCATION]")
        print("Example: IRRIGATE wheat Roorkee")
        print()
        
        while True:
            try:
                user_input = input("SMS> ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Parse input - last word might be location
                parts = user_input.split()
                if len(parts) > 1 and parts[-1].istitle():
                    location = parts[-1]
                    question = " ".join(parts[:-1])
                else:
                    location = ""
                    question = user_input
                
                print("Sending query...")
                response = self.send_query(question, location)
                print(f"\n{response}\n")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    emulator = SMSEmulator()
    
    # Test with sample queries
    test_queries = [
        ("IRRIGATE wheat", "Roorkee"),
        ("MARKET price rice", "Dehradun"),
        ("WEATHER forecast", "Haridwar"),
        ("FERTILIZER for potato", "Muzaffarnagar")
    ]
    
    print("=== Testing SMS Emulator ===")
    for question, location in test_queries:
        print(f"\nQuery: {question} {location}")
        response = emulator.send_query(question, location)
        print(f"Response: {response}")
    
    print("\n" + "="*50)
    emulator.interactive_mode()

if __name__ == "__main__":
    main()
