
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

print("Testing Gemini 3.8 Flash...")

try:
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents="Reply with: SupplyChainIQ AI connection successful!"
    )

    print("\nSUCCESS!")
    print(response.text)

except Exception as e:
    print("\nFAILED!")
    print(type(e).__name__)
    print(e)