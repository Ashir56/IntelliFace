# import cv2
#
# url = "http://webcam.st-malo.com/axis-cgi/mjpg/video.cgi"
#
# cap = cv2.VideoCapture(url)
#
# if not cap.isOpened():
#     print("Failed to connect to camera stream.")
#     exit()
#
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("Failed to grab frame.")
#         break
#
#     cv2.imshow("IP Camera Stream", frame)
#
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# cap.release()
# cv2.destroyAllWindows()
# ip_camera_url = 'http://161.6.70.78/mjpg/video.mjpg'
#
# cap = cv2.VideoCapture(ip_camera_url)
#
# if not cap.isOpened():
#     print("[ERROR] Cannot open video stream from IP camera")
#     exit()
#
# print("[INFO] Starting video stream... Press 'q' to quit")
#
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("[WARNING] Failed to grab frame")
#         break
#
#     # Display the frame in a window
#     cv2.imshow("IP Camera Video", frame)
#
#     # Press 'q' to exit the window
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# # Cleanup
# cap.release()
# cv2.destroyAllWindows()




import cv2

cam = cv2.VideoCapture("http://88.53.197.250/axis-cgi/mjpg/video.cgi?resolution=320x240")

cv2.namedWindow("test")

img_counter = 0

while True:
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break
    cv2.imshow("test", frame)

    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        img_name = "opencv_frame_{}.png".format(img_counter)
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        img_counter += 1

cam.release()

cv2.destroyAllWindows()