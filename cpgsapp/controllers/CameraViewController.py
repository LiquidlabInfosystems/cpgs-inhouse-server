# Developed By Tecktrio At Liquidlab Infosystems
# Project: Camera Contoller Methods
# Version: 1.0
# Date: 2025-03-08
# Description: A simple Camera Controller to manage camera related activities

# Importing functions
import base64
import json
import time
import cv2
import numpy as np
from cpgsapp.controllers.FileSystemContoller import get_space_coordinates, get_space_info, save_image, update_space_info
from cpgsapp.controllers.HardwareController import free_camera_device, update_pilot
from cpgsapp.controllers.NetworkController import update_server
from cpgsserver.settings import IS_PI_CAMERA_SOURCE
from storage import Variables

#Used for PI camera
if IS_PI_CAMERA_SOURCE:
    from picamera2 import Picamera2
    Variables.cap = Picamera2()
    config = Variables.cap.create_preview_configuration(main={"size":(1280, 720)})
    Variables.cap.configure(config)
    # Variables.cap.set_controls({
    #     "ExposureTime":20000,
    #     "AnalogueGain":8.0,
    #     "Brightness":0.5,
    # })
    Variables.cap.start()
else: Variables.cap = cv2.VideoCapture(0)


def image_to_base64(frame):
    try:
        frame_contiguous = np.ascontiguousarray(frame)
        success, encoded_img = cv2.imencode('.jpg', frame_contiguous)
        if not success:
            print("Failed to encode frame to JPEG")
            return None
        image_bytes = encoded_img.tobytes()
        base64_string = base64.b64encode(image_bytes).decode('utf-8')
        data_url = f"data:image/jpeg;base64,{base64_string}"
        return data_url
    except Exception as e:
        print(f"Error converting frame to base64: {str(e)}")
        return None
    

def image_to_rowbytes(frame):
    try:
        frame_contiguous = np.ascontiguousarray(frame)
        success, encoded_img = cv2.imencode('.jpg', frame_contiguous)
        if not success:
            print("Failed to encode frame to JPEG")
            return None
        image_bytes = encoded_img.tobytes()
        # base64_string = base64.b64encode(image_bytes).decode('utf-8')
        # data_url = f"image_bytes"
        return image_bytes
    except Exception as e:
        print(f"Error converting frame to base64: {str(e)}")
        return None




# Calling functon for license plate detection
def dectect_license_plate(space):
    plate_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml')
    # Load image
    isLicensePlate = False
    # gray = cv2.cvtColor(space, cv2.COLOR_BGR2GRAY)
    license_plate = None
    plates = plate_cascade.detectMultiScale(space, scaleFactor=1.1, minNeighbors=4, minSize=(25, 25))
    for (x, y, w, h) in plates:
        isLicensePlate = True 
        cv2.rectangle(space, (x, y), (x + w, y + h), (0, 255, 0), 2)  
        license_plate = space[y:y+h, x:x+w]
    
    # space  = cv2.cvtColor(space, cv2.COLOR_RGB2GRAY)
    return space, license_plate, isLicensePlate


# Function called for calibrating 
async def video_stream_for_calibrate():
    while True:
        frame  = load_camera_view()
        with open('coordinates.txt','r')as data:
            for space_coordinates in json.load(data):
                    for index in range (0,len(space_coordinates)-1):
                        x1 = int(space_coordinates[index][0])
                        y1 = int(space_coordinates[index][1])
                        x2 = int(space_coordinates[index+1][0])
                        y2 = int(space_coordinates[index+1][1])    
                        cv2.line(frame,(x1,y1),(x2,y2), (0, 255, 0), 2)  
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        encoded_frame = base64.b64encode(frame_bytes).decode('utf-8')
        readyToSendFrame = f"data:image/jpeg;base64,{encoded_frame}"
        yield readyToSendFrame



# Function called for capturing the frames
import cv2
import time

