# Source image (grab from dockerhub)
FROM ultralytics/ultralytics:latest

# Set the working directory inside the container
WORKDIR /app

# Bring the script to container
COPY . .

# Install packages
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y libmagic1 libmagic-dev && rm -rf /var/lib/apt/lists/*

# Expose the port Flask will run on
EXPOSE 5000

# Environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the Flask app
CMD ["python", "app.py"]
