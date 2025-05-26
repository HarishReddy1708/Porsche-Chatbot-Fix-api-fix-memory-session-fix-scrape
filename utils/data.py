import os
import logging
import psutil
from difflib import get_close_matches
from utils.scraper import scrape_porsche_model
from utils.storage import save_specs, get_latest_specs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import difflib
import requests
import re


porsche_models1 = [
    "911",
    "911 carrera",
    "911 carrera t",
    "911 carrera s",
    "911 carrera gts",
    "911 carrera 4 gts",
    "911 carrera cabriolet",
    "911 carrera T cabriolet",
    "911 carrera s cabriolet",
    "911 carrera gts cabriolet",
    "911 carrera 4 gts Cabriolet",
    "911 Targa 4 gts",
    "911 turbo s",
    "911 Turbo",
    "911 turbo cabriolet",
    "911 turbo s cabriolet",
    "911 gt3",
    "911 gt3 with touring package",
    "911 sprit 70",
    "911 gt3 rs",
    "911 turbo 50 years",
    "911 gt2 rs",
    "911 speedster",
    "911 speedster heritage design",
    "918 spyder",
    "918 spyder 4",
    "918 spyder 4 e-hybrid",
    "718",
    "718 cayman",
    "718 boxter",
    "718 cayman style edition",
    "718 boxster style edition",
    "718 cayman s",
    "718 boxter s",
    "718 cayman gts 4",
    "718 boxster gts 4",
    "718 spyder RS",
    "718 cayman gt4 RS",
    "taycan",
    "taycan 4",
    "taycan 4s",
    "taycan GTS",
    "taycan turbo",
    "taycan turbo s",
    "taycan turbo gt",
    "taycan 4 cross turismo",
    "taycan 4s cross turismo ",
    "taycan turbo cross turismo ",
    "taycan turbo s cross turismo",
    "taycan gts sport turismo",
    "panamera",
    "panamera 4",
    "panamera 4 E-Hybrid",
    "panamera 4s E-Hybrid",
    "panamera GTS",
    "panamera turbo e-hybrid",
    "panamera turbo s e-hybrid",
    "macan",
    "macan t",
    "macan s",
    "macan gts",
    "macan turbo",
    "macan electric",
    "macan 4 electric",
    "macan 4s electric",
    "macan turbo electric",
    "cayenne",
    "cayenne E-hybrid",
    "cayenne s",
    "cayenne s E-hybrid",
    "cayenne gts",
    "cayenne turbo E-hybrid",
    "cayenne turbo",
    "cayenne coupe",
    "cayenne e-hybrid coupe",
    "cayenne s coupe",
    "cayenne s e-hybrid coupe",
    "cayenne coupe e-hybrid",
    "cayenne turbo GT",
]

porsche_models = [
    "911 carrera",
    "911 carrera cabriolet",
    "911 turbo",
    "911 turbo s",
    "911 gt3",
    "911 gt3 rs",
    "911 targa",
    "911 speedster",
    "911 r",
    "911 turbo cabriolet",
    "911 gt2 rs",
    "911 dakar",
    "718 cayman",
    "718 cayman s",
    "718 cayman gts 4.0",
    "718 boxster",
    "718 boxster s",
    "718 boxster gts 4.0",
    "taycan",
    "taycan 4s",
    "taycan turbo",
    "taycan turbo s",
    "taycan cross turismo",
    "taycan cross turismo 4s",
    "taycan cross turismo turbo",
    "taycan cross turismo turbo s",
    "panamera",
    "panamera 4",
    "panamera 4s",
    "panamera turbo",
    "panamera turbo s",
    "panamera gts",
    "panamera 4 e-hybrid",
    "panamera turbo s e-hybrid",
    "panamera sport turismo",
    "macan",
    "macan s",
    "macan gts",
    "macan turbo",
    "cayenne",
    "cayenne s",
    "cayenne gts",
    "cayenne turbo",
    "cayenne turbo s e-hybrid",
    "cayenne coupe",
    "cayenne turbo coupe",
    "cayenne e-hybrid",
    "cayenne coupe e-hybrid",
    "918 spyder",
    "cayman gt4",
    "cayman gt4 rs",
    "boxster spyder",
    "macan ev",
    "911 sport classic",
]


