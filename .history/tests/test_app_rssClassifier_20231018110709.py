import requests
import time
import json

BASE_URL = "http://127.0.0.1:5003"

# Define your custom classes and threshold here
CLASSES = ["News", "Entertainment", "Sports", "Economy", "Technology", "Science", "Stock Market", "Reviews", "Business", "Finance"] # Replace with your desired classes
THRESHOLD = 0.76  # Replace with your desired threshold

def trigger_classification(classes, threshold):
    response = requests.get(f"{BASE_URL}/classify", params={"classes": json.dumps(classes), "threshold": threshold})
    try:
        data = response.json()
        if response.status_code == 200:
            print(data["message"])
        else:
            print(f"Error triggering classification: {data['error']}")
    except ValueError:  # JSON decoding failed
        print(f"Unexpected server response: {response.text}")

def poll_status():
    while True:
        response = requests.get(f"{BASE_URL}/status")
        try:
            data = response.json()
            print(f"Status: {data['status']}, Number of entries classified: {data['num_classified']}")

            # Print start_time and current_runtime
            if data['start_time']:
                formatted_start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['start_time']))
                print(f"Start Time: {formatted_start_time}")
            if data['current_runtime']:
                print(f"Current Runtime: {data['current_runtime']:.2f} seconds")

            if data['status'] == 'idle':
                break
        except ValueError:  # JSON decoding failed
            print(f"Unexpected server response: {response.text}")
            break
        time.sleep(1)

if __name__ == '__main__':
    trigger_classification(CLASSES, THRESHOLD)
    poll_status()