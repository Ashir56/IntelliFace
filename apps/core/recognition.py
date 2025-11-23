import cv2
import numpy as np
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity
from apps.users.models import Student, Snapshot
from django.conf import settings
import os

def recognize_attendance_from_snapshots_model(lecture=None, output_folder=None, threshold=0.50):
    snapshot_queryset = None
    if lecture is None:
        snapshots_queryset = Snapshot.objects.all()
    else:
        snapshots_queryset = Snapshot.objects.filter(lecture=lecture)

    # Load student embeddings from DB
    students = Student.objects.filter(enrollment_status='active')
    student_embeddings = {
        f"{s.first_name} {s.last_name}": np.array(s.face_embeddings)
        for s in students if s.face_embeddings
    }

    if not student_embeddings:
        return {"attendance": {}, "total_snapshots": 0, "percentage_presence": {}, "processed_snapshots": []}

    app = FaceAnalysis(allowed_modules=['detection', 'recognition'])
    app.prepare(ctx_id=-1, det_size=(640, 640))

    # Prepare output folder
    if output_folder:
        os.makedirs(output_folder, exist_ok=True)

    # Attendance tracking
    attendance = {name: 0 for name in student_embeddings.keys()}
    total_snapshots = 0
    processed_snapshots = []

    for snapshot in snapshots_queryset:
        img_path = snapshot.image.path
        img = cv2.imread(img_path)
        if img is None:
            continue

        faces = app.get(img)
        if len(faces) == 0:
            continue

        total_snapshots += 1
        processed_snapshots.append(snapshot.id)

        for face in faces:
            embedding = face.embedding.reshape(1, -1)
            best_match = None
            best_score = -1

            for student_name, student_embedding in student_embeddings.items():
                score = cosine_similarity(embedding, student_embedding.reshape(1, -1))[0][0]
                if score > best_score:
                    best_score = score
                    best_match = student_name

            box = face.bbox.astype(int)
            x1, y1, x2, y2 = box

            if best_score > threshold:
                attendance[best_match] += 1
                label = f"{best_match} ({best_score:.2f})"
                color = (0, 255, 0)
            else:
                label = f"Unknown ({best_score:.2f})"
                color = (0, 0, 255)

            if output_folder:
                cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        if output_folder:
            output_path = os.path.join(output_folder, os.path.basename(img_path))
            cv2.imwrite(output_path, img)

    percentage_presence = {
        student: (count / total_snapshots * 100) if total_snapshots > 0 else 0
        for student, count in attendance.items()
    }

    return {
        "attendance": attendance,
        "total_snapshots": total_snapshots,
        "percentage_presence": percentage_presence,
        "processed_snapshots": processed_snapshots
    }
