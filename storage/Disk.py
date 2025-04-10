import os
import cv2

def save_frame_to_binary(frame, file_path="spaceview.jpg"):
    """Save frame as a binary JPEG file."""
    cv2.imwrite(file_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])  # 85% quality

def load_frame_from_binary(file_path="spaceview.jpg"):
    """Load the latest frame from disk."""
    return cv2.imread(file_path) if os.path.exists(file_path) else None