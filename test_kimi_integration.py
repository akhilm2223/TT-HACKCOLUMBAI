import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_kimi_api():
    print("=== Testing Kimi K2 Integration (Requests + Save) ===")
    
    api_key = os.getenv("KIMI_K2_THINKING_API_KEY")
    api_url = "https://api.k2think.ai/v1/chat/completions"
    model_id = "MBZUAI-IFM/K2-Think-v2"
    
    if not api_key:
        print("Error: KIMI_K2_THINKING_API_KEY not found in .env")
        return

    # 1. Load the generated prompt
    prompt_file = "generated_prompt.txt"
    if not os.path.exists(prompt_file):
        print(f"Error: {prompt_file} not found.")
        return
        
    with open(prompt_file, "r") as f:
        prompt = f.read()
    
    print(f"Loaded Prompt ({len(prompt)} chars).")

    # 2. Call API
    print(f"Sending request to {api_url}...")
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model_id,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=120) # Long timeout for thinking models
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            print("\n=== Kimi K2 Response ===")
            print(content)
            
            # Save to file
            output_file = "kimi_response.txt"
            with open(output_file, "w") as f:
                f.write(content)
            print(f"\n[SUCCESS] Response saved to {output_file}")
            
        else:
            print(f"\nAPI Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\nRequests Error: {e}")

if __name__ == "__main__":
    test_kimi_api()