other_models = [
    "urus",
    "aventador",
    "huracan",
    "model x",
    "model y",
    "ferrari f8",
    "ferrari 812",
    "ferrari portofino",
    "m5",
    "m8",
    "x5 m",
    "x6 m",
    "rs7",
    "rs5",
    "q7",
    "q8 rs",
    "mercedes amg gt",
    "sls",
    "g-class",
    "e-class coupe",
    "vantage",
    "db11",
    "dbs superleggera",
    "720s",
    "570s",
    "gt",
    "continental gt",
    "bentley bentayga",
    "f-type",
    "i-pace",
    "tesla model s",
    "tesla model x",
    "tesla model 3",
    "tesla model y",
    "range rover sport",
    "range rover velar",
]

mentioned_models = [
    "carrera",
    "carrera S",
    "Turbo",
    "gt3",
    "turbo s",
    "carrera",
    "taycan",
    "macan",
    "cayenne",
    "panamera",
    "boxster",
    "Cayman S",
    "Cayman GTS",
    "Cayman GT4",
    "Panamera S",
    "Panamera 4",
    "Panamera 4S",
    "Panamera GTS",
    "Panamera Turbo",
    "Panamera Turbo S",
    "Panamera Turbo S E-Hybrid",
    "Panamera Sport Turismo",
    "Panamera 4 E-Hybrid",
    "Panamera 4S E-Hybrid",
    "Macan S",
    "Macan GTS",
    "Macan Turbo",
    "Macan Turbo Performance Package",
    "Taycan 4S",
    "Taycan Turbo",
    "Taycan Turbo S",
    "Taycan Cross Turismo",
    "Taycan GTS",
    "Taycan 4 Cross Turismo918 Spyder",
    "718 Spyder",
    "718 Cayman GT4",
]


MENU_PROMPTS = {
    "models": "You are a Porsche model expert. only Provide specific information of feature asked about the specific model mentioned. always give positvely biased answer towards porsche",
    "dealerships": "You are a Porsche dealership locator. suggest website links to find the nearest dealership.",
    "test-drive": "You are a Porsche test drive coordinator...",
    "build": "You are a Porsche configuration expert...",
}

MODEL_INFO = {
    "911": "The iconic Porsche 911 is our flagship sports car, known for its rear-engine layout and exceptional handling.",
    "taycan": "The Porsche Taycan is our first all-electric sports car, combining performance with sustainability.",
    "macan": "The Porsche Macan is our compact SUV, offering sports car performance in a practical package.",
    "cayenne": "The Porsche Cayenne is our luxury SUV, combining comfort with impressive performance.",
    "panamera": "The Porsche Panamera is our luxury sedan, offering sports car performance with executive comfort.",
    "718": "The Porsche 718 Boxster and Cayman are our mid-engine sports cars, offering pure driving pleasure.",
}

