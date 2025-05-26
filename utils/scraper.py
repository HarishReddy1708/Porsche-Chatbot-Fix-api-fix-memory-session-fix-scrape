import requests
from bs4 import BeautifulSoup
import logging
import re
from typing import Dict, List, Optional
from playwright.sync_api import sync_playwright
import time
from .specifications import ALL_SPECS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_model_url(model_name: str) -> Optional[str]:
    """Convert model name to Porsche.com URL format."""
    model_name = model_name.lower().strip()

    # Map model names to their URL paths
    model_urls = {
        "911 carrera": "https://www.porsche.com/usa/models/911/carrera-models/911-carrera/",
        "911 carrera t": "https://www.porsche.com/usa/models/911/carrera-models/911-carrera-t/",
        "911 carrera s": "https://www.porsche.com/usa/models/911/carrera-models/911-carrera-s/",
        "911 carrera gts": "https://www.porsche.com/usa/models/911/carrera-models/911-carrera-gts/",
        "911 carrera 4 gts": "https://www.porsche.com/usa/models/911/carrera-models/911-carrera-4-gts/",
        "911 carrera cabriolet": "https://www.porsche.com/usa/models/911/carrera-cabriolet-models/911-carrera-cabriolet/",
        "911 carrera t cabriolet": "https://www.porsche.com/usa/models/911/carrera-cabriolet-models/911-carrera-t-cabriolet/",
        "911 carrera s cabriolet": "https://www.porsche.com/usa/models/911/carrera-cabriolet-models/911-carrera-s-cabriolet/",
        "911 carrera gts cabriolet": "https://www.porsche.com/usa/models/911/carrera-cabriolet-models/911-carrera-gts-cabriolet/",
        "911 carrera 4 gts cabriolet": "https://www.porsche.com/usa/models/911/carrera-cabriolet-models/911-carrera-4-gts-cabriolet/",
        "911 targa 4 gts": "https://www.porsche.com/usa/models/911/targa-models/911-targa-4-gts/",
        "911 turbo": "https://www.porsche.com/usa/models/911/911-turbo-models/911-turbo/",
        "911 turbo s": "https://www.porsche.com/usa/models/911/911-turbo-models/911-turbo-s/",
        "911 turbo cabriolet": "https://www.porsche.com/usa/models/911/911-turbo-models/911-turbo-cabriolet/",
        "911 turbo s cabriolet": "https://www.porsche.com/usa/models/911/911-turbo-models/911-turbo-s-cabriolet/",
        "911 gt3": "https://www.porsche.com/usa/models/911/911-gt3-models/911-gt3/",
        "911 gt3 rs": "https://www.porsche.com/usa/models/911/911-gt3-rs/911-gt3-rs/",
        "911 gt3 touring": "https://www.porsche.com/usa/models/911/911-gt3-models/911-gt3-touring/",
        "911 spirit 70": "https://www.porsche.com/usa/models/911/911-spirit-70/911-spirit-70/",
        "911 turbo 50 years": "https://www.porsche.com/usa/models/911/911-turbo-50-years/911-turbo-50-years/",
        "taycan": "https://www.porsche.com/usa/models/taycan/taycan-models/taycan/",
        "taycan 4": "https://www.porsche.com/usa/models/taycan/taycan-models/taycan-4/",
        "taycan 4s": "https://www.porsche.com/usa/models/taycan/taycan-models/taycan-4s/",
        "taycan gts": "https://www.porsche.com/usa/models/taycan/taycan-models/taycan-gts/",
        "taycan turbo": "https://www.porsche.com/usa/models/taycan/taycan-models/taycan-turbo/",
        "taycan turbo s": "https://www.porsche.com/usa/models/taycan/taycan-models/taycan-turbo-s/",
        "taycan turbo gt": "https://www.porsche.com/usa/models/taycan/taycan-models/taycan-turbo-gt/",
        "taycan 4 cross turismo": "https://www.porsche.com/usa/models/taycan/taycan-cross-turismo-models/taycan-4-cross-turismo/",
        "taycan 4s cross turismo": "https://www.porsche.com/usa/models/taycan/taycan-cross-turismo-models/taycan-4s-cross-turismo/",
        "Taycan Turbo Cross Turismo": "https://www.porsche.com/usa/models/taycan/taycan-cross-turismo-models/taycan-turbo-cross-turismo/",
        "Taycan Turbo S Cross Turismo": "https://www.porsche.com/usa/models/taycan/taycan-cross-turismo-models/taycan-turbo-s-cross-turismo/",
        "Taycan gts Sport Turismo": "https://www.porsche.com/usa/models/taycan/taycan-sport-turismo-models/taycan-gts-sport-turismo/",
        "macan": "https://www.porsche.com/usa/models/macan/macan-models/macan/",
        "macan s": "https://www.porsche.com/usa/models/macan/macan-models/macan-s/",
        "macan t": "https://www.porsche.com/usa/models/macan/macan-models/macan-t/",
        "macan gts": "https://www.porsche.com/usa/models/macan/macan-models/macan-gts/",
        "macan electric": "https://www.porsche.com/usa/models/macan/macan-electric-models/macan-electric/",
        "macan 4 electric": "https://www.porsche.com/usa/models/macan/macan-electric-models/macan-4-electric/",
        "macan 4s electric": "https://www.porsche.com/usa/models/macan/macan-electric-models/macan-4s-electric/",
        "Macan turbo electric": "https://www.porsche.com/usa/models/macan/macan-electric-models/macan-turbo-electric/",
        "cayenne": "https://www.porsche.com/usa/models/cayenne/cayenne-models/cayenne/",
        "cayenne e-hybrid": "https://www.porsche.com/usa/models/cayenne/cayenne-models/cayenne-e-hybrid/",
        "cayenne s": "https://www.porsche.com/usa/models/cayenne/cayenne-models/cayenne-s/",
        "cayenne s e-hybrid": "https://www.porsche.com/usa/models/cayenne/cayenne-models/cayenne-s-e-hybrid/",
        "cayenne turbo": "https://www.porsche.com/usa/models/cayenne/cayenne-models/cayenne-turbo/",
        "cayenne gts": "https://www.porsche.com/usa/models/cayenne/cayenne-models/cayenne-gts/",
        "cayenne turbo-e-hybrid": "https://www.porsche.com/usa/models/cayenne/cayenne-models/cayenne-turbo-e-hybrid/",
        "cayenne coupe": "https://www.porsche.com/usa/models/cayenne/cayenne-coupe-models/cayenne-coupe/",
        "cayenne coupe e-hybrid": "https://www.porsche.com/usa/models/cayenne/cayenne-coupe-models/cayenne-coupe-e-hybrid/",
        "cayenne coupe s": "https://www.porsche.com/usa/models/cayenne/cayenne-coupe-models/cayenne-coupe-s/",
        "cayenne coupe s e-hybrid": "https://www.porsche.com/usa/models/cayenne/cayenne-coupe-models/cayenne-coupe-s-e-hybrid/",
        "cayenne coupe gts": "https://www.porsche.com/usa/models/cayenne/cayenne-coupe-models/cayenne-coupe-gts/",
        "cayenne coupe turbo e-hybrid": "https://www.porsche.com/usa/models/cayenne/cayenne-coupe-models/cayenne-coupe-turbo-e-hybrid/",
        "cayenne coupe turbo-gt": "https://www.porsche.com/usa/models/cayenne/cayenne-coupe-models/cayenne-coupe-turbo-gt/",
        "panamera": "https://www.porsche.com/usa/models/panamera/panamera-models/panamera/",
        "panamera 4": "https://www.porsche.com/usa/models/panamera/panamera-models/panamera-4/",
        "panamera 4 e hybrid": "https://www.porsche.com/usa/models/panamera/panamera-models/panamera-4-e-hybrid/",
        "panamera 4s e hybrid": "https://www.porsche.com/usa/models/panamera/panamera-models/panamera-4s-e-hybrid/",
        "panamera turbo": "https://www.porsche.com/usa/models/panamera/panamera-models/panamera-turbo/",
        "panamera turbo s": "https://www.porsche.com/usa/models/panamera/panamera-models/panamera-turbo-s/",
        "panamera turbo s e-hybrid": "https://www.porsche.com/usa/models/panamera/panamera-models/panamera-turbo-s-e-hybrid/",
        "panamera gts": "https://www.porsche.com/usa/models/panamera/panamera-models/panamera-gts/",
        "panamera turbo e-hybrid": "https://www.porsche.com/usa/models/panamera/panamera-models/panamera-turbo-e-hybrid/",
        "718 cayman": "https://www.porsche.com/usa/models/718/718-models/718-cayman/",
        "718 boxster": "https://www.porsche.com/usa/models/718/718-models/718-boxster/",
        "718 cayman style edition": "https://www.porsche.com/usa/models/718/718-models/718-cayman-style-edition/",
        "718 boxster style edition": "https://www.porsche.com/usa/models/718/718-models/718-boxster-style-edition/",
        "718 cayman s": "https://www.porsche.com/usa/models/718/718-models/718-cayman-s/",
        "718 boxster s": "https://www.porsche.com/usa/models/718/718-models/718-boxster-s/",
        "718 cayman gts 4": "https://www.porsche.com/usa/models/718/718-models/718-cayman-gts-4/",
        "718 boxster gts 4": "https://www.porsche.com/usa/models/718/718-models/718-boxster-gts-4/",
        "718 spyder rs": "https://www.porsche.com/usa/models/718/718-spyder-rs/718-spyder-rs/",
        "718 cayman gt4 rs": "https://www.porsche.com/usa/models/718/718-cayman-gt4-rs/718-cayman-gt4-rs/",
        "718 boxster gt4 rs": "https://www.porsche.com/usa/models/718/718-boxster-gt4-rs/718-boxster-gt4-rs/",
    }

    # Try to find exact match first
    if model_name in model_urls:
        return model_urls[model_name]

    # Try to find partial match
    for key in model_urls:
        if key in model_name or model_name in key:
            return model_urls[key]

    return None


