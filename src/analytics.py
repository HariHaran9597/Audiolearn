import os
import json
from datetime import datetime

ANALYTICS_FILE = ".audiolearn_analytics.json"

def load_analytics():
    """Load analytics data from file."""
    if not os.path.exists(ANALYTICS_FILE):
        return {"total_files": 0, "total_scripts": 0, "total_audio": 0, "history": []}
    
    try:
        with open(ANALYTICS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {"total_files": 0, "total_scripts": 0, "total_audio": 0, "history": []}

def save_analytics(analytics):
    """Save analytics data to file."""
    try:
        with open(ANALYTICS_FILE, 'w') as f:
            json.dump(analytics, f, indent=2)
    except Exception as e:
        print(f"Analytics save error: {e}")

def record_file_processing(filename, word_count):
    """Record a file processing event."""
    analytics = load_analytics()
    analytics["total_files"] += 1
    analytics["history"].append({
        "type": "file_processed",
        "filename": filename,
        "word_count": word_count,
        "timestamp": datetime.now().isoformat()
    })
    # Keep only last 100 entries
    if len(analytics["history"]) > 100:
        analytics["history"] = analytics["history"][-100:]
    save_analytics(analytics)

def record_script_generation(model, tone, speaker1, speaker2):
    """Record a script generation event."""
    analytics = load_analytics()
    analytics["total_scripts"] += 1
    analytics["history"].append({
        "type": "script_generated",
        "model": model,
        "tone": tone,
        "speakers": [speaker1, speaker2],
        "timestamp": datetime.now().isoformat()
    })
    if len(analytics["history"]) > 100:
        analytics["history"] = analytics["history"][-100:]
    save_analytics(analytics)

def record_audio_generation(duration_seconds):
    """Record an audio generation event."""
    analytics = load_analytics()
    analytics["total_audio"] += 1
    analytics["history"].append({
        "type": "audio_generated",
        "duration": duration_seconds,
        "timestamp": datetime.now().isoformat()
    })
    if len(analytics["history"]) > 100:
        analytics["history"] = analytics["history"][-100:]
    save_analytics(analytics)

def get_stats():
    """Get current statistics."""
    analytics = load_analytics()
    return {
        "total_files_processed": analytics["total_files"],
        "total_scripts_generated": analytics["total_scripts"],
        "total_audio_files": analytics["total_audio"],
        "recent_history": analytics["history"][-5:]
    }

def clear_analytics():
    """Clear all analytics data."""
    save_analytics({"total_files": 0, "total_scripts": 0, "total_audio": 0, "history": []})
