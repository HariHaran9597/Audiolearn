import streamlit as st
import json
from datetime import datetime

def generate_podcast_metadata(filename, script_data, settings):
    """
    Generates comprehensive metadata for the podcast.
    """
    metadata = {
        "podcast_info": {
            "title": f"AudioLearn: {filename.replace('.pdf', '')}",
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        },
        "source": {
            "filename": filename,
            "word_count": settings.get("word_count", 0),
            "reading_time_minutes": settings.get("reading_time", 0)
        },
        "generation_settings": {
            "model": settings.get("model", "unknown"),
            "tone": settings.get("tone", "Fun & Casual"),
            "language": settings.get("language", "English"),
            "speakers": settings.get("speakers", ["Siddharth", "Aditi"]),
            "pacing": settings.get("pacing", "Normal (100%)"),
            "silence_between_speakers_ms": settings.get("silence", 300)
        },
        "script_summary": {
            "total_lines": len(script_data),
            "estimated_duration_minutes": len(script_data) * 0.3,  # Rough estimate
            "speakers_in_script": list(set([line.get("speaker") for line in script_data]))
        }
    }
    return metadata

def generate_podcast_stats(script_data):
    """
    Generates detailed statistics about the podcast script.
    """
    speaker_stats = {}
    total_characters = 0
    
    for line in script_data:
        speaker = line.get("speaker", "Unknown")
        text = line.get("text", "")
        
        total_characters += len(text)
        
        if speaker not in speaker_stats:
            speaker_stats[speaker] = {
                "lines_spoken": 0,
                "total_characters": 0,
                "avg_line_length": 0
            }
        
        speaker_stats[speaker]["lines_spoken"] += 1
        speaker_stats[speaker]["total_characters"] += len(text)
    
    # Calculate averages
    for speaker in speaker_stats:
        lines = speaker_stats[speaker]["lines_spoken"]
        speaker_stats[speaker]["avg_line_length"] = (
            speaker_stats[speaker]["total_characters"] // lines if lines > 0 else 0
        )
    
    return {
        "total_lines": len(script_data),
        "total_characters": total_characters,
        "speaker_breakdown": speaker_stats
    }

def display_script_analysis(script_data):
    """
    Displays detailed analysis of the generated script in Streamlit.
    """
    stats = generate_podcast_stats(script_data)
    
    st.markdown("### 📊 Script Analysis")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Lines", stats["total_lines"])
    with col2:
        st.metric("Total Characters", f"{stats['total_characters']:,}")
    with col3:
        est_minutes = stats["total_characters"] / 600  # ~600 chars per minute of speech
        st.metric("Est. Duration", f"{est_minutes:.1f} min")
    
    # Speaker breakdown
    st.markdown("#### Speaker Breakdown")
    for speaker, data in stats["speaker_breakdown"].items():
        with st.expander(f"🎤 {speaker}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Lines Spoken", data["lines_spoken"])
            with col2:
                st.metric("Total Characters", f"{data['total_characters']:,}")
            with col3:
                st.metric("Avg. Line Length", data["avg_line_length"])

def create_srt_subtitles(script_data, avg_chars_per_second=15):
    """
    Generates SRT subtitle format from script.
    SRT format is compatible with most video players.
    """
    srt_content = []
    current_time = 0
    
    for index, line in enumerate(script_data, 1):
        speaker = line.get("speaker", "")
        text = line.get("text", "")
        
        if not text.strip():
            continue
        
        # Estimate duration based on character count
        duration = len(text) / avg_chars_per_second
        
        start_time = int(current_time)
        end_time = int(current_time + duration)
        
        start_ms = (start_time % 60) * 1000
        start_sec = start_time % 60
        start_min = (start_time // 60) % 60
        start_hour = start_time // 3600
        
        end_ms = (end_time % 60) * 1000
        end_sec = end_time % 60
        end_min = (end_time // 60) % 60
        end_hour = end_time // 3600
        
        srt_content.append(f"{index}")
        srt_content.append(f"{start_hour:02d}:{start_min:02d}:{start_sec:02d},000 --> {end_hour:02d}:{end_min:02d}:{end_sec:02d},000")
        srt_content.append(f"{speaker}: {text}")
        srt_content.append("")
        
        current_time += duration
    
    return "\n".join(srt_content)

def create_transcript(script_data):
    """
    Creates a readable transcript of the podcast.
    """
    transcript = []
    for line in script_data:
        speaker = line.get("speaker", "Unknown")
        text = line.get("text", "")
        transcript.append(f"{speaker}: {text}\n")
    
    return "\n".join(transcript)
