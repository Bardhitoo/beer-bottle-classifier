from locust import HttpUser, TaskSet, task, between

class UserBehavior(TaskSet):
    @task
    def classify_image(self):
        # Generate a simple in-memory image
        from PIL import Image
        import io

        img = Image.new('RGB', (100, 100), color=(73, 109, 137))
        img_bytes_io = io.BytesIO()
        img.save(img_bytes_io, format='JPEG')
        img_bytes_io.seek(0)

        files = {
            'file': ('test_image.jpg', img_bytes_io, 'image/jpeg')
        }
        headers = {
            'X-API-Key': 'your-secure-api-key'  # Replace with your actual API key
        }

        self.client.post("/classify", files=files, headers=headers)

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(0, 0.001)  # Minimal wait time to maximize throughput
