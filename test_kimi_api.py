"""
Quick test for Kimi K2 / Moonshot or IFM K2 Think API key.
Run: py -3 test_kimi_api.py

If .env has MOONSHOT_API_KEY set, it will be loaded. You can also pass the key inline:
  set MOONSHOT_API_KEY=IFM-yourkey && py -3 test_kimi_api.py
"""
import os

# Load .env from project root (same directory as this script's parent if run from repo root)
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
try:
    from dotenv import load_dotenv
    loaded = load_dotenv(_env_path)
    if loaded:
        print(f"Loaded .env from: {_env_path}")
    else:
        load_dotenv()  # fallback: cwd
except ImportError:
    pass

api_key = (os.environ.get("MOONSHOT_API_KEY") or os.environ.get("KIMI_K2_API_KEY") or "").strip()

if not api_key:
    print("FAIL: No API key found.")
    print("  Set MOONSHOT_API_KEY=yourkey in .env (e.g. IFM-xxx for DevFest K2 Think).")
    print(f"  Or run: set MOONSHOT_API_KEY=yourkey && py -3 test_kimi_api.py")
    exit(1)

# Determine base URL and model (IFM K2 Think vs Moonshot)
if api_key.strip().upper().startswith("IFM-"):
    base_url = (os.environ.get("IFM_K2_API_BASE_URL") or "").strip().rstrip("/")
    if not base_url:
        print("Your key is an IFM K2 Think key (e.g. Columbia DevFest).")
        print("Set IFM_K2_API_BASE_URL in .env to the API base URL from the event.")
        print("  Get it from: the cURL example in api.png, or the DevFest team/WhatsApp.")
        print("  Example (replace with the real URL from the team):")
        print('  IFM_K2_API_BASE_URL=https://api.example.com/v1')
        exit(1)
    model = os.environ.get("K2_THINK_MODEL", "k2-think")
    print(f"Using IFM K2 Think: {base_url} (model: {model})")
else:
    base_url = "https://api.moonshot.ai/v1"
    model = "kimi-k2.5"
    print("Using Moonshot (Kimi K2.5)")

print(f"Key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}")
print("Calling API...")

try:
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=base_url)
    r = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Reply with exactly: OK"}],
        max_tokens=10,
    )
    reply = r.choices[0].message.content
    print("SUCCESS: API key is valid.")
    print("Reply:", reply)
except Exception as e:
    print("FAIL:", e)
    if "IFM-" in api_key and "401" in str(e):
        print("\nIf this is your Columbia DevFest key, add IFM_K2_API_BASE_URL to .env")
        print("with the base URL from the event's api.png or team.")
    exit(1)
