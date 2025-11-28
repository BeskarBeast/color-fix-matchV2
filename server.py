from flask import Flask, request, jsonify, send_from_directory
from PIL import Image, UnidentifiedImageError
import numpy as np
from sklearn.cluster import KMeans
import os
import sys

# ------------------------------
# Initialize Flask app
# ------------------------------
app = Flask(__name__, static_folder='static')

# ------------------------------
# SECURITY: Limit max upload size (5MB)
# ------------------------------
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

# ------------------------------
# SECURITY: Allowed image extensions
# ------------------------------
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename):
    return (
        "." in filename and 
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

# ------------------------------
# Serve static files
# ------------------------------
@app.route('/')
def home():
    return send_from_directory("static", "index.html")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory("static", "favicon.svg", mimetype="image/svg+xml")

# Serve all static files (CSS, JS, images, locales, etc.)
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# ------------------------------
# Color detection endpoint
# ------------------------------
@app.route('/color', methods=['POST'])
def get_color():
    file = request.files.get("image")

    # No file uploaded
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    # SECURITY: Reject non-image extensions
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    try:
        # SECURITY: Catch non-image disguised files
        try:
            img = Image.open(file.stream).convert('RGB')
        except UnidentifiedImageError:
            return jsonify({"error": "Uploaded file is not a valid image"}), 400

        # Load image in original resolution
        arr = np.array(img).reshape(-1, 3)

        # Filter out extreme glare and shadows
        arr_filtered = arr[(arr.max(axis=1) < 240) & (arr.min(axis=1) > 20)]
        if len(arr_filtered) == 0:
            arr_filtered = arr  # fallback

        # Randomly sample pixels if too many for speed
        max_samples = 100000
        if len(arr_filtered) > max_samples:
            idx = np.random.choice(len(arr_filtered), max_samples, replace=False)
            arr_sampled = arr_filtered[idx]
        else:
            arr_sampled = arr_filtered

        # Run K-means clustering
        k = 3
        kmeans = KMeans(n_clusters=k, n_init=5, random_state=42)
        labels = kmeans.fit_predict(arr_sampled)
        centers = kmeans.cluster_centers_

        # Find the largest cluster = dominant color
        unique, counts = np.unique(labels, return_counts=True)
        dominant_cluster = unique[np.argmax(counts)]

        r, g, b = [int(x) for x in centers[dominant_cluster]]
        hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)

        return jsonify({
            "hex": hex_color,
            "rgb": [r, g, b]
        })

    except Exception as e:
        print("SERVER ERROR:", e)  # prints in console, not to user
        return jsonify({"error": "Internal server error"}), 500

# ------------------------------
# Run the server
# ------------------------------
if __name__ == "__main__":
    # Get port from environment variable (Render provides this)
    port = int(os.environ.get("PORT", 8000))
    
    # Read Python version from environment variable
    python_version_env = os.getenv("PYTHON_VERSION", "not set")
    print(f"Environment variable PYTHON_VERSION: {python_version_env}")
    print(f"Actual Python runtime: {sys.version.split()[0]}")

    app.run(host="0.0.0.0", port=port, debug=False)