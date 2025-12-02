import os
import json
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# Load API Key
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("❌ Groq API Key not found! Please check your .env file.")
    st.stop()

# Initialize Groq Client
client = Groq(api_key=api_key)

def generate_script(text_content):
    """
    Generates a podcast script JSON from the given text using Groq Llama 3.
    """
    
    # 1. Strict System Prompt (Llama 3 loves structure)
    system_prompt = """
    You are a professional podcast producer. 
    Your job is to turn the provided technical text into an engaging, natural 5-minute conversation script between two hosts: Siddharth and Aditi.
    
    PERSONAS:
    - Siddharth (Male): Enthusiastic, curious, uses Indian English idioms ("Arre", "Bas", "Exactly"). He asks the questions a beginner would ask.
    - Aditi (Female): The subject matter expert. Calm, articulate, uses analogies. She explains things clearly to Siddharth.

    FORMAT:
    - You MUST return a VALID JSON object.
    - The JSON must have a key "dialogue" which is a list of objects.
    - Each object must have "speaker" and "text".
    
    JSON STRUCTURE EXAMPLE:
    {
        "dialogue": [
            {"speaker": "Siddharth", "text": "Welcome back folks! Today we have something crazy to discuss."},
            {"speaker": "Aditi", "text": "That's right Sid. We are looking at..."}
        ]
    }
    """

    # 2. User Prompt (The Content)
    # We truncate to ~60k chars to stay safe within Groq's limits (though 70b handles 128k, output tokens are the bottleneck)
    user_content = f"""
    Here is the source text to discuss:
    {text_content[:60000]}
    
    Generate the script now.
    """

    try:
        # 3. The API Call
        completion = client.chat.completions.create(
            model="moonshotai/kimi-k2-instruct-0905",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.7,
            max_tokens=8000,
            response_format={"type": "json_object"} # <--- THE MAGIC SAUCE
        )
        
        # 4. Parsing
        response_text = completion.choices[0].message.content
        data = json.loads(response_text)
        
        # Handle cases where LLM might nest it differently, though our prompt is strict
        if "dialogue" in data:
            return data["dialogue"]
        else:
            return data # Fallback if it returns a list directly

    except Exception as e:
        st.error(f"Error generating script with Groq: {e}")
        return None