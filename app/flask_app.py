from flask import Flask, request, jsonify
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "data", "uploads")


@app.route("/health", methods=["GET"])
def health():
    return {"status": "OK", "service": "spark_flask_log_app"}


@app.route("/upload-logs", methods=["POST"])
def upload_logs():
    if "file" not in request.files:
        return {"error": "No file part in the request"}, 400

    file = request.files["file"]
    if file.filename == "":
        return {"error": "No selected file"}, 400

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)

    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "saved_to": save_path
    }, 200


@app.route("/process", methods=["POST"])
def process():
    """Trigger Spark cleaning on uploaded file"""
    from app.spark_service import clean_and_save
    filename = request.json.get("filename") if request.json else None
    if not filename:
        return {"error": "Provide filename in JSON body"}, 400

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return {"error": f"File {filename} not found in uploads"}, 404

    result = clean_and_save(file_path)
    return result, 200


@app.route("/summary", methods=["GET"])
def summary():
    from app.spark_service import get_summary
    return jsonify(get_summary())


@app.route("/top-attackers", methods=["GET"])
def top_attackers():
    from app.spark_service import get_top_attackers
    limit = request.args.get("limit", 20, type=int)
    return jsonify(get_top_attackers(limit))


@app.route("/targeted-urls", methods=["GET"])
def targeted_urls():
    from app.spark_service import get_targeted_urls
    limit = request.args.get("limit", 20, type=int)
    return jsonify(get_targeted_urls(limit))


@app.route("/direct-access", methods=["GET"])
def direct_access():
    from app.spark_service import get_direct_access
    limit = request.args.get("limit", 15, type=int)
    return jsonify(get_direct_access(limit))


@app.route("/rate-analysis", methods=["GET"])
def rate_analysis():
    from app.spark_service import get_rate_analysis
    limit = request.args.get("limit", 20, type=int)
    return jsonify(get_rate_analysis(limit))


if __name__ == "__main__":
    app.run(debug=True)