import time
if not hasattr(time, 'clock'):
    time.clock = time.perf_counter
from flask import Flask, render_template, request, jsonify
from family_agent import FamilyKnowledgeAgent

app = Flask(__name__)

print("Initializing Family Knowledge Base...")
agent = FamilyKnowledgeAgent()
print("Ready!")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/add", methods=["POST"])
def add_fact():
    """Input mode — collect facts from natural language."""
    data = request.get_json(silent=True)
    if data is None: data = {}
    if not isinstance(data, dict): return jsonify({"response":"Expected a JSON object."}), 400
    user_message = data.get("message", "")
    if not isinstance(user_message, str) or not user_message.strip() or len(user_message)>1000:
        return jsonify({"response": "Please enter a message."})
    try: return jsonify({"response": agent.ask_input(user_message)})
    except ValueError as exc: return jsonify({"response": str(exc)}), 400


@app.route("/ask", methods=["POST"])
def ask():
    """Query mode — query the KB."""
    data = request.get_json(silent=True)
    if data is None: data = {}
    if not isinstance(data, dict): return jsonify({"response":"Expected a JSON object."}), 400
    user_message = data.get("message", "")
    if not isinstance(user_message, str) or not user_message.strip() or len(user_message)>1000:
        return jsonify({"response": "Please enter a message."})
    try: return jsonify({"response": agent.ask(user_message)})
    except ValueError as exc: return jsonify({"response": str(exc)}), 400


@app.route("/reload", methods=["POST"])
def reload_kb():
    """Reload KB after new facts saved."""
    return jsonify({"response": agent.reload()})


if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=False, port=5000)
