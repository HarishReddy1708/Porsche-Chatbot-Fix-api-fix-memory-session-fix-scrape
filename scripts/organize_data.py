import json
import os
import logging
from datetime import datetime
from utils.data import porsche_models
from utils.scraper import scrape_porsche_model
from utils.specifications import ALL_SPECS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create data directory if it doesn't exist
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def organize_data():
    """Organize scraped data into the data folder"""
    specs_data = {}
    
    for model in porsche_models:
        logger.info(f"Processing {model}...")
        specs_data[model] = []
        
        for query in ALL_SPECS:
            try:
                # Scrape data for this model and query
                result = scrape_porsche_model(f"{model} {query}")
                
                if result and result.get('reference_text'):
                    # Add entry to the data
                    specs_data[model].append({
                        "query": query,
                        "specs": result['reference_text'],
                        "source_links": result.get('source_links', []),
                        "timestamp": datetime.now().isoformat()
                    })
                    logger.info(f"Added data for {model} - {query}")
                else:
                    logger.warning(f"No data found for {model} - {query}")
                    
            except Exception as e:
                logger.error(f"Error processing {model} - {query}: {str(e)}")
                continue
    
    # Save the organized data
    output_file = os.path.join(DATA_DIR, "porsche_specs.json")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(specs_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Data saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving data: {str(e)}")

if __name__ == "__main__":
    organize_data() 