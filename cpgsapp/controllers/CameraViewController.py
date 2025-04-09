# Developed By Tecktrio At Liquidlab Infosystems
# Project: Camera Contoller Methods
# Version: 1.0
# Date: 2025-03-08
# Description: A simple Camera Controller to manage camera related activities

# Importing functions
import base64
import json
import time
from cpgsapp.models import SpaceInfo
from cpgsapp.utils import FixedFIFO
import cv2
import numpy as np
from cpgsapp.controllers.FileSystemContoller import get_space_coordinates, get_space_info, update_space_info
from cpgsapp.controllers.HardwareController import  update_pilot
from cpgsapp.controllers.NetworkController import update_server
from cpgsserver.settings import CONFIDENCE_LEVEL, CONSISTENCY_LEVEL, IS_PI_CAMERA_SOURCE
from storage import Variables


# Camera Input Setup
if IS_PI_CAMERA_SOURCE:
    from picamera2 import Picamera2
    Variables.cap = Picamera2()
    config = Variables.cap.create_preview_configuration(main={"size":(1280, 720)})
    Variables.cap.configure(config)
    Variables.cap.start()
else: Variables.cap = cv2.VideoCapture(0)

# queque = FixedFIFO(CONSISTENCY_LEVEL)


# helps in converting image from cv2 metrix to base64
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
    


# helps in decting license plate in the current frame
def dectect_license_plate(space):
    plate_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml') 
    isLicensePlate = False
    license_plate = None
    plates = plate_cascade.detectMultiScale(space, scaleFactor=1.1, minNeighbors=4, minSize=(25, 25))
    for (x, y, w, h) in plates:
        isLicensePlate = True 
        cv2.rectangle(space, (x, y), (x + w, y + h), (0, 255, 0), 2)  
        license_plate = space[y:y+h, x:x+w]
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



# helps in capturing the frame from physical camera
def capture():
    """Synchronous capture function optimized for performance."""
    if IS_PI_CAMERA_SOURCE:
        frame = Variables.cap.capture_array()
        if frame is None:
            print("Failed to capture frame from PiCamera")
            time.sleep(0.5)
    else:
        ret, frame = Variables.cap.read()
        if not ret:
            print("Failed to capture frame from VideoCapture")
            time.sleep(0.1)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    if frame.size > 0:
        frame = cv2.resize(frame, (1280 , 720))
        return frame
    else:
        print("Invalid frame received")
    time.sleep(.8)



# LOAD CAMERA VIEW 
def load_camera_view(max_attempts=5, delay=0.05):
        camera_view = capture()
        if camera_view is not None and not camera_view.size == 0: 
            return camera_view
        else:
            height, width = 720 , 1280 
            blank_image = np.zeros((height, width, 1), dtype=np.uint8)
            return blank_image
      


# Function called for getting the camera view with space coordinates
def get_camera_view_with_space_coordinates():
    frame = load_camera_view()
    with open('storage/coordinates.txt', 'r') as data:
        for space_coordinates in json.load(data):
            for index in range (0,len(space_coordinates)-1):
                x1 = int(space_coordinates[index][0])
                y1 = int(space_coordinates[index][1])
                x2 = int(space_coordinates[index+1][0])
                y2 = int(space_coordinates[index+1][1])    
                cv2.line(frame,(x1,y1),(x2,y2), (255, 255, 255), 3)  
        points = Variables.points
        if len(points)>1:
            for index in range (0,len(points)-1):
                x1 = int(points[index][0])
                y1 = int(points[index][1])
                x2 = int(points[index+1][0])
                y2 = int(points[index+1][1])    
                cv2.line(frame,(x1,y1),(x2,y2), (255, 255, 255), 3)  
    ret, buffer = cv2.imencode('.jpg', frame)
    frame_bytes = buffer.tobytes()
    return frame_bytes



#Function called to detect license plate
def getSpaceMonitorWithLicensePlateDectection(spaceID, x, y, w, h ):
        camera_view = load_camera_view()
        spaceObject  = SpaceInfo.objects.get(spaceID = spaceID)
        space_view = camera_view[y:y+h, x:x+w]
        licensePlateinSpace, licensePlate, isLicensePlate =  dectect_license_plate(space_view)
        if isLicensePlate:
            spaceObject.spaceStatus =   "occupied"
            spaceObject.licensePlate =  image_to_base64(licensePlate)
            spaceObject.spaceFrame =  image_to_base64(space_view)
        else:
            spaceObject.spaceStatus =   "vaccant"
            spaceObject.spaceFrame =  image_to_base64(space_view)
        spaceObject.save()
        return isLicensePlate



