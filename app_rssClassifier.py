import os
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

import yaml
import json
import threading
from flask import Flask, jsonify, request
from  rssClassifier import classify_titles_from_db
import time


app = Flask(__name__)

CONFIG_PATH = "./config.yaml"

# Load config from config.yaml
with open(CONFIG_PATH, 'r') as file:
    config = yaml.safe_load(file)


DATABASE_PATH = config['database']['sqlite_path']

DEFAULT_CLASSES = ["Breaking News", "Entertainment", "Sports", "Economy", "Technology", "Science", "Stock Market"]
DEFAULT_THRESHOLD = 0.77

# Status variables
status = "idle"
num_classified = 0
start_time = None  # Add this line

num_classified_lock = threading.Lock()

def increment_classified_count():
    global num_classified
    with num_classified_lock:
        num_classified += 1

def run_classification(classes, threshold):
    global status, num_classified, start_time
    start_time = time.time()  # Update the start_time when the classification starts

    try:
        classify_titles_from_db(DATABASE_PATH, classes, threshold, increment_func=increment_classified_count)

    except Exception as e:
        print(f"Error during classification: {e}")
    finally:
        status = "idle"

@app.route('/classify', methods=['GET'])
def classify_entries():
    global status

    if status == "running":
        return jsonify({"message": "Classification is already in progress!"}), 409

    status = "running"
    
    # Get classes and threshold from query parameters, or use defaults
    classes = request.args.get('classes', DEFAULT_CLASSES, type=json.loads)
    threshold = request.args.get('threshold', DEFAULT_THRESHOLD, type=float)
    
    # Start the classification in a separate thread
    threading.Thread(target=run_classification, args=(classes, threshold)).start()

    return jsonify({"message": "Classification started successfully!"}), 200

@app.route('/status', methods=['GET'])
def get_status():
    current_runtime = None
    if status == "running" and start_time:
        current_runtime = time.time() - start_time

    return jsonify({
        "status": status,
        "num_classified": num_classified,
        "start_time": start_time,  # Return start_time
        "current_runtime": current_runtime  # Return current runtime
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
