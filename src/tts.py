import edge_tts
import asyncio
import tempfile
import os
from pydub import AudioSegment
import streamlit as st

# Voice Configuration with Language Support
VOICE_MAPPING = {
    "English": {
        "Siddharth": "en-IN-PrabhatNeural",
        "Aditi": "en-IN-NeerjaNeural",
        "Alternative1": "en-IN-AmitNeural",
        "Alternative2": "en-IN-GunjanNeural",
    },
    "Hindi": {
        "Siddharth": "hi-IN-MadhurNeural",
        "Aditi": "hi-IN-SwaraNeural",
        "Alternative1": "hi-IN-BharatNeural",
        "Alternative2": "hi-IN-KavyaNeural",
    }
}

# Pacing/Speed Settings (speech rate as percentage)
PACING_PRESETS = {
    "Slow (75%)": 0.75,
    "Normal (100%)": 1.0,
    "Fast (125%)": 1.25,
    "Very Fast (150%)": 1.5,
}

async def generate_audio_segment(text, voice, output_file, rate=1.0):
    """
    Generates a single audio segment using EdgeTTS with speed control.
    Rate: 1.0 = normal speed, 0.75 = slow, 1.25 = fast
    """
    try:
        # Rate format: +50% means 50% faster, -25% means 25% slower
        rate_str = f"{int((rate - 1) * 100):+d}%" if rate != 1.0 else "0%"
        
        communicate = edge_tts.Communicate(text, voice, rate=rate_str)
        await communicate.save(output_file)
    except Exception as e:
        print(f"Error generating audio segment: {e}")
        raise

async def generate_full_audio(script_json, language="English", pacing="Normal (100%)", 
                             silence_duration=300, custom_speakers=None):
    """
    Orchestrates the full audio generation with language and pacing support.
    
    Args:
        script_json: List of dialogue items
        language: Language for TTS (English, Hindi, etc.)
        pacing: Pacing preset from PACING_PRESETS
        silence_duration: Pause between speakers in milliseconds
        custom_speakers: Dict mapping speaker names to voice preferences
    """
    combined_audio = AudioSegment.empty()
    temp_files = []
    final_path = None
    
    # Get speech rate from pacing preset
    speech_rate = PACING_PRESETS.get(pacing, 1.0)
    
    # Get voices for language
    language_voices = VOICE_MAPPING.get(language, VOICE_MAPPING["English"])
    
    try:
        # Create silence segment
        silence = AudioSegment.silent(duration=silence_duration) 

        for index, item in enumerate(script_json):
            speaker = item.get("speaker", "Siddharth")
            text = item.get("text", "")
            
            # Skip empty text
            if not text.strip():
                continue
            
            # Get voice - prioritize custom speaker mappings
            if custom_speakers and speaker in custom_speakers:
                voice = custom_speakers[speaker]
            else:
                voice = language_voices.get(speaker, list(language_voices.values())[0])
            
            # Create temp file for this segment
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", mode='wb') as tmp:
                temp_filename = tmp.name
            
            # Generate Audio with speech rate control
            await generate_audio_segment(text, voice, temp_filename, rate=speech_rate)
            temp_files.append(temp_filename)
            
            # Load and append
            segment = AudioSegment.from_mp3(temp_filename)
            combined_audio += segment + silence
            
            # Progress logging
            progress = int((index + 1) / len(script_json) * 100)
            print(f"Generated {progress}%: Line {index+1}/{len(script_json)} - {speaker}")

        # Export final file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", mode='wb') as final_out:
            final_path = final_out.name
        
        combined_audio.export(final_path, format="mp3")
        print(f"Final audio exported to: {final_path}")
        
        return final_path

    except Exception as e:
        print(f"Error in Audio Generation: {e}")
        if final_path and os.path.exists(final_path):
            os.remove(final_path)
        return None
    
    finally:
        # Cleanup temporary files
        for f in temp_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception as e:
                print(f"Warning: Could not delete temp file {f}: {e}")

# Wrapper function to run async code synchronously
def create_podcast_audio(script_json, language="English", pacing="Normal (100%)", 
                        silence_duration=300, custom_speakers=None):
    """
    Synchronous wrapper for async audio generation with enhanced options.
    
    Args:
        script_json: Generated dialogue script
        language: Language for voice synthesis
        pacing: Speech speed/pacing
        silence_duration: Pause between speakers (ms)
        custom_speakers: Custom voice mappings
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(
                generate_full_audio(script_json, language, pacing, silence_duration, custom_speakers)
            )
        else:
            return loop.run_until_complete(
                generate_full_audio(script_json, language, pacing, silence_duration, custom_speakers)
            )
    except RuntimeError:
        return asyncio.run(
            generate_full_audio(script_json, language, pacing, silence_duration, custom_speakers)
        )
    except Exception as e:
        print(f"Error in create_podcast_audio: {e}")
        st.error(f"Audio generation failed: {str(e)[:200]}")
        return None
