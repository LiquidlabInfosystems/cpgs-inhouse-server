# Developed By Tecktrio At Liquidlab Infosystems
# Project: StartLive methods
# Version: 1.0
# Date: 2025-03-08
# Description: Runs to start the camera frames from when the server starts

# startup_watcher.py
import socket
import time
import requests

# from controllers.HardwareController import free_camera_device
import socket
import time
import requests

SERVER_IP = "0.0.0.0"  # Replace with your actual public IP
PORT = 8000

# print("Initiate Program V1, Waiting for the server to start!")

while True:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect((SERVER_IP, PORT))
            # print(f"Server is up on {SERVER_IP}:{PORT}")

        # Send request after confirming server is up
        try:
            response = requests.get(f"http://{SERVER_IP}:{PORT}/initiate", timeout=2)
            text_art = """
            /////  //////   //////     //////
            //     //  //   //         //
            //     //////   //  /////  ///////
            //     //       //  // //       //
            /////  //       ////// //  ///////
            """                  

            print(text_art)


            # print(f"Initiation Response: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request failed: {e}")

        break  # Exit loop once successful

    except (ConnectionRefusedError, socket.timeout):
        # print(f"Waiting for server on {SERVER_IP}:{PORT}...")
        time.sleep(1)  # Retry every second