# Function to start live mode and detect the available license plates
def liveMode():
    '''
    SCAN the parking slot FOR VEHICLE
    '''      
    poslist = get_space_coordinates()
    Variables.TOTALSPACES = len(poslist)
    for spaceID in range(Variables.TOTALSPACES):
        if len(Variables.CONFIDENCE_QUEUE) != Variables.TOTALSPACES:
            Variables.CONFIDENCE_QUEUE.append(FixedFIFO(CONSISTENCY_LEVEL))
    for spaceID, pos in enumerate(poslist):
        SpaceCoordinates = np.array([[pos[0][0], pos[0][1]], [pos[1][0], pos[1][1]], [pos[2][0], pos[2][1]], [pos[3][0], pos[3][1]]])
        pts = np.array(SpaceCoordinates, np.int32)
        x, y, w, h = cv2.boundingRect(pts)
        isLicensePlate = getSpaceMonitorWithLicensePlateDectection(spaceID, x, y, w, h)
        Variables.CONFIDENCE_QUEUE[spaceID].enqueue(isLicensePlate)
        queue = Variables.CONFIDENCE_QUEUE[spaceID].get_queue()
        Occupied_count = queue.count(True)
        Vaccency_count = queue.count(False)
        Occupied_confidence = int((Occupied_count/CONSISTENCY_LEVEL)*100)
        Vaccency_confidence = int((Vaccency_count/CONSISTENCY_LEVEL)*100)
        monitoring_spaces = get_space_info()
        current_space = monitoring_spaces[spaceID]
        
        
        if Occupied_confidence == CONFIDENCE_LEVEL:
            current_space_status = current_space['spaceStatus']
            current_licensePlate = current_space['licensePlate']
            update_server(spaceID, current_space_status, current_licensePlate)
            if IS_PI_CAMERA_SOURCE:
                update_pilot(current_licensePlate)
        
        elif Vaccency_confidence == CONFIDENCE_LEVEL:
            current_space_status = current_space['spaceStatus']
            current_licensePlate = current_space['licensePlate']
            update_server(spaceID, current_space_status, current_licensePlate)
            if IS_PI_CAMERA_SOURCE:
                update_pilot(current_licensePlate)
              
    
    return get_space_info()





# Function used to monitor the spaces
def get_monitoring_spaces():
    '''
    SCAN the parking slot FOR VEHICLE
    '''      
    poslist = get_space_coordinates()
    Variables.TOTALSPACES = len(poslist)
    for spaceID in range(Variables.TOTALSPACES):
        if len(Variables.CONFIDENCE_QUEUE) != Variables.TOTALSPACES:
            Variables.CONFIDENCE_QUEUE.append(FixedFIFO(CONSISTENCY_LEVEL))
    for spaceID, pos in enumerate(poslist):
        SpaceCoordinates = np.array([[pos[0][0], pos[0][1]], [pos[1][0], pos[1][1]], [pos[2][0], pos[2][1]], [pos[3][0], pos[3][1]]])
        pts = np.array(SpaceCoordinates, np.int32)
        x, y, w, h = cv2.boundingRect(pts)
        isLicensePlate = getSpaceMonitorWithLicensePlateDectection(spaceID, x, y, w, h)
        Variables.CONFIDENCE_QUEUE[spaceID].enqueue(isLicensePlate)
        queue = Variables.CONFIDENCE_QUEUE[spaceID].get_queue()
        Occupied_count = queue.count(True)
        Vaccency_count = queue.count(False)
        Occupied_confidence = int((Occupied_count/CONSISTENCY_LEVEL)*100)
        Vaccency_confidence = int((Vaccency_count/CONSISTENCY_LEVEL)*100)
        monitoring_spaces = get_space_info()
        current_space = monitoring_spaces[spaceID]
        
        
        if Occupied_confidence == CONFIDENCE_LEVEL:
            current_space_status = current_space['spaceStatus']
            current_licensePlate = current_space['licensePlate']
            update_server(spaceID, current_space_status, current_licensePlate)
            if IS_PI_CAMERA_SOURCE:
                update_pilot(current_licensePlate)
        
        elif Vaccency_confidence == CONFIDENCE_LEVEL:
            current_space_status = current_space['spaceStatus']
            current_licensePlate = current_space['licensePlate']
            update_server(spaceID, current_space_status, current_licensePlate)
            if IS_PI_CAMERA_SOURCE:
                update_pilot(current_licensePlate)
              
    
    return get_space_info()


