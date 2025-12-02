import edge_tts
import asyncio
import tempfile
import os
from pydub import AudioSegment

# Voice Configuration (The Indian Context)
VOICE_MAPPING = {
    "Siddharth": "en-IN-PrabhatNeural",  # Male, Indian Accent
    "Aditi": "en-IN-NeerjaNeural"        # Female, Indian Accent
}

async def generate_audio_segment(text, voice, output_file):
    """Generates a single audio segment using EdgeTTS."""
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
    except Exception as e:
        print(f"Error generating audio segment: {e}")
        raise

async def generate_full_audio(script_json):
    """
    Orchestrates the full audio generation:
    1. Loop through script lines.
    2. Generate individual audio clips.
    3. Stitch them together with silence.
    4. Return path to final MP3.
    """
    combined_audio = AudioSegment.empty()
    temp_files = []
    final_path = None

    try:
        # Create a silence segment (300ms pause between speakers)
        silence = AudioSegment.silent(duration=300) 

        for index, item in enumerate(script_json):
            speaker = item.get("speaker", "Siddharth")  # Use .get() for safety
            text = item.get("text", "")
            
            # Skip empty text
            if not text.strip():
                continue
                
            voice = VOICE_MAPPING.get(speaker, "en-IN-PrabhatNeural")
            
            # Create a temp file for this specific line
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", mode='wb') as tmp:
                temp_filename = tmp.name
            
            # Generate Audio (Await execution)
            await generate_audio_segment(text, voice, temp_filename)
            temp_files.append(temp_filename)
            
            # Load into Pydub and append
            segment = AudioSegment.from_mp3(temp_filename)
            combined_audio += segment + silence
            
            # Optional: Print progress to console
            print(f"Generated line {index+1}/{len(script_json)}: {speaker}")

        # Export final file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", mode='wb') as final_out:
            final_path = final_out.name
        
        combined_audio.export(final_path, format="mp3")
        print(f"Final audio exported to: {final_path}")
        
        return final_path

    except Exception as e:
        print(f"Error in Audio Generation: {e}")
        # Clean up final file if it was created but export failed
        if final_path and os.path.exists(final_path):
            os.remove(final_path)
        return None
    
    finally:
        # Cleanup temporary segment files
        for f in temp_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception as e:
                print(f"Warning: Could not delete temp file {f}: {e}")

# Wrapper function to run async code synchronously
def create_podcast_audio(script_json):
    """
    Synchronous wrapper for async audio generation.
    Handles event loop creation for different environments.
    """
    try:
        # Try to get existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running (e.g., in Jupyter/Streamlit)
            # Create a new loop in a thread
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(generate_full_audio(script_json))
        else:
            return loop.run_until_complete(generate_full_audio(script_json))
    except RuntimeError:
        # No event loop exists, create a new one
        return asyncio.run(generate_full_audio(script_json))
    except Exception as e:
        print(f"Error in create_podcast_audio: {e}")
        return None