import os
import json
import time
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# Load API Key
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("❌ Groq API Key not found! Please check your .env file.")
    st.stop()

# Configuration
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", 2))

# Available Groq Models
AVAILABLE_MODELS = [
    "moonshotai/kimi-k2-instruct-0905",
]

# Initialize Groq Client
client = Groq(api_key=api_key)

def get_system_prompt(speaker1_name="Siddharth", speaker2_name="Aditi", tone="Fun & Casual"):
    """
    Generates a dynamic system prompt based on tone and speaker preferences.
    """
    tone_instructions = {
        "Fun & Casual": "Keep it light, witty, and conversational. Use humor and casual language.",
        "Formal & Educational": "Be precise, academic, and structured. Focus on clarity and learning outcomes.",
        "Debate Style": "Present multiple perspectives, arguments and counter-arguments respectfully."
    }
    
    tone_desc = tone_instructions.get(tone, tone_instructions["Fun & Casual"])
    
    system_prompt = f"""
    You are a professional podcast producer. 
    Your job is to turn the provided technical text into an engaging, natural 5-minute conversation script between two hosts: {speaker1_name} and {speaker2_name}.
    
    TONE: {tone_desc}
    
    PERSONAS:
    - {speaker1_name}: Enthusiastic, curious, uses Indian English idioms ("Arre", "Bas", "Exactly"). Asks beginner-level questions.
    - {speaker2_name}: Subject matter expert. Calm, articulate, uses analogies and real-world examples.

    FORMAT:
    - You MUST return a VALID JSON object.
    - The JSON must have a key "dialogue" which is a list of objects.
    - Each object must have "speaker" (exact name: {speaker1_name} or {speaker2_name}) and "text".
    
    JSON STRUCTURE EXAMPLE:
    {{
        "dialogue": [
            {{"speaker": "{speaker1_name}", "text": "Welcome back folks! Today we have something to discuss."}},
            {{"speaker": "{speaker2_name}", "text": "That's right. We are looking at..."}}
        ]
    }}
    """
    return system_prompt


def generate_script_with_retry(text_content, model="moonshotai/kimi-k2-instruct-0905", tone="Fun & Casual", 
                               speaker1="Siddharth", speaker2="Aditi"):
    """
    Generates a podcast script with exponential backoff retry logic.
    """
    system_prompt = get_system_prompt(speaker1, speaker2, tone)
    
    user_content = f"""
    Here is the source text to discuss:
    {text_content[:60000]}
    
    Generate the script now. Make it engaging and appropriate for a {tone.lower()} podcast.
    """

    for attempt in range(MAX_RETRIES):
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text(f"Attempt {attempt + 1}/{MAX_RETRIES}: Generating script with {model}...")
            
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.7,
                max_tokens=8000,
                response_format={"type": "json_object"}
            )
            
            response_text = completion.choices[0].message.content
            data = json.loads(response_text)
            
            progress_bar.progress(100)
            status_text.text("✅ Script generated successfully!")
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()
            
            # Handle different JSON structures
            if "dialogue" in data:
                return data["dialogue"]
            else:
                return data

        except json.JSONDecodeError as e:
            st.warning(f"⚠️ JSON parsing error on attempt {attempt + 1}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY ** attempt)  # Exponential backoff
            else:
                st.error("❌ Failed to parse response after retries.")
                return None
                
        except Exception as e:
            st.warning(f"⚠️ API error on attempt {attempt + 1}: {str(e)[:100]}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY ** attempt)
            else:
                st.error(f"❌ Failed to generate script after {MAX_RETRIES} retries.")
                return None
    
    return None


def generate_script(text_content, model="moonshotai/kimi-k2-instruct-0905", tone="Fun & Casual", 
                   speaker1="Siddharth", speaker2="Aditi"):
    """
    Public wrapper for script generation with improved error handling.
    """
    return generate_script_with_retry(text_content, model, tone, speaker1, speaker2)