def capture():
    """Synchronous capture function optimized for performance."""
    # print('Camera Started!')
    # while True:
    if IS_PI_CAMERA_SOURCE:
        frame = Variables.cap.capture_array()
        if frame is None:
            print("Failed to capture frame from PiCamera")
            time.sleep(0.5)
            # continue
    else:
        ret, frame = Variables.cap.read()
        # frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        if not ret:
            print("Failed to capture frame from VideoCapture")
            time.sleep(0.1)
            # continue

    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    if frame.size > 0:  # Simplified check
        frame = cv2.resize(frame, (1280 , 720))
        return frame
        # save_image('camera_view', frame)
    else:
        print("Invalid frame received")
    time.sleep(.8)  # Reduced delay



# LOAD CAMERA VIEW 
def load_camera_view(max_attempts=5, delay=0.05):
    # for attempt in range(max_attempts):
        # print('getting image')
        camera_view = capture()
        # camera_view = cv2.imread("storage/camera_view.jpg")
        if camera_view is not None and not camera_view.size == 0:  # Check if image is valid
            return camera_view
        else:
            height, width = 720 , 1280 # Adjust as needed
            blank_image = np.zeros((height, width, 1), dtype=np.uint8)
            return blank_image
      


# Function called for getting the camera view with space coordinates
def get_camera_view_with_space_coordinates():
    frame = load_camera_view()
    with open('storage/coordinates.txt','r')as data:
        for space_coordinates in json.load(data):
                for index in range (0,len(space_coordinates)-1):
                    x1 = int(space_coordinates[index][0])
                    y1 = int(space_coordinates[index][1])
                    x2 = int(space_coordinates[index+1][0])
                    y2 = int(space_coordinates[index+1][1])    
                    cv2.line(frame,(x1,y1),(x2,y2), (0, 255, 0), 2)  
    ret, buffer = cv2.imencode('.jpg', frame)
    frame_bytes = buffer.tobytes()
    return frame_bytes



#Function called to detect license plate
def getSpaceMonitorWithLicensePlateDectection(spaceID, x, y, w, h ):
        camera_view = load_camera_view()
        space_view = camera_view[y:y+h, x:x+w]
        Variables.licensePlateinSpace, Variables.licensePlate, isLicensePlate =  dectect_license_plate(space_view)
        Variables.licensePlateinSpaceInBase64 = image_to_base64(Variables.licensePlateinSpace)
        # Variables.licensePlateinSpaceInBase64 = image_to_rowbytes(Variables.licensePlateinSpace)
        for space in Variables.SPACES:
            if space['spaceID'] == spaceID:
                Variables.licensePlateBase64 = ""
                if isLicensePlate:
                    Variables.licensePlateBase64 = image_to_base64(Variables.licensePlate)
                    # Variables.licensePlateBase64 = image_to_rowbytes(Variables.licensePlate)
                    space['spaceStatus'] = "occupied"
                space['spaceFrame'] = Variables.licensePlateinSpaceInBase64
                space['licensePlate'] = Variables.licensePlateBase64
        update_space_info(Variables.SPACES)
        return isLicensePlate


# Function to start live mode and detect the available license plates
def liveMode():
    '''
    SCAN the parking slot FOR VEHICLE
    '''      
    poslist = get_space_coordinates()
    Variables.SPACES = []
    Variables.TOTALSPACES = len(poslist)
    for spaceID in range(Variables.TOTALSPACES):
        obj = {
            'spaceID':spaceID,
            'spaceStatus':'vaccant',
            'spaceFrame':'',
            'licenseNumber':"",
            'licensePlate':""
        }
        Variables.SPACES.append(obj)
    update_space_info(Variables.SPACES)
    for spaceID, pos in enumerate(poslist):
        SpaceCoordinates = np.array([[pos[0][0], pos[0][1]], [pos[1][0], pos[1][1]], [pos[2][0], pos[2][1]], [pos[3][0], pos[3][1]]])
        pts = np.array(SpaceCoordinates, np.int32)
        x, y, w, h = cv2.boundingRect(pts)
        isLicensePlate = getSpaceMonitorWithLicensePlateDectection(spaceID, x, y, w, h)
    if IS_PI_CAMERA_SOURCE:
        update_pilot()
    if isLicensePlate:
        update_server()


