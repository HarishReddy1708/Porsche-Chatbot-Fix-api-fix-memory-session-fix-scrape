from utils.scraper import scrape_porsche_model
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_911_carrera_horsepower():
    model = "911 carrera"
    query = "horsepower"
    result = scrape_porsche_model(model, query)
    
    print("\nScraping Results:")
    print("----------------")
    print(f"Model: {model}")
    print(f"Query: {query}")
    print(f"Reference Text: {result['reference_text']}")
    print(f"Source Link: {result['source_links'][0] if result['source_links'] else 'No link'}")

if __name__ == "__main__":
    test_911_carrera_horsepower() 