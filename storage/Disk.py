import os
import cv2

class spaceViewStorage:
    def save(self, frame, spaceID):
        """Save frame as a binary JPEG file."""
        cv2.imwrite(f'spaceViewOf:{spaceID}.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])  # 85% quality

    def get(self,spaceID):
        """Load the latest frame from disk."""
        return cv2.imread(f'spaceViewOf:{spaceID}.jpg') if os.path.exists(f'spaceViewOf:{spaceID}.jpg') else None


class licensePlateStorage:
    def save(self,frame, spaceID):
        """Save frame as a binary JPEG file."""
        cv2.imwrite(f'licensePlateInSpace:{spaceID}.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])  # 85% quality

    def get(self,spaceID):
        """Load the latest frame from disk."""
        return cv2.imread(f'licensePlateInSpace:{spaceID}.jpg') if os.path.exists(f'licensePlateInSpace:{spaceID}.jpg') else None

