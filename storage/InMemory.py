import threading


class InMemory:
    def __init__(self):
        self.base64_frame = None  # Stores the latest frame as a base64 string
        self.lock = threading.Lock()

    def update_base64(self, base64_frame):
        """Store a frame as a base64-encoded string in memory."""
        # Encode frame to JPEG bytes
        with self.lock:
            self.base64_frame = base64_frame  # Store in RAM

    def get_base64(self):
        """Retrieve the base64-encoded frame."""
        with self.lock:
            return self.base64_frame if self.base64_frame is not None else None