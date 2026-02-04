import google.generativeai as genai
import os

genai.configure(api_key="AIzaSyB4mjb5rUQXbt702TMydxMQRRSuGdG3_Tc")

print("Listing models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error: {e}")
