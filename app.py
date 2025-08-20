from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import logging
from utils.suggetions import get_suggested_questions
from utils.response import ask_mistral_with_memory
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "your-secret-key")
app.config["SESSION_TYPE"] = "filesystem"
socketio = SocketIO(app, manage_session=True)





@socketio.on("message")
def handle_message(message):
    try:
        menu_context = message.get("menu_context", None)
        selected_model = message.get("selected_model", None)
        user_message = message.get("message", "")
        print(f"User message: {user_message}")

        if not user_message:
            emit("error", "Empty message received")
            return

        # Check if the message is just a name or random text, but allow city names for dealership queries
        if (
            menu_context != "dealerships"
            and len(user_message.split()) <= 2
            and not any(char.isdigit() for char in user_message)
        ):
            emit(
                "response",
                {
                    "message": "Hello! I'm your Porsche expert. Please ask me something about Porsche models, features, or performance.",
                    "suggested_questions": [
                        "What's the top speed of the 911 Turbo S?",
                        "How much horsepower does the Taycan produce?",
                        "Which Porsche is best for daily driving?",
                    ],
                },
            )
            return

        # Maintain session-based memory (keep last 1 message for now)
        history = session.get("history", [])
        history.append({"role": "user", "content": user_message})
        if len(history) > 1:
            history = history[-1:]

        # Get response from Mistral model
        response = ask_mistral_with_memory(history, menu_context, selected_model)

        # Update history with assistant's response
        history.append({"role": "assistant", "content": response})
        session["history"] = history

        # Get suggested questions based on user input
        suggested_questions = get_suggested_questions(menu_context, user_message)
        logger.info(f"menu_context: {menu_context}")

        # Emit response back to user
        emit(
            "response",
            {"message": response, "suggested_questions": suggested_questions},
        )

    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        emit("error", "Sorry, I encountered an error. Please try again.")

    logger.info(f"suggested_questions: {suggested_questions}")


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
