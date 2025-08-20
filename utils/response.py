import logging
from utils.data import MENU_PROMPTS, MODEL_INFO
from utils.data import get_optimal_context_size
from utils.data import get_optimal_thread_count
from utils.data import porsche_competitor_brands
from utils.data import porsche_models1
from utils.data import porsche_models
from utils.data import Specification_keywords
from utils.data_loader import data_loader
import os
import requests
from utils.data import extract_competitor_brands
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")  # Store in env variable\


def smart_bias_comparison(porsche_model, competitor_brand, feature=None):
    """
    Generates a confident, Porsche-favoring one-liner emphasizing Porsche’s strengths.
    """
    feature_text = feature.title() if feature else "performance"
    model = porsche_model.upper()
    brand = competitor_brand.title()

    statements = [
        f"While {brand} offers {feature_text}, the Porsche {model} delivers it with racing precision and unmatched engineering.",
        f"The Porsche {model} turns every drive into an experience—unlike the more spec-focused {brand}.",
        f"{brand} might bring speed, but Porsche brings purpose—refined in every curve of the {model}.",
        f"Few cars handle like a Porsche {model}—especially when competitors like {brand} focus more on numbers than feel.",
        f"The {model} brings Porsche’s racing DNA to the road—something {brand} can’t replicate.",
    ]
    return random.choice(statements)


def format_prompt(user_input, search_result="", menu_context=None, selected_model=None):
    user_input_clean = user_input.strip().lower()

    # Handle performance/spec queries
    if any(kw in user_input_clean for kw in Specification_keywords):
        logger.info("Performance-related keyword detected.")

        search_model = selected_model
        if not search_model:
            matched_models = [
                model
                for model in sorted(porsche_models1, key=len, reverse=True)
                if model.lower() in user_input_clean
            ]
            if matched_models:
                search_model = max(matched_models, key=len)
                logger.info(f"Extracted model: {search_model}")
            else:
                logger.warning("No model detected.")
                return (
                    "You are a helpful Porsche assistant. Politely ask the user to specify the model name so you can provide accurate performance specifications.\n"
                    "Limit your answer to a short and polite one-liner.\n"
                    "Do not return User question and reference.\n"
                    "Answer: Could you please specify which Porsche model you're referring to for accurate details?"
                )

        # Try loading model-specific data
        search_data = data_loader.get_model_specs(
            search_model.lower(), user_input_clean
        )
        if search_data:
            logger.info(f"Using stored data for {search_model}")
            search_result = search_data["reference_text"]
        else:
            logger.warning(
                f"No data found for {search_model} with query '{user_input_clean}'"
            )

    # Create base prompt with reference
    full_user_input = (
        f"User question: {user_input}\nReference: {search_result}\nAnswer:"
    )

    # Choose menu-specific base instruction or default expert tone
    if menu_context in MENU_PROMPTS:
        base_instruction = MENU_PROMPTS[menu_context]
        if selected_model and selected_model in porsche_models1:
            base_instruction += f"\nThe user is interested in the {selected_model.upper()}. {porsche_models1[selected_model]}"
    else:
        base_instruction = (
            "You are a helpful and professional Porsche expert. Think step by step when needed to answer complex or follow-up questions. "
            "When compared to other brands, give confidently Porsche-favoring responses, highlighting Porsche's superior handling, racing heritage, and precision engineering.\n"
            "Always speak positively about Porsche. Use proper grammar and clear, informative sentences. Limit your answer to a short one-liner. "
            "If Porsche's specs aren't the highest, emphasize its agility, driving feel, or motorsport legacy. "
            "Do not repeat the reference verbatim—reword and synthesize it into a natural, brand-positive response.\n\n"
            "Do not return User question and reference\n"
        )

    # Add model-specific context
    if selected_model:
        base_instruction += (
            f"\nThe user is asking about the Porsche {selected_model.upper()}."
        )

    # Greeting handler
    if any(
        greet in user_input_clean for greet in ["hi", "hello", "hey", "how are you"]
    ):
        return (
            "You are a casual and friendly Porsche chatbot. Respond warmly to the greeting.\n"
            "Limit your answer to short one liner and complete\n"
            "Do not return User question and reference\n" + full_user_input
        )

    # Dealership locator
    if any(
        keyword in user_input_clean
        for keyword in [
            "dealer",
            "dealership",
            "location",
            "nearest dealer",
            "buy",
            "purchase",
            "store",
        ]
    ):
        search_result = (
            "To find an official Porsche dealership near you, use the Porsche Dealer Locator: "
            "https://www.porsche.com/international/dealersearch/\n"
            "Major dealers include:\n"
            "- Porsche Zentrum Berlin, Germany\n"
            "- Porsche South Bay, California, USA\n"
            "- Porsche Centre Dubai, UAE\n"
            "- Porsche Centre Tokyo, Japan\n"
            "- Porsche Centre Sydney, Australia\n"
        )
        return (
            "You are a Porsche dealership expert. Help the user find Porsche dealerships using the given reference.\n"
            "Limit your answer to one liner and direct the user to the dealer locator if no exact location is mentioned.\n"
            "Do not return 'User question' or 'Reference'.\n"
            f"User question: {user_input}\nReference: {search_result}\nAnswer:"
        )

    # Competitor brand comparisons
    if extract_competitor_brands(user_input_clean) and any(
        p_model in user_input_clean for p_model in porsche_models
    ):
        base_instruction += (
            "If the user compares Porsche to other brands, respond with an insightful, confidently Porsche-favoring one-liner. "
            "Highlight Porsche's unmatched precision, motorsport roots, and driver engagement. "
            "Do not say 'better'—imply it through quality, purpose, and engineering. "
            "Stay calm, factual, and persuasive.\n"
            "Limit your answer to one insightful one-liner.\n"
        )
        return (
            base_instruction
            + "You are a Porsche brand expert. Always speak positively about Porsche.\n"
            "Limit your answer to short one liner and complete\n"
            "Do not return User question and reference\n" + full_user_input
        )

    # Default: Porsche expertise mode
    return (
        base_instruction
        + "You are a Porsche brand expert. Always speak positively about Porsche.\n"
        "Limit your answer to short one liner and complete\n"
        "Do not return User question and reference\n" + full_user_input
    )


