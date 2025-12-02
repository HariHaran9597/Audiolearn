# 🚀 AudioLearn Quick Start Guide

## 5-Minute Setup

### 1. Prerequisites
- Python 3.8+
- FFmpeg
- Git

### 2. Clone & Setup
```bash
git clone https://github.com/HariHaran9597/AudioLearn.git
cd AudioLearn
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Get Your API Key
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up (free account)
3. Copy your API key

### 4. Configure
```bash
# Copy template
cp .env.example .env

# Edit .env and add your API key
# GROQ_API_KEY=your_key_here
```

### 5. Run
```bash
streamlit run app.py
```

Open browser at `http://localhost:8501`

---

## First Podcast - 10 Steps

### Step 1: Upload PDF
Click "Upload a PDF Document" in sidebar → Select any PDF

### Step 2: Wait for Analysis
App shows:
- Word count
- Reading time estimate
- Preview of extracted text

### Step 3: Choose Model
Select from: Mixtral (fast), Llama 2 (quality), Llama 3.1 (latest)

### Step 4: Set Tone
- Fun & Casual
- Formal & Educational
- Debate Style

### Step 5: Pick Language
- English (Indian)
- Hindi

### Step 6: Name Your Speakers
Default: Siddharth & Aditi
Change to your preference

### Step 7: Adjust Audio Settings
- Pacing: Normal (100%) recommended
- Silence: 300ms recommended

### Step 8: Generate Script
Click "Generate Podcast Script" button
Wait for AI to create dialogue (usually 30-60 seconds)

### Step 9: Review & Export
- Read the script preview
- Export as JSON or TXT if desired
- Check "Script Analysis" for metrics

### Step 10: Generate Audio & Download
Click "Generate Audio with Voices"
Wait for audio synthesis (1-2 minutes)
Click download!

---

## Keyboard Shortcuts & Tips

### Streamlit Shortcuts
- `r` - Rerun the app
- `C` - Clear cache (if needed)
- `k` - Open keyboard help

### Pro Tips
1. **Cache Enabled** → Re-upload similar docs = instant generation
2. **Use Mixtral** → Fastest model, great quality
3. **Normal Pacing** → Works best for most content
4. **300ms Silence** → Professional sounding
5. **Export Settings** → Save for reproducibility

---

## Troubleshooting

### "API Key not found"
- Check if `.env` file exists
- Verify you added `GROQ_API_KEY=xxx`
- Restart the app

### "FFmpeg not found"
**Windows:**
1. Download: [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/)
2. Extract and add to PATH
3. Restart PowerShell

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

### "Script Generation Times Out"
- Try with smaller PDF
- Use Mixtral model (faster)
- Check internet connection

### "Audio Generation Fails"
- Ensure FFmpeg is installed
- Try with simpler script
- Check available disk space

---

## File Structure After Setup

```
AudioLearn/
├── app.py
├── .env (created by you)
├── src/
│   ├── processing.py
│   ├── generation.py
│   ├── tts.py
│   ├── cache.py
│   ├── analytics.py
│   └── utils.py
├── .audiolearn_cache/ (auto-created)
├── .audiolearn_analytics.json (auto-created)
└── config.json
```

---

## Next Steps

1. **Explore Settings** → Try different tones and languages
2. **Generate Multiple** → See how caching speeds up generation
3. **Review Analytics** → Check sidebar for usage stats
4. **Export Scripts** → Try JSON and TXT exports
5. **Read FEATURES.md** → Learn about advanced options

---

## Common Workflows

### Academic Paper → Professional Podcast
1. Upload PDF
2. Set tone: "Formal & Educational"
3. Keep default speakers (Siddharth & Aditi)
4. Normal pacing
5. Export as MP3

### Research Summary → Quick Overview
1. Upload PDF (first 20 pages)
2. Set tone: "Fun & Casual"
3. Use Fast pacing (125%)
4. Silence: 200ms
5. Short, snappy dialogue

### Multi-Language Content
1. Upload PDF
2. Generate in English first
3. Then regenerate in Hindi
4. Compare outputs

---

## Getting Help

### Check These First
1. README.md - Complete documentation
2. FEATURES.md - Detailed feature guide
3. config.json - Configuration reference

### If Still Stuck
- Check console for error messages
- Try a different PDF
- Verify FFmpeg: `ffmpeg -version`
- Check API key: Visit console.groq.com

---

## Pro Features to Try

### 1. Script Caching
Upload same PDF twice → 80% faster second time!

### 2. Custom Speaker Names
Change "Siddharth" to "Dr. Smith" → Personalized experience

### 3. Multiple Languages
Generate in English AND Hindi → Wider audience reach

### 4. Different Tones
Same PDF, different tones → Versatile content

### 5. Analytics Tracking
Monitor your usage → Track productivity

---

## Limits & Guidelines

### File Limits
- Max PDF size: ~100 MB
- Optimal: 10-50 pages
- Tested: PDFs up to 200 pages

### API Limits (Groq)
- Rate limited based on your plan
- Free tier: Good for personal use
- Premium tiers: Enterprise features

### Audio Limits
- Depends on script length
- Typical podcast: 5-15 minutes
- File size: 5-20 MB per podcast

---

## Performance Tips

| Setting | For Speed | For Quality |
|---------|-----------|-------------|
| Model | Mixtral | Llama 3.1 |
| Pacing | Fast 125% | Normal 100% |
| Language | English | Hindi |
| Caching | Enable | Enable |
| PDF Pages | < 30 | < 100 |

---

## Common Questions

**Q: Can I change voices?**
A: Yes! Use custom voice selection in advanced settings.

**Q: How long does generation take?**
A: Scripts: 30-60s. Audio: 1-2 minutes depending on length.

**Q: Can I edit the script?**
A: Export as JSON/TXT, edit, then regenerate audio.

**Q: Is my data private?**
A: PDFs are processed but not stored. Scripts are cached locally.

**Q: Can I deploy this?**
A: Yes! See deployment guides in docs (coming soon).

---

## Next Resources

- 📖 Full Guide: [README.md](README.md)
- 🎛️ Advanced Features: [FEATURES.md](FEATURES.md)
- ⚙️ Configuration: [config.json](config.json)
- 🔑 API Setup: [console.groq.com](https://console.groq.com)

---

**Happy Podcast Creating! 🎧**

For issues: [GitHub Issues](https://github.com/HariHaran9597/AudioLearn/issues)
