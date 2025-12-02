import streamlit as st
import os
import json
from datetime import datetime
from src.processing import process_pdf
from src.generation import generate_script, AVAILABLE_MODELS
from src.tts import create_podcast_audio, VOICE_MAPPING, PACING_PRESETS
from src.cache import hash_text, get_cache_key, get_from_cache, save_to_cache, cleanup_old_cache
from src.analytics import record_file_processing, record_script_generation, record_audio_generation, get_stats

# 1. Page Configuration
st.set_page_config(
    page_title="AudioLearn",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS for enhanced UI
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #1DB954;
        color: white;
        border-radius: 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1ed760;
    }
    .metric-card {
        background-color: #f0f0f0;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Header
st.title("🎧 AudioLearn")
st.caption("Transform PDFs into Engaging Podcasts with AI | Multi-Language Support | Advanced Customization")

# Clean up old cache periodically
if 'cleanup_done' not in st.session_state:
    cleanup_old_cache(days=7)
    st.session_state['cleanup_done'] = True

# 4. Sidebar: Settings & Data Ingestion
with st.sidebar:
    st.header("📂 Data Source")
    uploaded_file = st.file_uploader("Upload a PDF Document", type=["pdf"])
    
    st.markdown("---")
    st.markdown("### ⚙️ Podcast Settings")
    
    # Model Selection
    st.subheader("🤖 AI Model")
    selected_model = st.selectbox(
        "Choose Groq Model",
        AVAILABLE_MODELS,
        help="Using Kimi K2 Instruct - optimized for script generation"
    )
    
    # Tone Selection
    tone = st.selectbox(
        "Podcast Tone",
        ["Fun & Casual", "Formal & Educational", "Debate Style"],
        help="Affects the conversational style and language used"
    )
    
    # Language Selection
    st.subheader("🗣️ Voice & Language")
    language = st.selectbox(
        "Language",
        list(VOICE_MAPPING.keys()),
        help="Language for text-to-speech synthesis"
    )
    
    # Speaker Customization
    st.subheader("🎤 Speakers")
    speaker1_name = st.text_input("Speaker 1 Name", value="Siddharth", max_chars=20)
    speaker2_name = st.text_input("Speaker 2 Name", value="Aditi", max_chars=20)
    
    # Audio Settings
    st.subheader("🎧 Audio Settings")
    pacing = st.selectbox(
        "Speech Pacing",
        list(PACING_PRESETS.keys()),
        help="Controls how fast or slow the speakers talk"
    )
    
    silence_duration = st.slider(
        "Silence Between Speakers (ms)",
        min_value=100,
        max_value=1000,
        value=300,
        step=50,
        help="Pause duration between speaker transitions"
    )
    
    # Advanced Settings
    with st.expander("🔧 Advanced Settings"):
        enable_cache = st.checkbox("Enable Script Caching", value=True)
        enable_analytics = st.checkbox("Enable Analytics Tracking", value=True)
    
    # Analytics Sidebar
    st.markdown("---")
    st.subheader("📊 Session Analytics")
    if enable_analytics:
        stats = get_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Files Processed", stats["total_files_processed"])
            st.metric("Scripts Generated", stats["total_scripts_generated"])
        with col2:
            st.metric("Audio Files", stats["total_audio_files"])
    
    # About Section
    st.markdown("---")
    with st.expander("ℹ️ About AudioLearn"):
        st.markdown("""
        **AudioLearn** converts academic PDFs into natural podcast conversations.
        
        **Features:**
        - 🎙️ Multi-speaker dialogue generation
        - 🌍 Multi-language support (English, Hindi)
        - ⚡ Smart caching for faster generation
        - 📊 Usage analytics
        - 🎛️ Full customization options
        
        **Tech Stack:**
        - Groq Llama for script generation
        - Edge-TTS for voice synthesis
        - Streamlit for UI
        """)


# 5. Main Application Logic
if uploaded_file:
    # --- PHASE 1: PROCESSING (Ingestion) ---
    if 'processed_file' not in st.session_state or st.session_state['processed_file'] != uploaded_file.name:
        with st.spinner("🧠 Reading & Analyzing Document..."):
            data = process_pdf(uploaded_file)
            
            if data:
                # Store results in session state
                st.session_state['processed_file'] = uploaded_file.name
                st.session_state['pdf_text'] = data['text']
                st.session_state['word_count'] = data['word_count']
                st.session_state['est_time'] = data['est_reading_time']
                
                # Record analytics
                if enable_analytics:
                    record_file_processing(uploaded_file.name, data['word_count'])
                
                # Clear old script if new file uploaded
                if 'script' in st.session_state:
                    del st.session_state['script']
                if 'audio_file' in st.session_state:
                    del st.session_state['audio_file']
                    
                st.success("✅ Document processed successfully!")

    # --- PHASE 2: DASHBOARD (Metrics) ---
    if 'pdf_text' in st.session_state:
        # Display Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Source File", uploaded_file.name[:15]+"...")
        with col2:
            st.metric("Word Count", f"{st.session_state['word_count']:,}")
        with col3:
            st.metric("Est. Reading Time", f"{st.session_state['est_time']} min")
        with col4:
            st.metric("Language", language)

        # Content Preview (Collapsible)
        with st.expander("📄 View Extracted Text Source"):
            st.markdown(st.session_state['pdf_text'][:5000] + "...") # Show first 5k chars

        st.markdown("---")

        # --- PHASE 3: GENERATION (The Brain) ---
        col_gen1, col_gen2 = st.columns([3, 1])
        
        with col_gen1:
            if st.button("🎙️ Generate Podcast Script", type="primary", use_container_width=True):
                # Check cache first
                text_hash = hash_text(st.session_state['pdf_text'])
                cache_key = get_cache_key(text_hash, speaker1_name, speaker2_name, tone)
                
                cached_script = None
                if enable_cache:
                    cached_script = get_from_cache(cache_key)
                    if cached_script:
                        st.info("♻️ Using cached script from previous generation")
                
                if cached_script:
                    st.session_state['script'] = cached_script
                    if 'audio_file' in st.session_state:
                        del st.session_state['audio_file']
                    st.success("✅ Script loaded from cache!")
                else:
                    with st.spinner(f"🤖 Drafting the Script with {selected_model}..."):
                        script_data = generate_script(
                            st.session_state['pdf_text'],
                            model=selected_model,
                            tone=tone,
                            speaker1=speaker1_name,
                            speaker2=speaker2_name
                        )
                        
                        if script_data:
                            st.session_state['script'] = script_data
                            
                            # Save to cache
                            if enable_cache:
                                save_to_cache(script_data, cache_key, {
                                    "tone": tone,
                                    "model": selected_model,
                                    "speakers": [speaker1_name, speaker2_name]
                                })
                            
                            # Record analytics
                            if enable_analytics:
                                record_script_generation(selected_model, tone, speaker1_name, speaker2_name)
                            
                            if 'audio_file' in st.session_state:
                                del st.session_state['audio_file']
                            st.success("✅ Script generated successfully!")
                        else:
                            st.error("❌ Failed to generate script. Check API key and retry.")
        
        with col_gen2:
            st.markdown("")
            st.markdown("")
            if st.button("📥 Export Settings", use_container_width=True):
                settings_json = {
                    "file": uploaded_file.name,
                    "model": selected_model,
                    "tone": tone,
                    "language": language,
                    "speakers": [speaker1_name, speaker2_name],
                    "pacing": pacing,
                    "timestamp": datetime.now().isoformat()
                }
                st.download_button(
                    label="Download Settings",
                    data=json.dumps(settings_json, indent=2),
                    file_name=f"audiolearn_settings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

    # --- PHASE 4: DISPLAY (The Script UI) ---
    if 'script' in st.session_state:
        st.subheader("📝 Script Preview")
        st.markdown(f"*({speaker1_name} and {speaker2_name} are discussing your document)*")
        
        # Export Script Option
        col_export1, col_export2 = st.columns(2)
        with col_export1:
            script_json = json.dumps(st.session_state['script'], indent=2)
            st.download_button(
                label="📥 Export as JSON",
                data=script_json,
                file_name=f"audiolearn_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col_export2:
            # Convert script to readable text
            script_text = "\n\n".join([
                f"{line['speaker']}:\n{line['text']}"
                for line in st.session_state['script']
            ])
            st.download_button(
                label="📄 Export as TXT",
                data=script_text,
                file_name=f"audiolearn_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        st.markdown("---")
        
        # Display dialogue
        container = st.container()
        with container:
            for line in st.session_state['script']:
                # Dynamic avatars based on speaker
                speaker = line["speaker"]
                
                if speaker == speaker1_name:
                    avatar_icon = "🧑‍💻"
                    role = f"{speaker1_name} (Host)"
                else:
                    avatar_icon = "👩‍🔬"
                    role = f"{speaker2_name} (Expert)"
                
                # Render Chat Message
                with st.chat_message(role, avatar=avatar_icon):
                    st.write(line["text"])

        # --- PHASE 5: AUDIO GENERATION (The Voice) ---
        st.markdown("---")
        st.subheader("🎧 Generate & Listen to Podcast")
        
        # Check if audio exists
        if 'audio_file' in st.session_state and os.path.exists(st.session_state['audio_file']):
            st.success("✅ Audio is ready!")
            
            # Play audio
            with open(st.session_state['audio_file'], "rb") as audio_data:
                audio_bytes = audio_data.read()
                st.audio(audio_bytes, format='audio/mp3')
            
            # Download Button
            st.download_button(
                label="⬇️ Download Podcast MP3",
                data=audio_bytes,
                file_name=f"audiolearn_{uploaded_file.name.replace('.pdf', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                mime="audio/mp3",
                use_container_width=True
            )
        else:
            # Generate Audio Button
            if st.button("▶️ Generate Audio with Voices", type="primary", use_container_width=True):
                try:
                    with st.spinner(f"🔊 Recording Audio with {language} voices... ({speaker1_name} & {speaker2_name} are speaking)"):
                        audio_file = create_podcast_audio(
                            st.session_state['script'],
                            language=language,
                            pacing=pacing,
                            silence_duration=silence_duration,
                            custom_speakers={
                                speaker1_name: VOICE_MAPPING[language].get(speaker1_name, list(VOICE_MAPPING[language].values())[0]),
                                speaker2_name: VOICE_MAPPING[language].get(speaker2_name, list(VOICE_MAPPING[language].values())[1] if len(VOICE_MAPPING[language]) > 1 else list(VOICE_MAPPING[language].values())[0])
                            }
                        )
                        
                        if audio_file and os.path.exists(audio_file):
                            # Store in session state
                            st.session_state['audio_file'] = audio_file
                            
                            # Record analytics
                            if enable_analytics:
                                record_audio_generation(0)  # Duration tracking could be added
                            
                            st.success("✅ Audio Generated Successfully!")
                            
                            # Play audio
                            with open(audio_file, "rb") as audio_data:
                                audio_bytes = audio_data.read()
                                st.audio(audio_bytes, format='audio/mp3')
                            
                            # Download Button
                            st.download_button(
                                label="⬇️ Download Podcast MP3",
                                data=audio_bytes,
                                file_name=f"audiolearn_{uploaded_file.name.replace('.pdf', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                                mime="audio/mp3",
                                use_container_width=True
                            )
                            
                        else:
                            st.error("❌ Failed to generate audio. Please check:")
                            st.markdown("""
                            - **FFmpeg is installed** (required by pydub)
                                - Mac: `brew install ffmpeg`
                                - Windows: Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
                            - Your script has valid content
                            - Check console for detailed error messages
                            """)
                            
                except ImportError as e:
                    st.error(f"❌ Missing dependency: {e}")
                    st.info("Install required packages: `pip install edge-tts pydub nest-asyncio`")
                except Exception as e:
                    st.error(f"❌ Error generating audio: {str(e)[:200]}")
                    st.info("Check the console for detailed error logs.")

else:
    # Empty State (Welcome Screen)
    st.info("👈 Please upload a PDF from the sidebar to get started!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### How it works:
        1. **Upload** a research paper, resume, or textbook chapter.
        2. **Wait** for AI to analyze the content.
        3. **Customize** tone, language, and speaker names.
        4. **Generate** a natural dialogue script.
        5. **Listen** to AI-generated podcast!
        """)
    
    with col2:
        st.markdown("""
        ### Key Features:
        - 🎙️ Natural conversational scripts
        - 🌍 Multi-language voices
        - 🎛️ Full customization options
        - ⚡ Smart caching system
        - 📊 Usage analytics
        - 📥 Export as JSON/TXT
        - 💾 Download MP3 podcasts
        
        ### Powered By:
        - Groq Llama for Script Generation
        - Azure Text-to-Speech
        - Streamlit for UI
        """)