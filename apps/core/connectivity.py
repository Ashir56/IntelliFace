import cv2
import os
from datetime import datetime

# Camera RTSP
rtsp_url = "rtsp://admin:admin@192.168.0.110:554/cam/realmonitor?channel=1&subtype=0"

# Directory to save snapshots
save_dir = os.path.dirname(os.path.abspath(__file__))

# Open camera stream
cap = cv2.VideoCapture(rtsp_url)
if not cap.isOpened():
    raise Exception("Cannot open RTSP stream")

snapshot_count = 0
taking_snapshots = True  # Set to False when teacher presses "End Attendance"

while taking_snapshots:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        continue

    # Save snapshot
    timestamp = datetime.now().strftime("%H_%M_%S")
    filename = os.path.join(save_dir, f"snapshot_{timestamp}.jpg")
    cv2.imwrite(filename, frame)
    snapshot_count += 1
    print(f"Saved snapshot {snapshot_count}: {filename}")

    # Optional: wait a few seconds between snapshots
    cv2.waitKey(5000)  # 5 seconds

cap.release()

# After this, run your facial recognition on the saved snapshots
