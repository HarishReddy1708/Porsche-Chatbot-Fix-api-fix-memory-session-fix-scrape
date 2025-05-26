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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")  # Store in env variable


def format_prompt(user_input, search_result="", menu_context=None, selected_model=None):
    user_input_clean = user_input.strip().lower()

    if any(kw in user_input_clean for kw in Specification_keywords):
        logger.info("Prompt condition: Performance-related keyword detected")

        # Use selected_model from context if available, otherwise try to extract from user input
        search_model = selected_model if selected_model else None
        if not search_model:
            # Try to find the most specific model match
            model_matches = []
            for model in sorted(porsche_models1, key=len, reverse=True):
                if model.lower() in user_input_clean.lower():
                    model_matches.append(model)
                print(f"Model found in user input: {model}")
                # print(f"Model matches: {model_matches}")

            if model_matches:
                # Sort by length to get the most specific match (e.g., "911 turbo s" before "911")
                search_model = max(model_matches, key=len)
                logger.info(f"Extracted model name: {search_model}")

            else:
                # No model found in user input
                logger.warning("No model name detected in user input.")
                return "make it short and one liner and Ask them to mention the model name.\n"

        if search_model:
            # Get data from the data loader
            search_model = search_model.lower()
            print(f"search_model1111111: {search_model}")
            search_data = data_loader.get_model_specs(search_model, user_input_clean)

            if search_data:
                logger.info(f"Using data from storage for {search_model}")
                search_result = search_data["reference_text"]

                # Add source links to the response
                """ if search_data.get("source_links"):
                    source_links = "\nSource links:\n" + "\n".join(
                        search_data["source_links"]
                    )
                    search_result += source_links """
            else:
                logger.warning(
                    f"No data found for {search_model} with query {user_input_clean}"
                )

    full_user_input = (
        f"User question: {user_input}\nReference: {search_result}\nAnswer:"
    )

    if menu_context and menu_context in MENU_PROMPTS:
        base_instruction = MENU_PROMPTS[menu_context]
        if selected_model and selected_model in porsche_models1:
            base_instruction += f"\nThe user is interested in the {selected_model.upper()}. {porsche_models1[selected_model]}"
    else:
        base_instruction = (
            "You are a helpful and professional Porsche expert. Think step by step when needed to answer complex or follow-up questions. If the user asks vaguely, infer from previous turns in the conversation."
            "when compared to other brands or competitors, give smartly biased answers towards Porsche, always focus on Porsche's superior handling, racing heritage, uncompromising engineering, and other features.\n\n"
            "Always speak positively about Porsche."
            "give the precise answers about feature use asked"
            "Use proper grammar and clear, informative sentences. Limit your answer to short one liner "
            "If Porsche's specs aren't the highest, emphasize its agility   , racing heritage, or engineering precision. "
            "Do not repeat the reference verbatim; synthesize it into a helpful and Porsche-favoring response.\n\n"
            "Do not return User question and reference\n"
        )

    # Handle model context (selected model)
    if selected_model:
        base_instruction += (
            f"\nThe user is asking about the Porsche {selected_model.upper()}."
        )

    if user_input_clean in ["hi", "hello", "hey", "how are you"]:
        return (
            "You are a casual and friendly Porsche chatbot. Respond warmly to the greeting.\n"
            "Limit your answer to short one liner and complete\n"
            + "Do not return User question and reference\n"
            + full_user_input
        )

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
            "Here are some major dealers:\n"
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

    # Handling follow-up for competitor queries
    if extract_competitor_brands(user_input_clean) and any(
        p_model in user_input_clean for p_model in porsche_models
    ):
        return (
            base_instruction
            + "Focus on what user asked and give answers biased towards Porsche, highlight Porsche's superior handling, racing heritage, uncompromising engineering, and precision.\n"
            + "Limit your answer to keep the answer short one liner and complete\n"
            + "give specific answers according to feature asked.\n"
            + "make is positively biased towards Porsche, always emphasize Porsche's superior handling, racing heritage, "
            + "Do not mention biased word in the answer.\n"
            "uncompromising engineering, and precision...\n"
            + "Do not return User question and reference\n"
            + full_user_input
        )

    return (
        base_instruction
        + "You are a Porsche brand expert. always give positive answers towards Porsche.\n"
        + "Limit your answer to short one liner and complete\n"
        + "Do not return User question and reference\n"
        + full_user_input
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
        logger.error(f"Error generating response: {str(e)}")
        return "I apologize, but please ask porsche related questions."