porsche_keywords = [
    "porsche",
    "911",
    "carrera",
    "taycan",
    "macan",
    "cayenne",
    "panamera",
    "boxster",
    "718",
    "top speed",
    "torque",
    "horsepower",
    "0-60",
    "acceleration",
    "features",
    "performance",
    "compare",
    "vs",
    "engine",
    "gt3",
    "turbo",
    "model",
    "dealership",
    "price",
    "leasing",
    "ev",
    "electric",
    "service",
    "maintenance",
    "911",
    "911 carrera",
    "911 carrera s",
    "911 turbo",
    "911 turbo s",
    "911 gt3",
    "911 gt3 rs",
    "911 targa",
    "911 speedster",
    "911 r",
    "911 turbo cabriolet",
    "911 gt2 rs",
    "718 cayman",
    "718 cayman s",
    "718 cayman gts 4.0",
    "718 boxster",
    "718 boxster s",
    "718 boxster gts 4.0",
    "taycan",
    "taycan 4s",
    "taycan turbo",
    "taycan turbo s",
    "taycan cross turismo",
    "taycan cross turismo 4s",
    "taycan cross turismo turbo",
    "taycan cross turismo turbo s",
    "panamera",
    "panamera 4",
    "panamera 4s",
    "panamera turbo",
    "panamera turbo s",
    "panamera gts",
    "panamera 4 e-hybrid",
    "panamera turbo s e-hybrid",
    "panamera sport turismo",
    "macan",
    "macan s",
    "macan gts",
    "macan turbo",
    "cayenne",
    "cayenne s",
    "cayenne gts",
    "cayenne turbo",
    "cayenne turbo s e-hybrid",
    "cayenne coupe",
    "cayenne turbo coupe",
    "cayenne e-hybrid",
    "cayenne coupe e-hybrid",
    "918 spyder",
    "cayman gt4",
    "cayman gt4 rs",
    "boxster spyder",
    "macan ev",
    "911 sport classic",
    "color",
    "accelaration",
    "stroke",
    "test drive",
    "build",
]


porsche_competitor_brands = [
    "Ferrari",
    "Lamborghini",
    "McLaren",
    "Aston Martin",
    "Chevrolet",
    "Nissan",
    "BMW",
    "Mercedes-Benz",
    "Audi",
    "Tesla",
    "Lucid Motors",
    "Rivian",
    "Polestar",
    "Bentley",
    "Jaguar",
    "Lotus",
    "Range Rover",
    "Land Rover",
    "Maserati",
    "Genesis",
    "Cadillac",
    "Lexus",
    "Infiniti",
    "Koenigsegg ",
    "Hennessey ",
    "Bugatti",
    "Rimac",
    "Lucid Motors",
    "Rolls-Royce",
]

Specification_keywords = [
    "acceleration",
    "0-60",
    "top speed",
    "horsepower",
    "torque",
    "mileage",
    "mpg",
    "0 to 60",
    "performance",
    "specifications",
    "specs",
    "engine",
    "power",
    "speed",
    "stroke",
    "cylinder",
    "transmission",
    "drivetrain",
    "displacement",
    "bore",
    "wheelbase",
    "length",
    "width",
    "height",
    "curb weight",
    "weight",
    "cargo capacity",
    "trunk space",
    "towing capacity",
    "payload capacity",
    "brake horsepower",
    "brake torque",
    "brake system",
    "brake type",
    "brake size",
    "brake performance",
    "turning radius",
]

