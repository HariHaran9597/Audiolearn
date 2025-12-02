import os
import json
import hashlib
from datetime import datetime, timedelta

CACHE_DIR = ".audiolearn_cache"

def ensure_cache_dir():
    """Create cache directory if it doesn't exist."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def get_cache_key(text_hash, speaker1, speaker2, tone):
    """Generate a unique cache key based on input parameters."""
    combined = f"{text_hash}_{speaker1}_{speaker2}_{tone}"
    return hashlib.md5(combined.encode()).hexdigest()

def hash_text(text):
    """Generate MD5 hash of text content."""
    return hashlib.md5(text[:10000].encode()).hexdigest()  # Use first 10k chars

def save_to_cache(script_data, cache_key, metadata=None):
    """Save generated script to cache."""
    ensure_cache_dir()
    cache_path = os.path.join(CACHE_DIR, f"{cache_key}.json")
    
    cache_entry = {
        "script": script_data,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    
    try:
        with open(cache_path, 'w') as f:
            json.dump(cache_entry, f, indent=2)
        return True
    except Exception as e:
        print(f"Cache save error: {e}")
        return False

def get_from_cache(cache_key, max_age_days=7):
    """Retrieve script from cache if it exists and is fresh."""
    cache_path = os.path.join(CACHE_DIR, f"{cache_key}.json")
    
    if not os.path.exists(cache_path):
        return None
    
    try:
        with open(cache_path, 'r') as f:
            cache_entry = json.load(f)
        
        timestamp = datetime.fromisoformat(cache_entry["timestamp"])
        if datetime.now() - timestamp > timedelta(days=max_age_days):
            return None
        
        return cache_entry["script"]
    except Exception as e:
        print(f"Cache retrieval error: {e}")
        return None

def clear_cache():
    """Clear all cached files."""
    if os.path.exists(CACHE_DIR):
        import shutil
        shutil.rmtree(CACHE_DIR)
        ensure_cache_dir()

def cleanup_old_cache(days=7):
    """Remove cache entries older than specified days."""
    ensure_cache_dir()
    cutoff_time = datetime.now() - timedelta(days=days)
    
    for filename in os.listdir(CACHE_DIR):
        filepath = os.path.join(CACHE_DIR, filename)
        try:
            with open(filepath, 'r') as f:
                cache_entry = json.load(f)
            timestamp = datetime.fromisoformat(cache_entry["timestamp"])
            if timestamp < cutoff_time:
                os.remove(filepath)
        except Exception as e:
            print(f"Cache cleanup error for {filename}: {e}")
