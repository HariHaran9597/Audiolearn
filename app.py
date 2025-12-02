import streamlit as st
import os
from src.processing import process_pdf
from src.generation import generate_script

# 1. Page Configuration
st.set_page_config(
    page_title="AudioLearn",
    page_icon="🎧",
    layout="wide"
)

# 2. Custom CSS for a "Spotify-like" feel (Optional polish)
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #1DB954;
        color: white;
        border-radius: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Header
st.title("🎧 AudioLearn")
st.caption("Turn any PDF into an Engaging Podcast using Groq Llama 3 & EdgeTTS")

# 4. Sidebar: Data Ingestion
with st.sidebar:
    st.header("📂 Data Source")
    uploaded_file = st.file_uploader("Upload a PDF Document", type=["pdf"])
    
    st.markdown("---")
    st.markdown("### 🛠️ Settings")
    tone = st.selectbox("Podcast Tone", ["Fun & Casual", "Formal & Educational", "Debate Style"])

# 5. Main Application Logic
if uploaded_file:
    # --- PHASE 1: PROCESSING (Ingestion) ---
    # We use session_state to prevent re-processing on every interaction
    if 'processed_file' not in st.session_state or st.session_state['processed_file'] != uploaded_file.name:
        with st.spinner("🧠 Reading & Analyzing Document..."):
            data = process_pdf(uploaded_file)
            
            if data:
                # Store results in session state
                st.session_state['processed_file'] = uploaded_file.name
                st.session_state['pdf_text'] = data['text']
                st.session_state['word_count'] = data['word_count']
                st.session_state['est_time'] = data['est_reading_time']
                
                # Clear old script if a new file is uploaded
                if 'script' in st.session_state:
                    del st.session_state['script']
                if 'audio_file' in st.session_state:
                    del st.session_state['audio_file']
                    
                st.success("Document processed successfully!")

    # --- PHASE 2: DASHBOARD (Metrics) ---
    if 'pdf_text' in st.session_state:
        # Display Metrics Row
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Source File", uploaded_file.name[:20]+"...")
        with col2:
            st.metric("Word Count", f"{st.session_state['word_count']:,}")
        with col3:
            st.metric("Est. Reading Time", f"{st.session_state['est_time']} min")

        # Content Preview (Collapsible)
        with st.expander("📄 View Extracted Text Source"):
            st.markdown(st.session_state['pdf_text'][:5000] + "...") # Show first 5k chars

        st.markdown("---")

        # --- PHASE 3: GENERATION (The Brain) ---
        if st.button("🎙️ Generate Podcast Script", type="primary"):
            with st.spinner("🤖 Drafting the Script with Groq (Llama 3)..."):
                # Call the Groq generation function
                script_data = generate_script(st.session_state['pdf_text'])
                
                if script_data:
                    st.session_state['script'] = script_data
                    # Clear old audio when new script is generated
                    if 'audio_file' in st.session_state:
                        del st.session_state['audio_file']
                    st.success("Script generated!")
                else:
                    st.error("Failed to generate script. Please check your API key.")

    # --- PHASE 4: DISPLAY (The Script UI) ---
    if 'script' in st.session_state:
        st.subheader("📝 Script Preview")
        st.markdown("*(Siddharth and Aditi are discussing your document)*")
        
        container = st.container()
        with container:
            for line in st.session_state['script']:
                # Dynamic avatars based on speaker
                if line["speaker"] == "Siddharth":
                    avatar_icon = "🧑‍💻" # Male Techie
                    role = "Siddharth (Host)"
                else:
                    avatar_icon = "👩‍🔬" # Female Expert
                    role = "Aditi (Expert)"
                
                # Render Chat Message
                with st.chat_message(role, avatar=avatar_icon):
                    st.write(line["text"])

        # --- PHASE 5: AUDIO GENERATION (The Voice) ---
        st.markdown("---")
        st.subheader("🎧 Listen to Podcast")
        
        # Check if audio already exists in session
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
                file_name=f"audiolearn_{uploaded_file.name.replace('.pdf', '')}.mp3",
                mime="audio/mp3"
            )
        else:
            # Generate Audio Button
            if st.button("▶️ Generate Audio (Indian Voices)", type="primary"):
                try:
                    from src.tts import create_podcast_audio
                    
                    with st.spinner("🔊 Recording Audio... (Siddharth & Aditi are speaking)"):
                        audio_file = create_podcast_audio(st.session_state['script'])
                        
                        if audio_file and os.path.exists(audio_file):
                            # Store in session state
                            st.session_state['audio_file'] = audio_file
                            
                            st.success("✅ Audio Generated Successfully!")
                            
                            # Play audio in Streamlit
                            with open(audio_file, "rb") as audio_data:
                                audio_bytes = audio_data.read()
                                st.audio(audio_bytes, format='audio/mp3')
                            
                            # Download Button
                            st.download_button(
                                label="⬇️ Download Podcast MP3",
                                data=audio_bytes,
                                file_name=f"audiolearn_{uploaded_file.name.replace('.pdf', '')}.mp3",
                                mime="audio/mp3"
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
                    st.error(f"❌ Error generating audio: {e}")
                    st.info("Check the console for detailed error logs.")

else:
    # Empty State (Welcome Screen)
    st.info("👈 Please upload a PDF from the sidebar to get started!")
    st.markdown("""
    ### How it works:
    1. **Upload** a research paper, resume, or textbook chapter.
    2. **Wait** for the AI to analyze the content.
    3. **Click Generate** to create a natural dialogue script.
    4. **Listen** to the AI-generated podcast with Indian voices!
    
    ### Features:
    - 🎙️ Natural conversational script generation
    - 🗣️ Indian English voices (Siddharth & Aditi)
    - 💾 Download your podcast as MP3
    - 🎯 Powered by Groq Llama 3 & EdgeTTS
    """)