SUGGESTED_QUESTIONS = {
    "models": {
        "911": [
            "What are the different 911 variants?",
            "What is the 0-60 time of the 911?",
            "How much does the 911 cost?",
            "What are the key features of the 911?",
            "Which 911 is best for daily driving?",
            "What's the difference between the 911 Turbo and Turbo S?",
            "Is the 911 GT3 track-ready?",
            "What's new in the latest 911 model year?",
            "What are the differences between 911 Carrera and Carrera S?",
            "How reliable is the Porsche 911?",
            "What engine options are available for the 911?",
            " Does the 911 come in convertible or Targa versions?",
            "What's the top speed of the 911 Carrera S?",
            "What are common 911 maintenance costs?",
            "Is the 911 a good investment car?",
        ],
        "taycan": [
            "How fast can the Taycan charge?",
            "What are the different Taycan models?",
            "What is the price of the Taycan?",
            "How does Taycan compare to Tesla?",
            "What tech features come with the Taycan?",
            "Is the Taycan suitable for long-distance travel?",
            "What's the top speed of the Taycan Turbo S?",
            "How does Taycan compare to other electric cars?",
            "What are the Taycan's performance specs?",
            "What are the Taycan's luxury features?",
            "What are the Taycan's driver assistance features?",
            "Can the Taycan be used as a daily driver?",
            "How efficient is the Taycan compared to other EVs?",
            "How does the Taycan drive compared to gas-powered Porsches?",
        ],
        "macan": [
            "What are the Macan's performance specs?",
            "How much cargo space does the Macan have?",
            "What are the available Macan trims?",
            "What is the starting price of the Macan?",
            "Is the Macan available as an EV?",
            "How does Macan compare to other luxury SUVs?",
            "What driver assistance features are available in the Macan?",
            "What's the difference between Macan and Macan S?",
            "Is the Macan suitable for off-road driving?",
            "What are the Macan's luxury features?",
            "How does the Macan GTS differ from the Macan Turbo?",
            "What's the fuel economy of the Macan?",
            "How comfortable is the Macan for long trips?",
            "What's new in the latest Macan model?",
            "How does the Macan handle compared to the Cayenne?",
        ],
        "cayenne": [
            "What are the Cayenne's engine options?",
            "How much can the Cayenne tow?",
            "What are the Cayenne's luxury features?",
            "What is the price range of the Cayenne?",
            "Is the Cayenne available as a coupe?",
            "Does the Cayenne offer hybrid options?",
            "What is the Cayenne Turbo GT?",
            "How does the Cayenne handle off-road driving?"
            "What are the differences between Cayenne S, GTS, and Turbo?",
            "What's the top speed of the Cayenne Turbo S?",
            "What are common Cayenne maintenance costs?",
            "Is the Cayenne a good investment car?",
            "How does the Cayenne compare to other luxury SUVs?",
            "What's the fuel economy of the Cayenne?",
            "How does the E-Hybrid version perform?",
            "How comfortable is the Cayenne for long drives?",
        ],
        "panamera": [
            "What are the Panamera's performance specs?",
            "How many passengers can the Panamera seat?",
            "What are the Panamera's luxury features?",
            "What is the starting price of the Panamera?",
            "What's the difference between Panamera and Panamera Sport Turismo?",
            "Is the Panamera available as a hybrid?",
            "Does the Panamera have a performance variant?",
            "How does the Panamera compare to other executive sedans?",
        ],
        "718": [
            "What's the difference between Boxster and Cayman?",
            "What are the 718's performance specs?",
            "How much does the 718 cost?",
            "What are the available 718 variants?",
            "Is the 718 suitable for track use?",
            "How does the 718 handle compared to the 911?",
            "What engine options are available in the 718?",
            "Is the 718 a good option for a weekend sports car?"
            "What's the top speed of the 718 Cayman GT4?",
            "What are common 718 maintenance costs?",
            "Is the 718 a good investment car?",
            "How does the 718 compare to other luxury sedans?",
            "What's the fuel economy of the 718?",
            "How does the GT4 version perform?",
            "How comfortable is the 718 for long drives?",
        ],
    },
    "dealerships": [
        "What are the dealership hours?",
        "Do you offer financing options?",
        "Can I schedule a test drive?",
        "What services do you offer?",
    ],
    "test-drive": [
        "What models are available for test drive?",
        "How long is a test drive?",
        "Do I need to make an appointment?",
        "What documents do I need to bring?",
    ],
    "build": [
        "What are the available colors?",
        "What interior options are available?",
        "What performance packages are offered?",
        "How long does delivery take?",
    ],
}