def extract_spec_value(page, spec_name: str) -> Optional[str]:
    """Extract a specific specification value from the page."""
    try:
        # Wait for any content to load
        page.wait_for_load_state("networkidle")
        time.sleep(3)  # Give extra time for dynamic content

        # Get all text content from the page
        page_text = page.evaluate("""() => {
            function getTextContent(element) {
                let text = '';
                for (let node of element.childNodes) {
                    if (node.nodeType === 3) { // Text node
                        text += node.textContent;
                    } else if (node.nodeType === 1) { // Element node
                        text += getTextContent(node);
                    }
                }
                return text;
            }
            return getTextContent(document.body);
        }""")

        # Log the page content for debugging
        logger.info(f"Page content: {page_text[:500]}...")

        # Define patterns for different specifications
        spec_patterns = {
            # Performance specs
            "horsepower": [
                r"(\d+)\s*hp\s*Max\.?\s*engine\s*power",
                r"Max\.?\s*engine\s*power\s*(\d+)\s*hp",
                r"(\d+)\s*hp\s*Max\.?\s*power",
                r"Max\.?\s*power\s*(\d+)\s*hp",
                r"(\d+)\s*hp",
            ],
            "0-60 mph": [
                r"(\d\.\d)\s*s\s*0\s*-\s*60\s*mph",
                r"0\s*-\s*60\s*mph\s*(\d\.\d)\s*s",
                r"(\d\.\d)\s*seconds?\s*0\s*-\s*60",
                r"0\s*-\s*60\s*in\s*(\d\.\d)\s*s",
            ],
            "top speed": [
                r"(\d+)\s*mph\s*Top\s*track\s*speed",
                r"Top\s*track\s*speed\s*(\d+)\s*mph",
                r"(\d+)\s*mph\s*Top\s*speed",
                r"Top\s*speed\s*(\d+)\s*mph",
            ],
            "torque": [
                r"(\d+)\s*lb-ft\s*Max\.?\s*engine\s*torque",
                r"Max\.?\s*engine\s*torque\s*(\d+)\s*lb-ft",
                r"(\d+)\s*lb-ft\s*Max\.?\s*torque",
                r"Max\.?\s*torque\s*(\d+)\s*lb-ft",
            ],
            "acceleration": [
                r"(\d\.\d)\s*s\s*0\s*-\s*100\s*km/h",
                r"0\s*-\s*100\s*km/h\s*(\d\.\d)\s*s",
                r"(\d\.\d)\s*s\s*0\s*-\s*100",
                r"0\s*-\s*100\s*in\s*(\d\.\d)\s*s",
            ],
            # Engine specs
            "engine type": [
                r"(\w+\s*\w*)\s*engine\s*type",
                r"engine\s*type:\s*(\w+\s*\w*)",
                r"(\w+\s*\w*)\s*engine",
            ],
            "displacement": [
                r"(\d+\.\d+)\s*L\s*displacement",
                r"displacement\s*(\d+\.\d+)\s*L",
                r"(\d+\.\d+)\s*liter",
            ],
            "cylinders": [r"(\d+)\s*cylinder", r"(\d+)\s*cyl"],
            "bore": [
                r"bore\s*(\d+\.\d+)\s*mm",  # Matches "Bore 91.0 mm"
                r"(\d+\.\d+)\s*mm\s*bore",  # Matches "91.0 mm Bore"
                r"bore\s*×\s*(\d+\.\d+)\s*mm",  # Matches "Bore × 91.0 mm"
                r"(\d+\.\d+)\s*mm\s*×\s*bore",  # Matches "91.0 mm × Bore"
            ],
            "stroke": [
                r"stroke\s*(\d+\.\d+)\s*mm",  # Matches "Stroke 76.4 mm"
                r"(\d+\.\d+)\s*mm\s*stroke",  # Matches "76.4 mm Stroke"
                r"stroke\s*×\s*(\d+\.\d+)\s*mm",  # Matches "Stroke × 76.4 mm"
                r"(\d+\.\d+)\s*mm\s*×\s*stroke",  # Matches "76.4 mm × Stroke"
            ],
            "compression ratio": [
                r"(\d+\.\d+):1\s*compression\s*ratio",
                r"compression\s*ratio\s*(\d+\.\d+):1",
            ],
            "fuel type": [r"(\w+\s*\w*)\s*fuel\s*type", r"fuel\s*type:\s*(\w+\s*\w*)"],
            "fuel tank capacity": [
                r"(\d+\.\d+)\s*gal\s*fuel\s*tank",
                r"fuel\s*tank\s*(\d+\.\d+)\s*gal",
                r"(\d+\.\d+)\s*L\s*fuel\s*tank",
                r"fuel\s*tank\s*(\d+\.\d+)\s*L",
            ],
            "max. engine power": [
                r"(\d+)\s*hp\s*Max\.?\s*engine\s*power",
                r"Max\.?\s*engine\s*power\s*(\d+)\s*hp",
            ],
            "max. power per liter": [
                r"(\d+)\s*hp/L\s*power\s*density",
                r"power\s*density\s*(\d+)\s*hp/L",
            ],
            # Dimensions and weight
            "length": [
                r"length\s*\n\s*(\d+\.\d+)\s*in",  # Matches "Length\n178.8 in"
                r"length\s*\n\s*(\d+\.\d+)\s*mm",  # Matches "Length\n4541 mm"
                r"length\s*(\d+\.\d+)\s*in",  # Matches "Length 178.8 in"
                r"length\s*(\d+\.\d+)\s*mm",  # Matches "Length 4541 mm"
            ],
            "width": [
                r"width\s*\n\s*(\d+\.\d+)\s*in",  # Matches "Width\n80.0 in"
                r"width\s*\n\s*(\d+\.\d+)\s*mm",  # Matches "Width\n2032 mm"
                r"width\s*(\d+\.\d+)\s*in",  # Matches "Width 80.0 in"
                r"width\s*(\d+\.\d+)\s*mm",  # Matches "Width 2032 mm"
            ],
            "height": [
                r"height\s*\n\s*(\d+\.\d+)\s*in",  # Matches "Height\n51.3 in"
                r"height\s*\n\s*(\d+\.\d+)\s*mm",  # Matches "Height\n1303 mm"
                r"height\s*(\d+\.\d+)\s*in",  # Matches "Height 51.3 in"
                r"height\s*(\d+\.\d+)\s*mm",  # Matches "Height 1303 mm"
            ],
            "wheelbase": [
                r"wheelbase\s*\n\s*(\d+\.\d+)\s*in",  # Matches "Wheelbase\n96.5 in"
                r"wheelbase\s*\n\s*(\d+\.\d+)\s*mm",  # Matches "Wheelbase\n2451 mm"
                r"wheelbase\s*(\d+\.\d+)\s*in",  # Matches "Wheelbase 96.5 in"
                r"wheelbase\s*(\d+\.\d+)\s*mm",  # Matches "Wheelbase 2451 mm"
            ],
            "weight": [
                r"weight\s*\n\s*(\d+,\d+)\s*lbs",  # Matches "Weight\n3,342 lbs"
                r"weight\s*\n\s*(\d+,\d+)\s*kg",  # Matches "Weight\n1,516 kg"
                r"weight\s*(\d+,\d+)\s*lbs",  # Matches "Weight 3,342 lbs"
                r"weight\s*(\d+,\d+)\s*kg",  # Matches "Weight 1,516 kg"
            ],
            "curb weight": [
                r"curb\s*weight\s*\n\s*(\d+,\d+)\s*lbs",  # Matches "Curb weight\n3,342 lbs"
                r"curb\s*weight\s*\n\s*(\d+,\d+)\s*kg",  # Matches "Curb weight\n1,516 kg"
                r"curb\s*weight\s*(\d+,\d+)\s*lbs",  # Matches "Curb weight 3,342 lbs"
                r"curb\s*weight\s*(\d+,\d+)\s*kg",  # Matches "Curb weight 1,516 kg"
            ],
            "cargo volume": [
                r"(\d+\.\d+)\s*cu\s*ft\s*cargo",
                r"cargo\s*volume\s*(\d+\.\d+)\s*cu\s*ft",
                r"(\d+\.\d+)\s*L\s*cargo",
                r"cargo\s*volume\s*(\d+\.\d+)\s*L",
            ],
            "turning circle": [
                r"turning\s*circle\s*diameter\s*\n\s*(\d+\.\d+)\s*ft",  # Matches "Turning circle diameter\n36.7 ft"
                r"turning\s*circle\s*diameter\s*\n\s*(\d+\.\d+)\s*m",  # Matches "Turning circle diameter\n11.2 m"
                r"turning\s*circle\s*diameter\s*(\d+\.\d+)\s*ft",  # Matches "Turning circle diameter 36.7 ft"
                r"turning\s*circle\s*diameter\s*(\d+\.\d+)\s*m",  # Matches "Turning circle diameter 11.2 m"
            ],
            "ground clearance": [
                r"(\d+\.\d+)\s*in\s*ground\s*clearance",
                r"ground\s*clearance\s*(\d+\.\d+)\s*in",
                r"(\d+\.\d+)\s*mm\s*ground\s*clearance",
                r"ground\s*clearance\s*(\d+\.\d+)\s*mm",
            ],
            # Transmission and drivetrain
            "transmission": [
                r"(\w+\s*\w*)\s*transmission",
                r"transmission:\s*(\w+\s*\w*)",
            ],
            "gearbox": [r"(\d+)\s*speed\s*gearbox", r"gearbox:\s*(\d+)\s*speed"],
            "drivetrain": [r"(\w+\s*\w*)\s*drivetrain", r"drivetrain:\s*(\w+\s*\w*)"],
            "clutch": [r"(\w+\s*\w*)\s*clutch", r"clutch:\s*(\w+\s*\w*)"],
            "differential": [
                r"(\w+\s*\w*)\s*differential",
                r"differential:\s*(\w+\s*\w*)",
            ],
            # Fuel economy
            "fuel economy": [
                r"(\d+)\s*mpg\s*fuel\s*economy",
                r"fuel\s*economy\s*(\d+)\s*mpg",
            ],
            "mpg city": [r"(\d+)\s*mpg\s*city", r"city\s*(\d+)\s*mpg"],
            "mpg highway": [r"(\d+)\s*mpg\s*highway", r"highway\s*(\d+)\s*mpg"],
            "mpg combined": [r"(\d+)\s*mpg\s*combined", r"combined\s*(\d+)\s*mpg"],
            "range": [
                r"(\d+)\s*miles\s*range",
                r"range\s*(\d+)\s*miles",
                r"(\d+)\s*km\s*range",
                r"range\s*(\d+)\s*km",
            ],
            # Price and warranty
            "price": [
                r"\$\s*(\d{1,3}(?:,\d{3})*)\s*from",
                r"from\s*\$\s*(\d{1,3}(?:,\d{3})*)",
                r"starting\s*at\s*\$\s*(\d{1,3}(?:,\d{3})*)",
                r"msrp\s*\$\s*(\d{1,3}(?:,\d{3})*)",
            ],
            "msrp": [
                r"msrp\s*\$\s*(\d{1,3}(?:,\d{3})*)",
                r"\$\s*(\d{1,3}(?:,\d{3})*)\s*MSRP",
            ],
            "starting price": [
                r"starting\s*at\s*\$\s*(\d{1,3}(?:,\d{3})*)",
                r"\$\s*(\d{1,3}(?:,\d{3})*)\s*starting\s*price",
            ],
            "warranty": [r"(\d+)\s*year\s*warranty", r"warranty:\s*(\d+)\s*year"],
            "service": [r"(\d+)\s*year\s*service", r"service:\s*(\d+)\s*year"],
        }

        # Look for the specification in the text
        if spec_name.lower() in spec_patterns:
            patterns = spec_patterns[spec_name.lower()]
            for pattern in patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    value = match.group(1)
                    logger.info(f"Found {spec_name} value: {value}")
                    return value

        return None
    except Exception as e:
        logger.error(f"Error extracting spec value: {str(e)}")
        return None


