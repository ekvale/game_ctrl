from dotenv import load_dotenv
import os
from elevenlabs.client import ElevenLabs

# Load environment variables
load_dotenv('.env.prod')

# Get API key
elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
print(f"API Key found: {'Yes' if elevenlabs_key else 'No'}")

# Test the API
if elevenlabs_key:
    try:
        client = ElevenLabs(api_key=elevenlabs_key)
        # Try to list voices (simple API test)
        voices = client.voices.get_all()
        print("API Test successful!")
        print(f"Available voices: {len(voices)}")
    except Exception as e:
        print(f"API Test failed: {str(e)}")
else:
    print("No API key found in .env.prod") 