model_keywords = {
    "911 turbo s": "Porsche 911 Turbo S",
    "911 carrera": "Porsche 911 Carrera",
    "911 carrera s": "911 Carrera S",
    "911 carrera gts": "911 Carrera GTS",
    "911 gt3": "Porsche 911 GT3",
    "911 gt3 rs": "Porsche 911 GT3 RS",
    "911 gt2 rs": "Porsche 911 GT2 RS",
    "911 sport classic": "Porsche 911 Sport Classic",
    "911 turbo cabriolet": "Porsche 911 Turbo Cabriolet",
    "911 targa": "Porsche 911 Targa",
    "911 speedster": "Porsche 911 Speedster",
    "911 r": "Porsche 911 R",
    "911 dakar": "Porsche 911 Dakar",
    "718": "Porsche 718",
    "718 cayman": "Porsche 718 Cayman",
    "718 cayman s": "Porsche 718 Cayman S",
    "718 cayman gts 4.0": "Porsche 718 Cayman GTS 4.0",
    "718 boxster": "Porsche 718 Boxster",
    "718 boxster s": "Porsche 718 Boxster S",
    "718 boxster gts 4.0": "Porsche 718 Boxster GTS 4.0",
    "taycan": "Porsche Taycan",
    "taycan turbo": "Porsche Taycan Turbo",
    "taycan turbo s": "Porsche Taycan Turbo S",
    "taycan cross turismo": "Porsche Taycan Cross Turismo",
    "taycan cross turismo 4s": "Porsche Taycan Cross Turismo 4S",
    "taycan cross turismo turbo": "Porsche Taycan Cross Turismo Turbo",
    "taycan cross turismo turbo s": "Porsche Taycan Cross Turismo Turbo S",
    "macan": "Porsche Macan",
    "macan s": "Porsche Macan S",
    "macan gts": "Porsche Macan GTS",
    "macan turbo": "Porsche Macan Turbo",
    "macan turbo s": "Porsche Macan Turbo S",
    "macan ev": "Porsche Macan EV",
    "macan turbo s e-hybrid": "Porsche Macan Turbo S e-Hybrid",
    "macan gts e-hybrid": "Porsche Macan GTS e-Hybrid",
    "macan sport turismo": "Porsche Macan Sport Turismo",
    "macan sport turismo s": "Porsche Macan Sport Turismo S",
    "macan sport turismo s e-hybrid": "Porsche Macan Sport Turismo S e-Hybrid",
    "cayenne": "Porsche Cayenne",
    "cayenne s": "Porsche Cayenne S",
    "cayenne gts": "Porsche Cayenne GTS",
    "cayenne turbo": "Porsche Cayenne Turbo",
    "cayenne turbo s": "Porsche Cayenne Turbo S",
    "cayenne coupe": "Porsche Cayenne Coupe",
    "cayenne turbo coupe": "Porsche Cayenne Turbo Coupe",
    "cayenne turbo coupe s": "Porsche Cayenne Turbo Coupe S",
    "cayenne e-hybrid": "Porsche Cayenne e-Hybrid",
    "cayenne coupe e-hybrid": "Porsche Cayenne Coupe e-Hybrid",
    "cayenne turbo coupe e-hybrid": "Porsche Cayenne Turbo Coupe e-Hybrid",
    "cayenne gts e-hybrid": "Porsche Cayenne GTS e-Hybrid",
    "cayenne coupe gts e-hybrid": "Porsche Cayenne Coupe GTS e-Hybrid",
    "cayenne turbo coupe gts e-hybrid": "Porsche Cayenne Turbo Coupe GTS e-Hybrid",
    "cayenne sport turismo": "Porsche Cayenne Sport Turismo",
    "cayenne sport turismo s": "Porsche Cayenne Sport Turismo S",
    "cayenne sport turismo s e-hybrid": "Porsche Cayenne Sport Turismo S e-Hybrid",
    "cayenne coupe sport turismo": "Porsche Cayenne Coupe Sport Turismo",
    "cayenne coupe sport turismo s": "Porsche Cayenne Coupe Sport Turismo S",
    "cayenne coupe sport turismo s e-hybrid": "Porsche Cayenne Coupe Sport Turismo S e-Hybrid",
    "panamera": "Porsche Panamera",
    "panamera 4": "Porsche Panamera 4",
    "panamera 4s": "Porsche Panamera 4S",
    "panamera turbo": "Porsche Panamera Turbo",
    "panamera turbo s": "Porsche Panamera Turbo S",
    "panamera gts": "Porsche Panamera GTS",
    "panamera 4 e-hybrid": "Porsche Panamera 4 e-Hybrid",
    "panamera turbo s e-hybrid": "Porsche Panamera Turbo S e-Hybrid",
    "panamera sport turismo": "Porsche Panamera Sport Turismo",
    "boxster": "Porsche Boxster",
    "boxster spyder": "Porsche Boxster Spyder",
    "cayman gt4": "Porsche Cayman GT4",
    "cayman gt4 rs": "Porsche Cayman GT4 RS",
}


