import json
import os
import logging
from typing import Dict, Optional, List
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to the data file
DATA_DIR = "data"
SPECS_FILE = os.path.join(DATA_DIR, "porsche_specs.json")


class PorscheDataLoader:
    def __init__(self):
        self.data = self._load_data()

    def _load_data(self) -> Dict:
        """Load data from the JSON file"""
        try:
            if os.path.exists(SPECS_FILE):
                with open(SPECS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            logger.warning(f"No data file found at {SPECS_FILE}")
            return {}
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return {}

    def _normalize_query(self, query: str) -> str:
        """Normalize query for better matching"""
        # Convert to lowercase
        query = query.lower()

        # Remove common words and phrases
        query = re.sub(
            r"\b(give|tell|me|about|the|what|is|are|of|for|a|an)\b", "", query
        )

        # Remove extra whitespace
        query = " ".join(query.split())

        return query

    def _get_query_type(self, query: str) -> str:
        """Determine the type of query based on keywords"""
        query = query.lower()

        # Map of keywords to query types
        query_mapping = {
            "horsepower": ["horsepower", "hp", "power", "engine power"],
            "0-60 mph": ["0-60", "acceleration", "0 to 60", "zero to sixty"],
            "top speed": ["top speed", "maximum speed", "max speed", "speed"],
            "torque": ["torque", "lb-ft", "pound feet"],
            "price": ["price", "cost", "msrp", "starting price"],
            "engine": ["engine", "motor", "displacement", "cylinders"],
            "bore": ["bore", "diameter"],
            "stroke": ["stroke"],
            "compression ratio": ["compression", "ratio"],
            "length": ["length"],
            "width": ["width"],
            "height": ["height"],
            "wheelbase": ["wheelbase"],
            "curb weight": ["curb weight"],
            "weight": ["weight", "mass"],
            "transmission": ["transmission", "gearbox", "gears", "manual", "automatic"],
            "fuel economy": ["fuel", "mpg", "economy", "consumption", "efficiency"],
        }

        # Check each query type's keywords
        for query_type, keywords in query_mapping.items():
            if any(keyword in query for keyword in keywords):
                return query_type

        return query

    def _get_full_model_name(self, model_name: str) -> str:
        """Get the full model name from a partial name"""
        # Common model name mappings
        model_mappings = {
            # 911 variants
            "911 carrera": "911 carrera",
            "911 carrera T": "911 carrera T",
            "911 carrera s": "911 carrera s",
            "911 carrera cabriolet": "911 carrera cabriolet",
            "911 carrera T cabriolet": "911 carrera t cabriolet",
            "911 carrera s cabriolet": "911 carrera s cabriolet",
            "911 carrera gts cabriolet": "911 carrera gts cabriolet",
            "911 carrera 4 gts cabriolet": "911 carrera 4 gts cabriolet",
            "911 turbo s": "911 turbo s",
            "911 turbo": "911 turbo",
            "911 turbo cabriolet": "911 turbo cabriolet",
            "911 turbo s cabriolet": "911 turbo s cabriolet",
            "911 carrera GTS": "911 carrera GTS",
            "911 carrera 4 GTS": "911 carrera 4 gts",
            "911 gt3": "911 gt3",
            "911 gt3 rs": "911 gt3 rs",
            "911 gt2 rs": "911 gt2 rs",
            "911 targa": "911 targa",
            "911 targa 4 gts": "911 targa 4 gts ",
            "911 spirit 70": "911 spirit 70",
            "718 cayman": "718 cayman",
            "718 boxster": "718 boxster",
            "718 cayman s": "718 cayman s",
            "718 boxster s": "718 boxster s",
            "718 cayman style edition": "718 cayman style edition",
            "718 boxster style edition": "718 boxster style edition",
            "718 spyder": "718 spyder",
            "718 cayman gt4 rs": "718 cayman gt4 rs",
            "718 boxster gt4": "718 boxster gt4",
            "718 cayman gts 4.0": "718 cayman gts 4.0",
            "718 boxster gts 4.0": "718 boxster gts 4.0",
            "718 spyder rs": "718 spyder rs",
            "taycan": "taycan",
            "taycan 4s": "taycan 4s",
            "taycan 4": "taycan 4",
            "taycan gts": "taycan gts",
            "taycan turbo": "taycan turbo",
            "taycan turbo s": "taycan turbo s",
            "taycan turbo gt": "taycan turbo gt",
            "taycan 4 cross turismo": "taycan 4 cross turismo",
            "taycan 4s cross turismo": "taycan 4s cross turismo",
            "taycan gts cross turismo": "taycan gts cross turismo",
            "taycan turbo cross turismo": "taycan turbo cross turismo",
            "taycan turbo s cross turismo": "taycan turbo s cross turismo",
            "taycan gts sport turismo": "taycan gts sport turismo",
            "panamera": "panamera",
            "panamera 4": "panamera 4",
            "panamera 4 e-hybrid": "panamera 4 e-hybrid",
            "panamera 4s e-hybrid": "panamera 4s e-hybrid",
            "panamera GTS": "panamera GTS",
            "panamera turbo e-hybrid": "panamera turbo e-hybrid",
            "panamera turbo s e-hybrid": "panamera turbo s e-hybrid",
            "cayenne": "cayenne",
            "cayenne s": "cayenne s",
            "cayenne gts": "cayenne gts",
            "cayenne E-hybrid": "cayenne E-hybrid",
            "cayenne s e-hybrid": "cayenne s e-hybrid",
            "cayenne coupe": "cayenne coupe",
            "cayenne e-hybrid coupe": "cayenne e-hybrid coupe",
            "cayenne s coupe": "cayenne s coupe",
            "cayenne s e-hybrid coupe": "cayenne s e-hybrid coupe",
            "cayenne coupe e-hybrid": "cayenne coupe e-hybrid",
            "cayenne gts coupe": "cayenne gts coupe",
            "cayenne turbo E-hybrid": "cayenne turbo E-hybrid",
            "cayenne turbo gt": "cayenne turbo gt",
            "macan": "macan",
            "macan t": "macan t",
            "macan s": "macan s",
            "macan gts": "macan gts",
            "macan electric": "macan electric",
            "macan 4 electric": "macan 4 electric",
            "macan 4s electric": "macan 4s electric",
            "macan turbo electric": "macan turbo electric",
        }

        # Try to find the full model name
        model_name = model_name.lower()

        # First try exact matches
        for partial, full in model_mappings.items():
            if model_name == partial:
                return full

        # Then try partial matches
        for partial, full in model_mappings.items():
            if partial in model_name:
                return full

        return model_name

    def get_model_specs(self, model_name: str, query: str = "") -> Optional[Dict]:
        """
        Get specifications for a specific model and query

        Args:
            model_name: Name of the Porsche model
            query: Optional query to filter specifications

        Returns:
            Dictionary containing specifications or None if not found
        """
        try:
            # Get the full model name
            full_model_name = self._get_full_model_name(model_name)
            logger.info(f"Model name '{model_name}' mapped to '{full_model_name}'")

            if full_model_name not in self.data:
                logger.warning(f"Model '{full_model_name}' not found in data")
                return None

            model_entries = self.data[full_model_name]

            # If query provided, determine the query type
            if query:
                query_type = self._get_query_type(query)
                logger.info(f"Query '{query}' mapped to type: {query_type}")

                if query_type:
                    filtered_entries = [
                        entry for entry in model_entries if entry["query"] == query_type
                    ]
                    if filtered_entries:
                        model_entries = filtered_entries
                        logger.info(
                            f"Found {len(filtered_entries)} entries for query type: {query_type}"
                        )

            if not model_entries:
                logger.warning(
                    f"No entries found for {full_model_name} with query: {query}"
                )
                return None

            # Get the latest entry
            latest_entry = max(model_entries, key=lambda x: x["timestamp"])

            return {
                "reference_text": latest_entry["specs"],
                "source_links": latest_entry["source_links"],
            }

        except Exception as e:
            logger.error(f"Error getting model specs: {str(e)}")
            return None

    def get_all_models(self) -> List[str]:
        """Get list of all available models"""
        return list(self.data.keys())

    def get_model_queries(self, model_name: str) -> List[str]:
        """Get list of all available queries for a model"""
        full_model_name = self._get_full_model_name(model_name)
        if full_model_name not in self.data:
            return []
        return list(set(entry["query"] for entry in self.data[full_model_name]))

    def get_all_specs(self, model_name: str) -> Dict[str, str]:
        """
        Get all specifications for a model

        Returns:
            Dictionary mapping query types to their specifications
        """
        full_model_name = self._get_full_model_name(model_name)
        if full_model_name not in self.data:
            return {}

        specs = {}
        for entry in self.data[full_model_name]:
            query = entry["query"]
            if query not in specs:  # Only keep the latest entry for each query
                specs[query] = {
                    "reference_text": entry["specs"],
                    "source_links": entry["source_links"],
                }
        return specs


# Create a global instance
data_loader = PorscheDataLoader()
