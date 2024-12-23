import io
import magic  
from scripts.utils import load_yolo, logger
from flask import Flask, request, jsonify, send_from_directory, abort
from PIL import Image
from werkzeug.utils import secure_filename
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__, static_folder='static', static_url_path='')

# Configure maximum file size (e.g., 16 MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 Megabytes

# Initialize rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"] 
    )

# Load the YOLO model
model = load_yolo("./model_files/best.pt", device='')

# Define allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """Check if the file has one of the allowed extensions."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_mime(file_stream):
    """Validate the MIME type of the uploaded file."""
    mime = magic.from_buffer(file_stream.read(1024), mime=True)
    file_stream.seek(0)  # Reset file pointer after reading
    return mime in {'image/png', 'image/jpg', 'image/jpeg'}


@app.route('/classify', methods=['POST'])
@limiter.limit("50 per minute") 
def classify():
    logger.info("Received request to /classify")
    
    # Check if the post request has the file part
    if 'file' not in request.files:
        logger.warning("No file part in the request.")
        return jsonify({"error": "No file provided."}), 400
    
    file = request.files['file']
    
    # If user does not select file, browser may submit an empty part without filename
    if file.filename == '':
        logger.warning("No filename provided in the request.")
        return jsonify({"error": "No filename provided."}), 400
    
    # Validate file extension
    if not allowed_file(file.filename):
        logger.warning(f"Unsupported file extension: {file.filename}")
        return jsonify({"error": "Unsupported file type. Only PNG, JPG, and JPEG are allowed."}), 400
    
    # Validate MIME type
    if not validate_mime(file.stream):
        logger.warning(f"Unsupported MIME type for file: {file.filename}")
        return jsonify({"error": "Unsupported MIME type. Only PNG, JPG, and JPEG are allowed."}), 400
    
    # Secure the filename
    filename = secure_filename(file.filename)
    logger.info(f"Processing file: {filename}")
    
    try:
        # Read the image
        img_bytes = file.read()
        logger.info("Image read successfully.")

        # Open the image with PIL
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        logger.info(f"Image size: {img.size}")

    except Exception as e:
        logger.error(f"Error processing the image file: {e}")
        return jsonify({"error": "Invalid image file."}), 400

    # Run inference
    try:
        results = model.predict(img)
    except Exception as e:
        logger.error(f"Model prediction failed: {e}")
        return jsonify({"error": "Model inference error."}), 500

    # Check if there are any results
    if not results:
        logger.warning("No predictions returned by the model.")
        return jsonify({"error": "No predictions found."}), 200 

    # Take the first / highest confidence result
    highest_conf_pred = results[0]
    logger.info(f"Highest Confidence Prediction: {highest_conf_pred}")

    # Extract information from YOLO (class_name, probability)
    try:
        top_class_id = highest_conf_pred.probs.top1
        top_class_name = highest_conf_pred.names[top_class_id]
        top_conf = highest_conf_pred.probs.top1conf.tolist()
    except Exception as e:
        logger.error(f"Error extracting prediction data: {e}")
        return jsonify({"error": "Error extracting prediction data."}), 500

    response = {
        "bottle_status": top_class_name,
        "confidence": top_conf
    }

    logger.info(f"Prediction: {top_class_name.upper()} with confidence {top_conf}")
    return jsonify(response), 200

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file size limit error."""
    logger.warning("Uploaded file is too large.")
    return jsonify({"error": "File is too large. Maximum size allowed is 16 MB."}), 413

@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded error."""
    logger.warning("Rate limit exceeded.")
    return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
