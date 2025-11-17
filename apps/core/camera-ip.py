from onvif import ONVIFCamera

# Replace with your camera IP and credentials
camera_ip = '192.168.0.110'  # your camera IP
username = 'admin'
password = 'admin@1234'
port = 80

# Connect to camera via ONVIF
camera = ONVIFCamera(camera_ip, port, username, password)

# Create media service object to retrieve stream URI
media_service = camera.create_media_service()

# Get profiles (most cameras have at least one)
profiles = media_service.GetProfiles()
profile = profiles[0]

# Get the RTSP stream URI
stream_uri = media_service.GetStreamUri({
    'StreamSetup': {'Stream': 'RTP-Unicast', 'Transport': {'Protocol': 'RTSP'}},
    'ProfileToken': profile.token
})

rtsp_url = stream_uri.Uri
print("RTSP URL:", rtsp_url)
