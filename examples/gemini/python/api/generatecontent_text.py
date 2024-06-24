import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")

response = model.generate_content("Give me python code to sort a list")
print(response.text)
