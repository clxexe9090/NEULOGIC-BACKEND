from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase_config import get_supabase
import time

app = Flask(__name__)
CORS(app)

# ==============================
# Health Check
# ==============================
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "NeuroLab Backend Running "
    })


# ==============================
# Receive IoT Data
# ==============================
@app.route("/api/v1/data", methods=["POST"])
def receive_data():
    try:
        supabase = get_supabase()

        payload = request.get_json()

        if not payload:
            return jsonify({"error": "No JSON received"}), 400

        required_fields = ["device_id", "gsr", "sound", "accel"]

        for field in required_fields:
            if field not in payload:
                return jsonify({"error": f"Missing field: {field}"}), 400

        device_id = payload["device_id"]
        gsr = float(payload["gsr"])
        sound = float(payload["sound"])
        accel = float(payload["accel"])
        timestamp = int(time.time())

        # ==============================
        # Normalization (basic)
        # ==============================
        gsr_norm = min(max(gsr, 0), 1)
        sound_norm = min(max(sound, 0), 1)
        accel_norm = min(max(accel, 0), 1)

        # ==============================
        # Stress Index Calculation
        # ==============================
        stress_index = (
            0.4 * gsr_norm +
            0.3 * sound_norm +
            0.3 * accel_norm
        )

        # ==============================
        # Crisis Detection
        # ==============================
        alert = None
        if stress_index > 0.7:
            alert = "Possible overstimulation detected"

        # ==============================
        # Insert into Database
        # ==============================
        insert_data = {
            "device_id": device_id,
            "gsr": gsr_norm,
            "sound": sound_norm,
            "accel": accel_norm,
            "stress_index": stress_index,
            "timestamp": timestamp
        }

        response = supabase.table("sensor_data").insert(insert_data).execute()

        return jsonify({
            "status": "Data stored",
            "stress_index": stress_index,
            "alert": alert
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# Export for Vercel
handler = app