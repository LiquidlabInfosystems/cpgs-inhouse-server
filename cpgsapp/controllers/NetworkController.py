# Developed By Tecktrio At Liquidlab Infosystems
# Project: Network Contoller Methods
# Version: 1.0
# Date: 2025-03-08
# Description: A simple Network Controller to manage network related activities


# Importing functions
import socket
import subprocess
import time

from requests import request
from cpgsapp.controllers.FileSystemContoller import get_space_info
from cpgsapp.models import NetworkSettings
from cpgsapp.serializers import NetworkSettingsSerializer
from storage import Variables

def chunk_data(image_data, chunk_size):
    chunks = []
    for i in range(0, len(image_data), chunk_size):
        chunks.append(image_data[i:i+chunk_size])
    return chunks



def send_chunks(ip, port, chunks):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    total_chunks = len(chunks)
    for i, chunk in enumerate(chunks):
        # Add metadata (e.g., chunk number and total chunk count)
        metadata = f"{i+1}/{total_chunks}".encode('utf-8')
        message = metadata + b"|" + chunk
        sock.sendto(message, (ip, port))  # Send each chunk to the receiver
        print(f"Sent chunk {i+1}/{total_chunks}")
    sock.close()




def update_server():
    """Detects changes in space status and updates the main server."""
    current_spaces = get_space_info()
    if current_spaces != {}:
        NetworkSetting = NetworkSettings.objects.first()
        last_spaces = Variables.LAST_SPACES

        
        # changed_space = None
        for space in range(Variables.TOTALSPACES):
            # if space in current_spaces and space in last_spaces:
            if current_spaces[space]['spaceStatus'] != last_spaces[space]['spaceStatus']:
                sd = current_spaces[space]
                data_to_send = {
                    "spaceID": sd['spaceID'],
                    "spaceStatus": sd['spaceStatus'],
                    "licensePlate": sd['licensePlate']
                }
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # print("server setting: ",NetworkSetting.server_ip, NetworkSetting.server_port)
                CHUNK_SIZE = 20
                MESSAGE = f"{data_to_send}".encode()    
                chunks = chunk_data(MESSAGE, CHUNK_SIZE)
                for chuck in chunks:
                    sock.sendto(chuck, (NetworkSetting.server_ip, NetworkSetting.server_port))
                sock.close()
                print("Dectection update send to server - spaceID : ",data_to_send['spaceID'], ", status : ",data_to_send['spaceStatus'], ", server Address : ", NetworkSetting.server_ip, ":", NetworkSetting.server_port)
                break




def change_hostname(new_hostname):
    try:
        commands = [
            f'echo "{new_hostname}" | sudo tee /etc/hostname',
            f'sudo sed -i "s/127.0.1.1.*/127.0.1.1\t{new_hostname}/" /etc/hosts',
            f'sudo hostnamectl set-hostname {new_hostname}'
        ]
        for cmd in commands:
            result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
            print(f"Command: {cmd}")
            print(f"Output: {result.stdout}")
            print(f"Error (if any): {result.stderr}")
        # print(f"Hostname successfully changed to {new_hostname}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error changing hostname: {e}")
        print(f"Output: {e.output}")
        print(f"Error: {e.stderr}")
        return False


# Function to set a static IP
def set_static_ip(data):
    """Configures a static IP address."""
    try:
        nmcli_commands = [
            f"nmcli con modify {data['connection_name']} ipv4.addresses {data['static_ip']}",
            f"nmcli con modify {data['connection_name']} ipv4.gateway {data['gateway_ip']}",
            f"nmcli con modify {data['connection_name']} ipv4.dns {data['dns_ip']}",
            f"nmcli con modify {data['connection_name']} ipv4.method manual",
            f"nmcli con down {data['connection_name']}",
            f"nmcli con up {data['connection_name']}"
        ]
        for cmd in nmcli_commands:
            subprocess.run(cmd, shell=True, check=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error setting static IP: {e}")
        return False


# Function to set a dynamic IP
def set_dynamic_ip(data):
    """Configures a dynamic IP address."""
    try:
        nmcli_commands = [
            f"nmcli con modify {data['connection_name']} ipv4.method auto",
            f"nmcli con down {data['connection_name']}",
            f"nmcli con up {data['connection_name']}"
        ]
        for cmd in nmcli_commands:
            subprocess.run(cmd, shell=True, check=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error setting dynamic IP: {e}")
        return False


# Function to get network settings
def get_network_settings():
    """Retrieves the current network settings."""
    settings = NetworkSettings.objects.first()
    return NetworkSettingsSerializer(settings).data if settings else {}


# Function to save network settings
def saveNetworkSetting(new_settings):
    """Saves new network settings and applies them."""
    try:
        command = f"""
        nmcli con modify $(nmcli -g UUID con show --active | head -n 1) \
        ipv4.method manual \
        ipv4.addresses {new_settings.ipv4_address}/24 \
        ipv4.gateway {new_settings.gateway_address} \
        ipv4.dns "8.8.8.8 8.8.4.4"
        """
        subprocess.run(["sudo", "bash", "-c", command], check=True, text=True)
        connection_name = "preconfigured"
        subprocess.run(["sudo", "nmcli", "connection", "down", connection_name], check=True, text=True)
        subprocess.run(["sudo", "nmcli", "connection", "up", connection_name], check=True, text=True)
        subprocess.run(["sudo", "reboot", "now"], check=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error saving network settings: {e}")


# SCAN WIFI
def scan_wifi():
    """Scans for available WiFi networks and returns a list of SSIDs."""
    try:
        subprocess.run("sudo nmcli dev wifi rescan", shell=True, check=True, text=True)
        time.sleep(2)
        result = subprocess.run(
            "nmcli -f SSID dev wifi list",
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        output_lines = result.stdout.strip().split('\n')[1:]
        ssids = list(set(line.strip() for line in output_lines if line.strip()))
        return ssids
    except subprocess.CalledProcessError as e:
        print(f"Error scanning WiFi networks: {e}")
        return []



# CONNEC TO THE WIFI
def connect_to_wifi(ssid, password):
    """Connects to a WiFi network and enables autoconnect after scanning."""
    available_ssids = scan_wifi()
    if not available_ssids:
        print("No WiFi networks found or scanning failed.")
        return 401
    # print(f"Available networks: {', '.join(available_ssids)}")
    if ssid not in available_ssids:
        print(f"Error: Network '{ssid}' not found in scan results.")
        return 401
    try:
       # Step 1: Connect to the WiFi network
        connect_cmd = f'sudo nmcli dev wifi connect "{ssid}" password "{password}"'
        result = subprocess.run(connect_cmd, shell=True, check=True, text=True, capture_output=True)
        print(f"Ready to Connect with WiFi: {ssid}")
        
        # Step 3: Modify the connection to enable autoconnect using the UUID
        modify_cmd = f'sudo nmcli connection modify "preconfigured" connection.autoconnect yes'
        subprocess.run(modify_cmd, shell=True, check=True, text=True)
        print(f"Autoconnect enabled for {ssid}")
     
    except subprocess.CalledProcessError as e:
        print(f"Error connecting to WiFi: {e}")


