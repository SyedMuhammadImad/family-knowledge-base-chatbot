import time
# Fix for python-aiml compatibility with newer Python versions
if not hasattr(time, 'clock'):
    time.clock = time.perf_counter

from flask import Flask, render_template, request, jsonify
from family_agent import FamilyKnowledgeAgent

app = Flask("__Apna__Bot__")

# Initialize the agent once when the server starts
print("Initializing Family Knowledge Base...")
agent = FamilyKnowledgeAgent()
print("Ready!")

@app.route("/")
def home():
    # Serves the HTML UI
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    # Receives the message from the web UI, passes it to the agent
    user_data = request.json
    user_message = user_data.get("message", "")

    if not isinstance(user_message, str) or not user_message.strip() or len(user_message)>1000:
        return jsonify({"response": "Please enter a message."})

    bot_response = agent.ask(user_message)
    return jsonify({"response": bot_response})


if __name__ == "__main__":
    # Runs the local development server
    app.run(host="127.0.0.1", debug=False, port=5000)