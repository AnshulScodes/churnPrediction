from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()

# Retrieve API key
api_key = os.getenv('POSTHOG_API_KEY')

# Check if API key is loaded correctly
if not api_key:
    print("Error: POSTHOG_API_KEY not found in environment variables")
    exit(1)

# Correct endpoint
url = "https://app.posthog.com/capture/"

# Payload
data = {
    "api_key": api_key,
    "event": "test_event",
    "distinct_id": "goat who figures everything out",
    "properties": {"key": "value"},
}

# Send request
response = requests.post(url, json=data)

# Output response
print(response.status_code, response.json())
