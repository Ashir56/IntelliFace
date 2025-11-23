import os
import time
from datetime import datetime
import subprocess

rtsp_url = "rtsp://admin:admin%401234@192.168.0.110:554/cam/realmonitor?channel=1&subtype=1"

base_dir = os.path.dirname(os.path.abspath(__file__))
save_dir = os.path.join(base_dir, "snapshots")
os.makedirs(save_dir, exist_ok=True)

SNAPSHOT_INTERVAL = 300

while True:
    timestamp = datetime.now().strftime("%H_%M_%S")
    filename = os.path.join(save_dir, f"snapshot_{timestamp}.jpg")

    cmd = [
        "ffmpeg",
        "-rtsp_transport", "tcp",
        "-i", rtsp_url,
        "-frames:v", "1",
        "-q:v", "2",
        filename,
        "-y"
    ]

    print(f"Capturing snapshot → {filename}")

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("Saved:", filename)

    time.sleep(SNAPSHOT_INTERVAL)