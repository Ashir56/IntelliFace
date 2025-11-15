# import subprocess
# import shlex
# import cv2
# import numpy as np
# import os
# import insightface
#
# # ========================
# # CONFIGURATION
# # ========================
# NVR_RTSP_URL = "rtsp://admin:hik%40786786@192.168.0.103:554/Streaming/Channels/201"
# OUTPUT_CLIP = "nvr_clip.mp4"
# CLIP_DURATION = 10  # seconds
#
# # ========================
# # STEP 1 — Download short clip from NVR using ffmpeg
# # ========================
# def download_nvr_clip(rtsp_url, duration, output_path):
#     print(f"[INFO] Downloading {duration}s clip from NVR...")
#     cmd = f'ffmpeg -rtsp_transport tcp -i "{rtsp_url}" -t {duration} -an -c copy -y "{output_path}"'
#     process = subprocess.run(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     if process.returncode != 0:
#         print("[ERROR] ffmpeg failed:", process.stderr.decode()[:300])
#         raise RuntimeError("ffmpeg error")
#     print(f"[INFO] Clip saved to {output_path}")
# #
# # # ========================
# # # STEP 2 — Load InsightFace model
# # # ========================
# # def load_insightface_model():
# #     print("[INFO] Loading InsightFace model...")
# #     app = insightface.app.FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
# #     app.prepare(ctx_id=0)
# #     return app
# #
# # # ========================
# # # STEP 3 — Load known embeddings
# # # ========================
# # def load_known_faces():
# #     # Replace this section with your actual saved embeddings and names
# #     known_faces = []
# #     known_names = []
# #     if os.path.exists("known_faces.npz"):
# #         data = np.load("known_faces.npz", allow_pickle=True)
# #         known_faces = data["embeddings"]
# #         known_names = data["names"]
# #         print(f"[INFO] Loaded {len(known_faces)} known faces")
# #     else:
# #         print("[WARN] No known face data found.")
# #     return known_faces, known_names
# #
# # # ========================
# # # STEP 4 — Process video with InsightFace
# # # ========================
# # def process_video(video_path, app, known_faces, known_names, threshold=0.4):
# #     cap = cv2.VideoCapture(video_path)
# #     if not cap.isOpened():
# #         print("[ERROR] Cannot open video.")
# #         return
# #
# #     frame_idx = 0
# #     while True:
# #         ret, frame = cap.read()
# #         if not ret:
# #             break
# #
# #         faces = app.get(frame)
# #         for face in faces:
# #             bbox = face.bbox.astype(int)
# #             embedding = face.embedding
# #
# #             name = "Unknown"
# #             if len(known_faces) > 0:
# #                 # Compute cosine similarity
# #                 sims = np.dot(known_faces, embedding) / (
# #                     np.linalg.norm(known_faces, axis=1) * np.linalg.norm(embedding)
# #                 )
# #                 best_idx = np.argmax(sims)
# #                 if sims[best_idx] > threshold:
# #                     name = known_names[best_idx]
# #
# #             # Draw bounding box
# #             cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
# #             cv2.putText(frame, f"{name}", (bbox[0], bbox[1] - 10),
# #                         cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
# #
# #         cv2.imshow("InsightFace Recognition", frame)
# #         if cv2.waitKey(1) & 0xFF == ord('q'):
# #             break
# #
# #         frame_idx += 1
# #
# #     cap.release()
# #     cv2.destroyAllWindows()
# #
# # # ========================
# # # MAIN EXECUTION
# # # ========================
# if __name__ == "__main__":
#     # Step 1: Download short video clip
#     download_nvr_clip(NVR_RTSP_URL, CLIP_DURATION, OUTPUT_CLIP)
#
#     # Step 2: Load InsightFace
#     # app = load_insightface_model()
#     #
#     # # Step 3: Load your known embeddings
#     # known_faces, known_names = load_known_faces()
#     #
#     # # Step 4: Run recognition on the clip
#     # process_video(OUTPUT_CLIP, app, known_faces, known_names)



# Correct Approach



# import cv2
# import subprocess
# import numpy as np
#
# rtsp_url = "rtsp://admin:hik%40786786@192.168.0.103:554/Streaming/Channels/201"
#
# ffmpeg_cmd = [
#     'ffmpeg',
#     '-rtsp_transport', 'tcp',
#     '-i', rtsp_url,
#     '-f', 'rawvideo',  # output raw frames
#     '-pix_fmt', 'bgr24',  # compatible with OpenCV
#     '-'
# ]
#
# width, height = 1920, 1080
# frame_size = width * height * 3
#
# proc = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10 ** 8)
#
# while True:
#     raw_frame = proc.stdout.read(frame_size)
#     if len(raw_frame) != frame_size:
#         print("Frame size mismatch, stopping")
#         break
#     frame = np.frombuffer(raw_frame, np.uint8).reshape((height, width, 3))
#
#     cv2.imshow("Live NVR Feed", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# proc.terminate()
# cv2.destroyAllWindows()


from insightface.app import FaceAnalysis
import cv2
import subprocess
import numpy as np

# Initialize InsightFace detection (RetinaFace)
app = FaceAnalysis(allowed_modules=['detection', 'recognition'])
app.prepare(ctx_id=-1, det_thresh=0.5, det_size=(640, 640))

rtsp_url = "rtsp://admin:hik%40786786@192.168.0.103:554/Streaming/Channels/201"
ffmpeg_cmd = [
    'ffmpeg', '-rtsp_transport', 'tcp', '-i', rtsp_url,
    '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'
]

width, height = 1920, 1080
frame_size = width * height * 3

proc = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)

while True:
    raw_frame = proc.stdout.read(frame_size)
    if len(raw_frame) != frame_size:
        break

    frame = np.frombuffer(raw_frame, np.uint8).reshape((height, width, 3))

    frame = frame.copy()

    faces = app.get(frame)
    for face in faces:
        x1, y1, x2, y2 = map(int, face.bbox)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    cv2.imshow("Live Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

proc.terminate()
cv2.destroyAllWindows()
