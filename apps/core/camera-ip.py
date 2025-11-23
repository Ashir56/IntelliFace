from onvif import ONVIFCamera


def get_camera_ip_address(camera=None):
    camera_ip = '192.168.0.110'
    username = 'admin'
    password = 'admin@1234'
    port = 80

    camera = ONVIFCamera(camera_ip, port, username, password)

    media_service = camera.create_media_service()

    profiles = media_service.GetProfiles()
    profile = profiles[0]

    stream_uri = media_service.GetStreamUri({
        'StreamSetup': {'Stream': 'RTP-Unicast', 'Transport': {'Protocol': 'RTSP'}},
        'ProfileToken': profile.token
    })

    rtsp_url = stream_uri.Uri
    print("RTSP URL:", rtsp_url)


get_camera_ip_address()