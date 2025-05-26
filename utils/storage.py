import json
import os
import logging
from datetime import datetime
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory to store the data
DATA_DIR = "data"
SPECS_FILE = os.path.join(DATA_DIR, "porsche_specs.json")
CACHE_FILE = os.path.join(DATA_DIR, "specs_cache.json")

def ensure_data_dir():
    """Ensure the data directory exists"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def save_specs(model_name: str, specs_data: Dict[str, str], query: str = ""):
    """
    Save scraped specifications for a Porsche model
    
    Args:
        model_name: Name of the Porsche model
        specs_data: Dictionary containing reference_text and source_links
        query: The original query that was used to get these specs
    """
    try:
        ensure_data_dir()
        
        # Load existing data
        existing_data = load_all_specs()
        
        # Create timestamp
        timestamp = datetime.now().isoformat()
        
        # Prepare the new entry
        new_entry = {
            "model": model_name,
            "query": query,
            "specs": specs_data["reference_text"],
            "source_links": specs_data["source_links"],
            "timestamp": timestamp
        }
        
        # Add to existing data
        if model_name not in existing_data:
            existing_data[model_name] = []
        existing_data[model_name].append(new_entry)
        
        # Save back to file
        with open(SPECS_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Saved specs for {model_name}")
        
    except Exception as e:
        logger.error(f"Error saving specs: {str(e)}")

def load_all_specs() -> Dict:
    """Load all saved specifications"""
    try:
        if os.path.exists(SPECS_FILE):
            with open(SPECS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading specs: {str(e)}")
        return {}

def get_latest_specs(model_name: str, query: str = "") -> Optional[Dict]:
    """
    Get the latest specifications for a model
    
    Args:
        model_name: Name of the Porsche model
        query: Optional query to filter specifications
        
    Returns:
        Dictionary containing the latest specs or None if not found
    """
    try:
        all_specs = load_all_specs()
        
        if model_name not in all_specs:
            return None
            
        # Get all entries for this model
        model_entries = all_specs[model_name]
        
        # Filter by query if provided
        if query:
            filtered_entries = [
                entry for entry in model_entries 
                if query.lower() in entry["query"].lower()
            ]
            if filtered_entries:
                model_entries = filtered_entries
        
        if not model_entries:
            return None
            
        # Get the latest entry
        latest_entry = max(model_entries, key=lambda x: x["timestamp"])
        
        return {
            "reference_text": latest_entry["specs"],
            "source_links": latest_entry["source_links"]
        }
        
    except Exception as e:
        logger.error(f"Error getting latest specs: {str(e)}")
        return None

def clear_old_specs(days_to_keep: int = 7):
    """
    Clear specifications older than the specified number of days
    
    Args:
        days_to_keep: Number of days of data to keep
    """
    try:
        all_specs = load_all_specs()
        current_time = datetime.now()
        
        for model in list(all_specs.keys()):
            # Filter out old entries
            all_specs[model] = [
                entry for entry in all_specs[model]
                if (current_time - datetime.fromisoformat(entry["timestamp"])).days <= days_to_keep
            ]
            
            # Remove model if no entries left
            if not all_specs[model]:
                del all_specs[model]
        
        # Save back to file
        with open(SPECS_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_specs, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Cleared specs older than {days_to_keep} days")
        
    except Exception as e:
        logger.error(f"Error clearing old specs: {str(e)}") 