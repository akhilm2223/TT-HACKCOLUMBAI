
import os
import sys
from dotenv import load_dotenv

# Mock environment for testing if not present
if not os.getenv("MOONSHOT_API_KEY"):
    os.environ["MOONSHOT_API_KEY"] = "IFM-TEST-KEY"
if not os.getenv("IFM_K2_API_BASE_URL"):
    os.environ["IFM_K2_API_BASE_URL"] = "https://mock.api.ifm.ai/v1"

try:
    print("--- Verifying K2-Think Detector ---")
    from kimi_k2_detector import KimiK2Detector
    detector = KimiK2Detector()
    print(f"Detector initialized.")
    from kimi_k2_detector import _get_base_url_and_model
    base_url, model = _get_base_url_and_model(detector.api_key)
    print(f"API Key Prefix: {detector.api_key[:4]}")
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    print("Detector Verification: PASS\n")

    print("--- Verifying K2-Think Coach ---")
    from modules.llm_coach import K2Coach
    coach = K2Coach()
    print(f"Coach initialized.")
    print(f"Coach Model: {coach.model}")
    print("Coach Verification: PASS\n")

    print("--- K2-Think Integration Verification Successful ---")

except ImportError as e:
    print(f"Import Error: {e}")
    exit(1)
except Exception as e:
    print(f"Runtime Error: {e}")
    exit(1)
