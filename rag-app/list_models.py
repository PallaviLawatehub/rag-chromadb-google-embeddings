import google.genai as genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("Available models:")
models = client.models.list()
for model in models:
    print(f"  - {model.name}")
    if hasattr(model, 'supported_generation_methods'):
        print(f"    Methods: {model.supported_generation_methods}")
