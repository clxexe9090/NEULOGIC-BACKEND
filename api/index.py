from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase_config import get_supabase

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return jsonify({"status": "Backend connected 🚀"})

@app.route("/test-db")
def test_db():
    try:
        supabase = get_supabase()
        response = supabase.table("sensor_data").select("*").limit(1).execute()

        return jsonify({
            "status": "Database connected ✅",
            "data": response.data
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route("/insert-test", methods=["POST"])
def insert_test():
    try:
        supabase = get_supabase()

        data = {
            "gsr": 35.5,
            "pulse": 80,
            "timestamp": 1710000000
        }

        response = supabase.table("sensor_data").insert(data).execute()

        return jsonify({
            "inserted": response.data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500