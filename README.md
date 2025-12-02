# 🎧 AudioLearn - PDF to Podcast Generator

Transform academic PDFs and documents into engaging, natural-sounding podcast conversations using AI.

## ✨ Features

### Core Features
- **🎙️ Multi-Speaker Dialogue** - Generate natural conversations between customizable speakers
- **🤖 Multiple AI Models** - Choose between Groq's Mixtral, Llama 2, and Llama 3.1 models
- **🌍 Multi-Language Support** - Generate podcasts in English and Hindi with authentic regional voices
- **🎛️ Full Customization** - Adjust tone, pacing, speaker names, and silence duration
- **📊 Advanced Analytics** - Track your usage and generation statistics
- **⚡ Smart Caching** - Intelligently cache generated scripts for faster generation on similar content
- **📥 Multiple Export Formats** - Export scripts as JSON, TXT, and generate SRT subtitles

### Advanced Features
- **Exponential Backoff Retry Logic** - Automatic retries with intelligent backoff for API failures
- **Session State Management** - Prevent re-processing and efficient caching
- **Progress Tracking** - Real-time progress indicators during generation
- **Metadata Export** - Download comprehensive podcast metadata
- **Script Analysis** - Detailed breakdowns of speaker contributions and content metrics

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- FFmpeg (required for audio processing)
  - **Windows**: Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
  - **Mac**: `brew install ffmpeg`
  - **Linux**: `sudo apt-get install ffmpeg`

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/HariHaran9597/AudioLearn.git
cd AudioLearn
```

2. **Create a virtual environment**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install system dependencies**
```bash
# The packages.txt file lists system dependencies
# On Windows with WSL or Linux:
xargs apt-get install -y < packages.txt
```

5. **Set up environment variables**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Groq API key
# Get your API key from: https://console.groq.com
```

### Running the Application

```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`

## 📖 How to Use

### Step 1: Upload PDF
- Click the file uploader in the sidebar
- Select any PDF document (research papers, textbooks, resumes, etc.)
- The app automatically extracts and analyzes the content

### Step 2: Configure Settings
- **Choose AI Model**: Select your preferred Groq model (affects quality and speed)
- **Set Tone**: Pick between Fun & Casual, Formal & Educational, or Debate Style
- **Select Language**: Choose English or Hindi for voice synthesis
- **Customize Speakers**: Enter custom names for your podcast hosts
- **Adjust Audio Settings**:
  - Speech Pacing (Slow/Normal/Fast/Very Fast)
  - Silence between speakers
  - Voice selection per speaker

### Step 3: Generate Script
- Click "Generate Podcast Script"
- The AI creates a 5-minute dialogue conversation
- Scripts are automatically cached for future use on similar content

### Step 4: Generate Audio
- Review the generated script
- Click "Generate Audio with Voices"
- The app synthesizes speech in your chosen language
- Listen to the preview or download the MP3

### Step 5: Export
- **Export Script**: Download as JSON or TXT
- **Export Metadata**: Save generation settings and statistics
- **Download Audio**: MP3 with your podcast

## ⚙️ Configuration

### Environment Variables (.env)
```ini
# Required
GROQ_API_KEY=your_api_key_here

# Optional
GROQ_MODEL=mixtral-8x7b-32768
ENABLE_CACHING=true
ENABLE_ANALYTICS=true
MAX_RETRIES=3
RETRY_DELAY=2
```

### Available Models
- `mixtral-8x7b-32768` - Balanced quality and speed
- `llama2-70b-4096` - Good quality, slower
- `llama-3.1-70b-versatile` - Latest, high quality

### Supported Languages & Voices

**English (en-IN)**
- Siddharth: PrabhatNeural (Male)
- Aditi: NeerjaNeural (Female)
- Alternatives: AmitNeural, GunjanNeural

**Hindi (hi-IN)**
- Siddharth: MadhurNeural (Male)
- Aditi: SwaraNeural (Female)
- Alternatives: BharatNeural, KavyaNeural

## 🗂️ Project Structure

```
AudioLearn/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── packages.txt          # System dependencies (ffmpeg)
├── .env.example          # Environment template
├── .gitignore            # Git ignore patterns
└── src/
    ├── __init__.py
    ├── processing.py     # PDF extraction using pymupdf4llm
    ├── generation.py     # Script generation with Groq API
    ├── tts.py            # Text-to-speech synthesis with Edge-TTS
    ├── cache.py          # Script caching system
    ├── analytics.py      # Usage tracking and statistics
    └── utils.py          # Utility functions and metadata generation
```

## 🔧 Advanced Usage

### Using Different Models
```python
from src.generation import generate_script

script = generate_script(
    text_content,
    model="llama-3.1-70b-versatile",
    tone="Formal & Educational",
    speaker1="Dr. Smith",
    speaker2="Professor Jones"
)
```

### Custom Language Voices
```python
from src.tts import create_podcast_audio

audio_file = create_podcast_audio(
    script_data,
    language="Hindi",
    pacing="Slow (75%)",
    custom_speakers={
        "Dr. Smith": "hi-IN-MadhurNeural",
        "Professor Jones": "hi-IN-SwaraNeural"
    }
)
```

### Cache Management
```python
from src.cache import cleanup_old_cache, clear_cache

# Remove cached scripts older than 7 days
cleanup_old_cache(days=7)

# Clear all cache
clear_cache()
```

## 📊 Analytics

The app tracks:
- Total files processed
- Total scripts generated
- Total audio files created
- Recent generation history

Access analytics through the sidebar when enabled.

## 🐛 Troubleshooting

### "FFmpeg is not installed"
- Install FFmpeg from the links above
- Verify installation: `ffmpeg -version`

### API Key errors
- Ensure your GROQ_API_KEY is in `.env`
- Get a key from https://console.groq.com
- Check that the key has valid credits

### Script generation times out
- This can happen with very large documents
- Try splitting the PDF or using a faster model
- Check your internet connection

### Audio generation fails
- Verify FFmpeg is installed
- Check that Edge-TTS packages are up to date
- Try regenerating with fewer lines or different settings

## 📈 Performance Tips

1. **Use Mixtral Model** - Fastest with good quality
2. **Enable Caching** - Reuses similar scripts automatically
3. **Reduce Silence Duration** - Decreases final file size
4. **Use Fast Pacing** - Generates shorter audio files
5. **Limit Document Size** - Keep PDFs under 50 pages for best results

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙋 Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues first
- Provide detailed error messages and logs

## 🎯 Roadmap

- [ ] Real-time progress streaming
- [ ] Custom voice fine-tuning
- [ ] Batch PDF processing
- [ ] Web-based deployment templates
- [ ] More language support (Spanish, French, etc.)
- [ ] Video generation with subtitles
- [ ] Integration with podcasting platforms

## 👏 Acknowledgments

- **Groq** - Powerful LLM API
- **Microsoft Azure** - Edge-TTS voice synthesis
- **PyMuPDF** - PDF extraction
- **Streamlit** - Web framework

## 📧 Contact

Created by [HariHaran9597](https://github.com/HariHaran9597)

---

**Made with ❤️ for educators and content creators**
