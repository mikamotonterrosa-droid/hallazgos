import os
from flask import Flask, request, send_file

app = Flask(__name__)

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@app.route("/")
def index():
    return send_file(os.path.join(REPO_DIR, "landing-dietas.html"))

@app.route("/api/current-plan", methods=["POST"])
def generate_plan():
    # Aquí irá la lógica de generación del PDF
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