def scrape_porsche_model(model_name: str, query: str = "") -> Dict[str, str]:
    """
    Scrape information about a Porsche model from porsche.com using Playwright

    Args:
        model_name: Name of the Porsche model
        query: Optional search query to filter specific information

    Returns:
        Dictionary containing reference text and source links
    """
    try:
        url = get_model_url(model_name)
        if not url:
            logger.error(f"Could not find URL for model: {model_name}")
            return {"reference_text": "", "source_links": []}

        logger.info(f"Scraping URL: {url}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            )
            page = context.new_page()

            # Navigate to the page
            page.goto(url, wait_until="networkidle")

            # Wait for the page to load
            page.wait_for_load_state("networkidle")
            time.sleep(3)  # Give extra time for dynamic content

            reference_text = ""
            specs_found = []

            # If query is provided, only check specs mentioned in the query
            if query:
                query_lower = query.lower()
                specs_to_check = []

                # Check each spec category
                for spec in ALL_SPECS:
                    if spec.lower() in query_lower:
                        specs_to_check.append(spec)

                # If no specific specs found in query, check all specs
                if not specs_to_check:
                    specs_to_check = ALL_SPECS
            else:
                # If no query provided, check all specs
                specs_to_check = ALL_SPECS

            # Get values for each requested specification
            for spec in specs_to_check:
                value = extract_spec_value(page, spec)
                if value:
                    # Format the spec value based on the type of specification
                    if spec in ["horsepower", "max. engine power"]:
                        specs_found.append(f"{value} horsepower")
                    elif spec == "0-60 mph":
                        specs_found.append(f"0-60 mph in {value} seconds")
                    elif spec == "top speed":
                        specs_found.append(f"top speed of {value} mph")
                    elif spec == "torque":
                        specs_found.append(f"{value} lb-ft of torque")
                    elif spec == "acceleration":
                        specs_found.append(f"0-100 km/h in {value} seconds")
                    elif spec == "braking distance":
                        specs_found.append(f"braking distance of {value} ft")
                    elif spec == "lateral acceleration":
                        specs_found.append(f"lateral acceleration of {value} g")
                    elif spec in [
                        "length",
                        "width",
                        "height",
                        "wheelbase",
                        "ground clearance",
                    ]:
                        specs_found.append(f"{spec} of {value} inches")

                    elif spec in ["bore", "Stroke"]:
                        specs_found.append(f"{spec} of {value} mm")
                    elif spec in ["displacement", "engine displacement"]:
                        specs_found.append(f"{spec} of {value} cc")
                    elif spec in ["weight", "curb weight"]:
                        specs_found.append(f"{spec} of {value} lbs")
                    elif spec == "cargo volume":
                        specs_found.append(f"cargo volume of {value} cubic feet")
                    elif spec == "turning circle":
                        specs_found.append(f"turning circle of {value} feet")
                    elif spec in ["mpg city", "mpg highway", "mpg combined"]:
                        specs_found.append(f"{spec} of {value} mpg")
                    elif spec == "range":
                        specs_found.append(f"range of {value} miles")
                    elif spec in ["price", "msrp", "starting price"]:
                        specs_found.append(f"{spec} of ${value}")
                    elif spec in ["warranty", "service"]:
                        specs_found.append(f"{spec} of {value} years")
                    else:
                        specs_found.append(f"{spec}: {value}")

            # Combine all found specifications into a single text
            if specs_found:
                reference_text = f"The {model_name} has " + ", ".join(specs_found) + "."

            return {"reference_text": reference_text, "source_links": [url]}

    except Exception as e:
        logger.error(f"Error scraping {model_name}: {str(e)}")
        return {"reference_text": "", "source_links": []}
