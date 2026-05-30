from flask import Flask
from flask import request, jsonify
import pickle

# Load model
with open("project_one_model.pkl", "rb") as f_in:
    dv, model = pickle.load(f_in)

app = Flask("Predict")


# Health endpoint for Kubernetes probes
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


# Prediction endpoint
@app.route("/predict", methods=["POST"])
def predict():
    candidate = request.get_json()

    X = dv.transform(candidate)

    preds = model.predict_proba(X)[:, 1]

    placement = preds > 0.5

    result = {
        "Placement_Probability": float(preds[0]),
        "Placement": bool(placement[0])
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=9696
    )