# Function used to monitor the spaces
def get_monitoring_spaces():
    '''
    SCAN the parking slot FOR VEHICLE
    '''      
    poslist = get_space_coordinates()
    Variables.SPACES = []
    Variables.TOTALSPACES = len(poslist)
    for spaceID in range(Variables.TOTALSPACES):
        obj = {
            'spaceID':spaceID,
            'spaceStatus':'vaccant',
            'spaceFrame':'',
            'licenseNumber':"",
            'licensePlate':""
        }
        Variables.SPACES.append(obj)
    Variables.LAST_SPACES = get_space_info()        
    update_space_info(Variables.SPACES)

    for spaceID, pos in enumerate(poslist):
        SpaceCoordinates = np.array([[pos[0][0], pos[0][1]], [pos[1][0], pos[1][1]], [pos[2][0], pos[2][1]], [pos[3][0], pos[3][1]]])
        pts = np.array(SpaceCoordinates, np.int32)
        x, y, w, h = cv2.boundingRect(pts)
        isLicensePlate = getSpaceMonitorWithLicensePlateDectection(spaceID, x, y, w, h)
        if IS_PI_CAMERA_SOURCE:
            update_pilot()
        if isLicensePlate:
            update_server()

    return get_space_info()



# def auto_calibrate(frame):
#     frameInGray = cv2.cvtColor((frame), cv2.COLOR_BGR2GRAY)
#     frameInGrayAndBlur = cv2.GaussianBlur(frameInGray, (3, 3), 2)
#     with open("config.json","rb") as configurations:
#         config = json.load(configurations)
#         configuration_data = {
#             "CameraFilterThresh" : config["threshold"],
#             "serverIP" :config["server_ip"],
#             "serverPort" : config["server_port"],
#             "DEBUG" : config["DEBUG"],
#             "CameraFilterMaximumThresh" : 255,
#             "CameraFilterThreshOnCalibrate" : config["threshold"],
#             "CameraFilterMaximumThreshOnCalibrate" : 255,
#             "BoostThreshAT":2,
#         }
#     _,ThreshHoldedFrame  = cv2.threshold(frameInGrayAndBlur,
#                                             configuration_data["CameraFilterThreshOnCalibrate"], 
#                                             configuration_data["CameraFilterMaximumThreshOnCalibrate"], 
#                                             cv2.THRESH_BINARY_INV)
#     imgmedian = cv2.medianBlur(ThreshHoldedFrame, 3 )
#     kernal = np.ones((3, 3), np.uint8)
#     imgdilate = cv2.dilate(imgmedian, kernel=kernal, iterations=configuration_data["BoostThreshAT"])
#     contours, _ = cv2.findContours(imgdilate, cv2.INTER_AREA, cv2.CHAIN_APPROX_SIMPLE)
#     self.coordinate_data = []
#     for slotIndex, contour in enumerate(contours):
#         area = cv2.contourArea(contour)
#         perimeter = cv2.arcLength(contour, True)
#         area_threshold = 500
#         perimeter_threshold = 200
#         if area > area_threshold and perimeter > perimeter_threshold:
#             epsilon = 0.02 * perimeter 
#             approx_polygon = cv2.approxPolyDP(contour, epsilon, True)
#             x, y, w, h = cv2.boundingRect(approx_polygon)
#             if len(approx_polygon) == 4 and h > w :
#                 corners = [tuple(coord[0]) for coord in approx_polygon]
#                 vector1 = (corners[1][0] - corners[0][0], corners[1][1] - corners[0][1])
#                 vector2 = (corners[2][0] - corners[1][0], corners[2][1] - corners[1][1])
#                 dot_product = sum(a * b for a, b in zip(vector1, vector2))
#                 magnitude1 = math.sqrt(sum(a * a for a in vector1))
#                 magnitude2 = math.sqrt(sum(b * b for b in vector2))
#                 cosine_angle = dot_product / (magnitude1 * magnitude2)
#                 angle = math.degrees(math.acos(cosine_angle))
#                 if angle >70 and angle <110:
#                     self.coordinate_data.append(corners)
#     with open('coordinates.txt','w') as coordinates:
#             json.dump(self.coordinates, coordinate, indent=4)

