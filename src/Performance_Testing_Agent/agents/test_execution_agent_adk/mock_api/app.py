from flask import Flask, jsonify, request
import time

app = Flask(__name__)


@app.route("/api/v1/payment", methods=["POST"])
def payment():
    data = request.get_json(silent=True) or {}

    amount = data.get("amount")
    upi_id = data.get("upiId")
    transaction_id = data.get("transactionId")

    if not amount or not upi_id or not transaction_id:
        return jsonify({
            "status": "failed",
            "message": "Missing required payment fields"
        }), 400

    # Simulate small processing time
    time.sleep(0.01)

    return jsonify({
        "status": "success",
        "message": "Payment processed successfully",
        "transactionId": transaction_id
    }), 200


@app.route("/api/v1/payment/failure", methods=["POST"])
def payment_failure():
    """
    Controlled failure endpoint used to test
    k6 failure detection and error handling.
    """

    time.sleep(0.01)

    return jsonify({
        "status": "failed",
        "message": "Simulated payment gateway failure"
    }), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "UP"
    }), 200


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8000,
        debug=False
    )