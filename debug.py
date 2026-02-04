from duckduckgo_search import DDGS
import google.generativeai as genai
import os

print("1. Testing DuckDuckGo...")
try:
    results = DDGS().text("India news", max_results=2)
    print(f"Success! Found {len(results)} results.")
    print(results)
except Exception as e:
    print(f"FAILED DDGS: {e}")

print("\n2. Testing Gemini...")
try:
    genai.configure(api_key="AIzaSyB4mjb5rUQXbt702TMydxMQRRSuGdG3_Tc")
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content("Say 'Hello' if working")
    print(f"Success! Response: {response.text}")
except Exception as e:
    print(f"FAILED Gemini: {e}")
