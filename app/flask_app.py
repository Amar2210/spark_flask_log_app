"""
===========================================================
FLASK BASICS - LEARNING VERSION
-----------------------------------------------------------
This file is intentionally heavily commented so that you
can revisit it later and understand every piece.
===========================================================
"""

# ---------------------------------------------------------
# 1) IMPORT FLASK CLASS
# ---------------------------------------------------------
# 'flask'  -> is the library (package)
# 'Flask'  -> is a class inside that library
# We import the class so we can create our web application.
# ---------------------------------------------------------
from flask import Flask, request
import os

# ---------------------------------------------------------
# 2) CREATE THE FLASK APPLICATION OBJECT
# ---------------------------------------------------------
# Flask(...) creates a new web application.
#
# __name__ tells Flask:
# "This current file (flask_app.py) is the starting point
#  of my application."
#
# Flask uses this information internally to:
# - locate files
# - understand project structure (later, when we add templates/static)
#
# You can think of this line as:
# "Create a Flask app whose home is this file."
# ---------------------------------------------------------
app = Flask(__name__)

# ---------------------------------------------------------
# 3) DEFINE A ROUTE (ENDPOINT)
# ---------------------------------------------------------
# @app.route is a DECORATOR.
#
# It tells Flask:
# "Whenever someone makes a GET request to /health,
#  run the function named 'health'."
#
# Internally, Flask stores something like:
# {
#   "/health": reference_to_health_function
# }
#
# IMPORTANT:
# YOU DO NOT CALL health() YOURSELF.
# Flask will call it automatically when /health is visited.
# ---------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    """
    This function defines what should happen when
    someone visits: http://127.0.0.1:5000/health

    You:
      - Just define the function.
    Flask:
      - Calls this function when the route is hit.
    """

    # We return a Python dictionary.
    # Flask automatically converts this to JSON before
    # sending it back to the browser / client.
    return {
        "status": "OK",                 # Indicates service is running
        "service": "spark_flask_log_app" # Name of our application
    }

# ---------------------------------------------------------
# 4) START THE WEB SERVER
# ---------------------------------------------------------
# __name__ is a special Python variable.
#
# If you run THIS file directly:
#   python app/flask_app.py
#
# then inside this file:
#   __name__ == "__main__"
#
# Meaning: "I am the main program being executed."
#
# In that case, we WANT to start the Flask server.
#
# If this file is IMPORTED in another script:
#   from app.flask_app import app
#
# then:
#   __name__ != "__main__"
#
# Meaning: "Do NOT start the server automatically."
#
# This prevents accidental server starts when we
# just want to reuse 'app' in another file.
# ---------------------------------------------------------
# if __name__ == "__main__":

#     # app.run() actually starts the web server.
#     #
#     # debug=True means:
#     # - Automatic reload when code changes
#     # - Better error messages in the browser
#     #
#     # By default, Flask will run on:
#     # http://127.0.0.1:5000
#     app.run(debug=True)

"""
---------------------------------------------------------
MENTAL MODEL SUMMARY (KEEP THIS IN MIND)
---------------------------------------------------------

1. app = Flask(__name__)
   -> Create a Flask web application based in this file.

2. @app.route("/health")
   -> Register the function 'health' to be called when
      someone visits /health.

3. def health():
   -> The actual logic that runs when /health is hit.

4. app.run()
   -> Starts the web server so your app can receive requests.

5. if __name__ == "__main__":
   -> "Only start the server if I run THIS file directly."

6. WHO CALLS health()?
   -> FLASK calls it, NOT you.
---------------------------------------------------------
"""


# Define base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define upload folder path
UPLOAD_FOLDER = os.path.join(BASE_DIR, "data", "uploads")

# ---------------------------------------------------------
# NEW ENDPOINT: POST /upload-logs
# ---------------------------------------------------------
@app.route("/upload-logs", methods=["POST"])
def upload_logs():
    """
    What this endpoint does:
    1. Receives a file from the client
    2. Saves it inside data/uploads/
    3. Returns a success message
    """

    # Check if a file was actually sent
    if "file" not in request.files:
        return {
            "error": "No file part in the request"
        }, 400   # 400 = Bad Request

    file = request.files["file"]

    # If user submitted empty file
    if file.filename == "":
        return {
            "error": "No selected file"
        }, 400

    # Create full file path
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)

    # Save the file
    file.save(save_path)

    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "saved_to": save_path
    }, 200  # 200 = Success

if __name__ == "__main__":
    app.run(debug=True)