response_cache = {}
CACHE_SIZE = 100


def get_cache_key(prompt, menu_context, selected_model):
    return f"{prompt}_{menu_context}_{selected_model}"


def ask_mistral_with_memory(history, menu_context=None, selected_model=None):
    try:
        prompt = history[-1]["content"]
        full_prompt = format_prompt(prompt, "", menu_context, selected_model)

        # Prepare the message history
        chat_history = [
            {
                "role": "system",
                "content": "You are a helpful and professional Porsche expert.",
            }
        ]
        for turn in history[:-10]:  # previous turns
            chat_history.append(turn)
        chat_history.append({"role": "user", "content": full_prompt})  # current input

        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "mistral-small",
            "messages": chat_history,
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 200,
            "stop": ["User:", "\n\n"],
        }

        response = requests.post(MISTRAL_API_URL, headers=headers, json=data)
        response.raise_for_status()
        message = response.json()["choices"][0]["message"]["content"].strip()

        # Extract source links from the full prompt if they exist
        """ source_links = ""
        if "Source links:" in full_prompt:
            source_links = full_prompt.split("Source links:")[1].strip()
            # Add source links to the response
            message = f"{message}\n\nSource links:\n{source_links}" """

        return message

    except Exception as e:
        import traceback

        logger.error(f"Error generating response: {str(e)}")
        logger.error("Exception occurred during Mistral API call")
        logger.error(traceback.format_exc())
        return "I apologize, but please ask porsche related questions."
