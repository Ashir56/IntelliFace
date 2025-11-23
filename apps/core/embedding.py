import cv2
from insightface.app import FaceAnalysis

def student_picture_embedding(student):
    app = FaceAnalysis(allowed_modules=['detection', 'recognition'])
    app.prepare(ctx_id=-1, det_size=(640, 640))
    face_embedding = []

    for stu in student.images.all():
        image = stu.image.path
        img = cv2.imread(image)

        faces = app.get(img)
        if len(faces) == 0:
            print(f"⚠️ No face detected")
            continue

        face = faces[0]
        embedding = face.embedding
        face_embedding.append(embedding.tolist())

    student.face_embeddings = face_embedding

    student.save()

