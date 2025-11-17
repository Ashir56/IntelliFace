from insightface.app import FaceAnalysis
import cv2
import numpy as np
import os

# -----------------------------
# 1. Initialize InsightFace
# -----------------------------
app = FaceAnalysis(allowed_modules=['detection', 'recognition'])
app.prepare(ctx_id=-1, det_thresh=0.5, det_size=(320, 320))  # smaller size = faster

# -----------------------------
# 2. Load known face from picture
# -----------------------------
# Replace "person.jpg" with your file name
reference_image_path = "moizz.jpg"
if not os.path.exists(reference_image_path):
    print(f"Error: {reference_image_path} not found")
    exit()

ref_img = cv2.imread(reference_image_path)
faces_in_ref = app.get(ref_img)

if len(faces_in_ref) == 0:
    print("Error: No face detected in reference image")
    exit()

# Get embedding of the first face in the image
known_embedding = faces_in_ref[0].embedding
known_faces = {"Person": known_embedding}  # you can change the name

RECOGNITION_THRESHOLD = 50  # distance threshold

# -----------------------------
# 3. RTSP URL (substream for low latency)
# -----------------------------
rtsp_url = "rtsp://admin:admin%401234@192.168.0.110:554/cam/realmonitor?channel=1&subtype=1"

# -----------------------------
# 4. Open camera
# -----------------------------
cap = cv2.VideoCapture(rtsp_url)
if not cap.isOpened():
    print("Error: Cannot open camera stream")
    exit()

# -----------------------------
# 5. Recognition loop
# -----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        print("Warning: Empty frame received")
        break

    frame_copy = frame.copy()
    faces = app.get(frame_copy)

    for face in faces:
        x1, y1, x2, y2 = map(int, face.bbox)

        # Draw bounding box
        cv2.rectangle(frame_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Recognition
        embedding = face.embedding
        name = "Unknown"
        dist = np.linalg.norm(embedding - known_embedding)
        print(dist)
        if dist < RECOGNITION_THRESHOLD:
            name = "Moizz"  # same as known_faces key

        # Put name on frame
        cv2.putText(frame_copy, name, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # Show video
    cv2.imshow("Live Recognition", frame_copy)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# -----------------------------
# 6. Cleanup
# -----------------------------
cap.release()
cv2.destroyAllWindows()
