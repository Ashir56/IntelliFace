import cv2
import numpy as np
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity
from apps.users.models import Student, Snapshot
import os
from django.core.files.base import ContentFile


def recognize_attendance_from_snapshots_model(lecture=None, output_folder=None, threshold=0.50):
    # Fetch snapshots
    if lecture is None:
        snapshots_queryset = Snapshot.objects.all()
    else:
        snapshots_queryset = Snapshot.objects.filter(lecture=lecture)

    # Active students
    students = Student.objects.filter(enrollment_status='active')

    # Store embeddings with Student instance as key
    student_embeddings = {
        student: np.array(student.face_embeddings)
        for student in students if student.face_embeddings
    }

    if not student_embeddings:
        return {
            "attendance": {},
            "total_snapshots": 0,
            "percentage_presence": {},
            "processed_snapshots": []
        }

    # Initialize InsightFace
    app = FaceAnalysis(allowed_modules=['detection', 'recognition'])
    app.prepare(ctx_id=-1, det_size=(640, 640))

    # Create output folder if needed
    if output_folder:
        os.makedirs(output_folder, exist_ok=True)

    # Attendance dictionary now holds Student objects
    attendance = {student: 0 for student in student_embeddings.keys()}

    total_snapshots = 0
    processed_snapshots = []

    # Process each snapshot
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

            # Compare with stored student embeddings
            for student, student_embedding in student_embeddings.items():
                score = cosine_similarity(
                    embedding,
                    student_embedding.reshape(1, -1)
                )[0][0]

                if score > best_score:
                    best_score = score
                    best_match = student

            # Bounding box
            x1, y1, x2, y2 = face.bbox.astype(int)

            # Match decision
            if best_score >= threshold:
                attendance[best_match] += 1

                label = (
                    f"{best_match.first_name} {best_match.last_name} "
                    f"({best_score:.2f})"
                )
                color = (0, 255, 0)
            else:
                label = f"Unknown ({best_score:.2f})"
                color = (0, 0, 255)

            # Draw bounding box
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

            text_y = y1 - 10 if y1 - 10 > 20 else y1 + 20

            cv2.putText(
                img,
                label,
                (x1, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

        # Save processed image to Snapshot.processed_image
        _, buffer = cv2.imencode(".jpg", img)
        processed_bytes = buffer.tobytes()

        snapshot.processed_image.save(
            f"processed_{os.path.basename(img_path)}",
            ContentFile(processed_bytes),
            save=True
        )

    # Calculate presence percentages
    percentage_presence = {
        student: (count / total_snapshots * 100) if total_snapshots > 0 else 0
        for student, count in attendance.items()
    }

    return {
        "attendance": attendance,   # keys = Student instances
        "total_snapshots": total_snapshots,
        "percentage_presence": percentage_presence,
        "processed_snapshots": processed_snapshots
    }
