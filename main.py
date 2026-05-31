import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("API Key Found:", api_key is not None)

client = genai.Client(api_key=api_key)

topic = input("Enter a study topic: ")

prompt = f"""
For the topic '{topic}', provide:

1. A concise study summary
2. Five quiz questions
3. Five flashcards with answers

Format the response clearly.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

print("\n")
print(response.text)

filename = f"study_materials/{topic}.txt"

with open(filename, "w", encoding="utf-8") as file:
    file.write(response.text)

print(f"\nSaved to: {filename}")