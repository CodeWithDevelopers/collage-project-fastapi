import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
genai.configure(api_key="AIzaSyADtAStrtrP9OseGxvuwTWxyL8qevJZjaI")

def get_gemini_model():
    return genai.GenerativeModel("gemini-2.0-flash")
