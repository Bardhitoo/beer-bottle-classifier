import io
import os
import sys
import time
import threading
from PIL import Image
import requests

# Configuration
FLASK_APP_URL = 'http://localhost:5000/classify'  
API_KEY = 'some-secure-api'  # Replace with your actual API key
TOTAL_REQUESTS = 200  # Total number of requests to send
CONCURRENT_THREADS = 10  # Number of concurrent threads
REQUESTS_PER_THREAD = 20  # Number of requests each thread will send

# Statistics
lock = threading.Lock()
success_count = 0
rate_limited_count = 0
other_errors = 0

def generate_image(format='JPEG'):
    """Generate an in-memory image and return it as bytes."""
    img = Image.new('RGB', (100, 100), color = (73, 109, 137))
    img_bytes_io = io.BytesIO()
    img.save(img_bytes_io, format=format)
    img_bytes_io.seek(0)
    return img_bytes_io

def send_request(thread_id, request_id):
    global success_count, rate_limited_count, other_errors
    # Alternate between JPEG and PNG
    image_format = 'JPEG' if request_id % 2 == 0 else 'PNG'
    img_bytes_io = generate_image(format=image_format)
    files = {
        'file': ('test_image.' + image_format.lower(), img_bytes_io, 'image/' + image_format.lower())
    }
    headers = {
        'X-API-Key': API_KEY
    }
    try:
        response = requests.post(FLASK_APP_URL, files=files, headers=headers)
        with lock:
            if response.status_code == 200:
                success_count += 1
                print(f"[Thread {thread_id}] Request {request_id}: Success (200)")
            elif response.status_code == 429:
                rate_limited_count += 1
                print(f"[Thread {thread_id}] Request {request_id}: Rate Limited (429)")
            else:
                other_errors += 1
                print(f"[Thread {thread_id}] Request {request_id}: Error ({response.status_code}) - {response.text}")
    except requests.exceptions.RequestException as e:
        with lock:
            other_errors += 1
        print(f"[Thread {thread_id}] Request {request_id}: Exception - {e}")

def worker(thread_id, num_requests):
    for i in range(1, num_requests + 1):
        send_request(thread_id, i)
        time.sleep(0.1)

def main():
    global success_count, rate_limited_count, other_errors
    threads = []
    start_time = time.time()

    print(f"Starting rate limiter test with {TOTAL_REQUESTS} total requests using {CONCURRENT_THREADS} threads.")

    for thread_id in range(1, CONCURRENT_THREADS + 1):
        t = threading.Thread(target=worker, args=(thread_id, REQUESTS_PER_THREAD))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end_time = time.time()
    duration = end_time - start_time

    print("\n=== Test Summary ===")
    print(f"Total Requests Sent: {CONCURRENT_THREADS * REQUESTS_PER_THREAD}")
    print(f"Successful Responses (200): {success_count}")
    print(f"Rate Limited Responses (429): {rate_limited_count}")
    print(f"Other Errors: {other_errors}")
    print(f"Total Duration: {duration:.2f} seconds")
    print("====================\n")

    if success_count <= 10 and rate_limited_count >= TOTAL_REQUESTS - 10:
        print("Rate limiter is functioning as expected.")
    else:
        print("Rate limiter may not be functioning correctly.")

if __name__ == "__main__":
    # Optional: Allow API key and URL to be set via command-line arguments
    if len(sys.argv) > 1:
        API_KEY = sys.argv[1]
    if len(sys.argv) > 2:
        FLASK_APP_URL = sys.argv[2]
    main()
