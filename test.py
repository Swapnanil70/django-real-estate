import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Get the SIGNING_KEY from the .env file or environment
signing_key = os.getenv('SIGNING_KEY')

# Print the SIGNING_KEY
if signing_key:
    print(f"SIGNING_KEY: {signing_key}")
else:
    print("SIGNING_KEY not found")
