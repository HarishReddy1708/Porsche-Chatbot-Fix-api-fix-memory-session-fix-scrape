import os
import sys
import logging
import time


# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from utils.scraper import scrape_porsche_model
from utils.storage import save_specs, ensure_data_dir
from utils.data import porsche_models1
from utils.specifications import ALL_SPECS


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_all_models():
    """
    Scrape specifications for all Porsche models and save them
    """
    ensure_data_dir()

    total_models = len(porsche_models1)
    for index, model in enumerate(porsche_models1, 1):
        logger.info(f"Scraping model {index}/{total_models}: {model}")

        # Scrape each specification
        for spec in ALL_SPECS:
            try:
                # Add delay to avoid overwhelming the server
                time.sleep(2)

                # Scrape the data
                result = scrape_porsche_model(model, spec)

                if result["reference_text"]:
                    # Save the data
                    save_specs(model, result, spec)
                    logger.info(f"Saved {spec} for {model}")
                else:
                    logger.warning(f"No data found for {spec} on {model}")

            except Exception as e:
                logger.error(f"Error scraping {spec} for {model}: {str(e)}")
                continue

        # Add a longer delay between models
        time.sleep(5)

    logger.info("Finished scraping all models")


if __name__ == "__main__":
    logger.info("Starting to scrape all Porsche models...")
    scrape_all_models()
