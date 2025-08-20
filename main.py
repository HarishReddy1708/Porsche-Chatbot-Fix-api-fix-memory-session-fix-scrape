from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(
    app, cors_allowed_origins="http://127.0.0.1:5000"
)  # Or ["http://127.0.0.1:5000"]


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("message")
def handle_message(data):
    print("Received:", data)
    emit("response", {"message": "Hello from server!"})


if __name__ == "__main__":
    socketio.run(app)
