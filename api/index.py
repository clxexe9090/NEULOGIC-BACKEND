from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client
import os
import time

app = Flask(__name__)
CORS(app)

# =========================
# Supabase connection
# =========================
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Supabase environment variables not set")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# Routes
# =========================
@app.route("/")
def root():
    return {
        "service": "NeuroLab API",
        "status": "running"
    }

@app.route("/health")
def health():
    return {
        "status": "ok",
        "timestamp": int(time.time())
    }

@app.route("/v1/data", methods=["POST"])
def receive_data():
    payload = request.get_json()

    if not payload:
        return {"error": "Invalid JSON"}, 400

    required = ["device_id", "gsr", "sound", "accel"]

    for field in required:
        if field not in payload:
            return {"error": f"Missing field {field}"}, 400

    device_id = str(payload["device_id"])
    gsr = float(payload["gsr"])
    sound = float(payload["sound"])
    accel = float(payload["accel"])

    stress_index = round(
        0.4 * gsr +
        0.3 * sound +
        0.3 * accel,
        4
    )

    alert = None
    if stress_index > 0.7:
        alert = "Possible overstimulation detected"

    supabase.table("sensor_data").insert({
        "device_id": device_id,
        "gsr": gsr,
        "sound": sound,
        "accel": accel,
        "stress_index": stress_index,
        "timestamp": int(time.time())
    }).execute()

    return {
        "status": "stored",
        "stress_index": stress_index,
        "alert": alert
    }, 201


# 👇 NECESARIO EN VERCEL
handler = app