def extract_competitor_brands(user_input, cutoff=0.8):
    words = user_input.split()
    found = set()
    for word in words:
        matches = difflib.get_close_matches(
            word, porsche_competitor_brands, n=1, cutoff=cutoff
        )
        if matches:
            found.add(matches[0])
    return list(found)


def match_model_phrase(text, p_models):
    """Returns the most specific matching Porsche model found as an exact phrase."""
    text = text.lower()
    # Sort models by length in descending order to match the most specific (longest) first
    sorted_models = sorted(p_models, key=len, reverse=True)
    for model in sorted_models:
        pattern = r"\b" + re.escape(model.lower()) + r"\b"
        if re.search(pattern, text):
            return model
    return None


def correct_spelling(user_input):
    words = user_input.lower().split()
    corrected = []
    for word in words:
        match = get_close_matches(word, porsche_models1 + other_models, n=1, cutoff=0.8)
        corrected.append(match[0] if match else word)
    return " ".join(corrected)


# Extract model mentions
def extract_models(user_input):
    known_models = ["911", "taycan", "panamera", "cayenne", "macan", "718"]
    return [kw for kw in known_models if kw in user_input.lower()]


# Resource optimization
def get_optimal_thread_count():
    cpu_count = psutil.cpu_count(logical=False)
    return max(1, min(cpu_count - 1, 4))


def get_optimal_context_size():
    """
    Determine the optimal context window size for the LLM based on system memory.
    Allows override via environment variable 'LLM_CONTEXT_SIZE'.
    """
    try:
        # Allow manual override from environment
        ctx_override = os.getenv("LLM_CONTEXT_SIZE")
        if ctx_override:
            ctx = int(ctx_override)
            logger.info(f"Context size overridden via environment: {ctx}")
            return ctx

        memory = psutil.virtual_memory()
        gb = memory.total / (1024 * 1024 * 1024)

        if gb > 16:
            ctx = 2048
        elif gb > 12:
            ctx = 1536
        elif gb > 8:
            ctx = 1024
        else:
            ctx = 512

        logger.info(
            f"Total system memory: {gb:.2f} GB — Optimal context size selected: {ctx}"
        )
        return ctx
    except Exception as e:
        logger.warning(
            f"Error determining context size: {str(e)} — Falling back to default 512"
        )
        return 512


def search_porsche_model(model_name, num_results=2):
    """
    Search for Porsche model information using pre-scraped data or web scraping as fallback
    """
    try:
        # Extract the model name and query from the input
        input_text = model_name.lower().strip()

        # Remove common words that might interfere with model matching
        input_text = re.sub(
            r"\b(porsche|specifications|features|specs|info|details)\b",
            "",
            input_text,
            flags=re.IGNORECASE,
        )
        input_text = input_text.strip()

        # Try to find a matching model name
        model_match = None
        for model in porsche_models1:
            if model.lower() in input_text:
                model_match = model
                break

        if not model_match:
            logger.error(f"Could not find matching model in: {input_text}")
            return {"reference_text": "", "source_links": []}

        # Extract the query (everything after the model name)
        query = input_text.replace(model_match.lower(), "").strip()

        # First try to get pre-scraped data
        cached_specs = get_latest_specs(model_match, query)
        if cached_specs:
            logger.info(f"Using pre-scraped data for {model_match}")
            return cached_specs

        # If no pre-scraped data found, scrape new data
        logger.info(
            f"No pre-scraped data found for {model_match}, scraping new data..."
        )
        result = scrape_porsche_model(model_match, query)

        # Save the scraped data for future use
        if result["reference_text"]:
            save_specs(model_match, result, query)

        return result

    except Exception as e:
        logger.error(f"Error searching Porsche model: {str(e)}")
        return {"reference_text": "", "source_links": []}


def trim_reference(ref_text, max_sentences=2):
    sentences = re.split(r"(?<=[.!?]) +", ref_text)
    return " ".join(sentences[:max_sentences])
