import random
from utils.data import SUGGESTED_QUESTIONS
from utils.data import extract_models
import logging


logger = logging.getLogger(__name__)


def get_suggested_questions(menu_context, user_input=None):
    logger.info(f"Menu context: {menu_context}, User input: {user_input}")

    if user_input:
        models_mentioned = extract_models(user_input)
        logger.info(f"Models mentioned: {models_mentioned}")
        model = models_mentioned[0] if models_mentioned else None
    else:
        model = None

    if menu_context == "models" and model:
        questions = SUGGESTED_QUESTIONS["models"].get(model, [])
        logger.info(f"Model-specific questions: {questions}")
        return random.sample(questions, min(2, len(questions))) if questions else []

    elif menu_context in SUGGESTED_QUESTIONS:
        questions = SUGGESTED_QUESTIONS[menu_context]
        #logger.info(f"General context questions: {questions}")
        if isinstance(questions, list):
            return random.sample(questions, min(3, len(questions)))

    logger.warning("No suggested questions found.")
    return []
