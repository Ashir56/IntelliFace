import cv2
import numpy as np
import json
import os
from django.core.files.base import ContentFile
from django.utils import timezone
from apps.users.models import Student, Snapshot, Attendance, Course
from .enhancement import enhance_image

# Try to import ML dependencies with proper error handling
try:
    from insightface.app import FaceAnalysis
    from sklearn.metrics.pairwise import cosine_similarity
    ML_AVAILABLE = True
    print("[INFO] ML dependencies for recognition loaded successfully")
except ImportError as e:
    print(f"[ERROR] Failed to import ML dependencies for recognition: {e}")
    ML_AVAILABLE = False
    FaceAnalysis = None
    cosine_similarity = None


def save_processed_snapshot(snapshot, image, faces, detections, output_dir="processed_snapshots"):
    os.makedirs(os.path.join("media", output_dir), exist_ok=True)

    for face in faces:
        x1, y1, x2, y2 = map(int, face.bbox)
        label = "Unknown"

        for student_id, info in detections.items():
            if info.get("last_embedding") is face.embedding:
                label = f"{info['student'].email} ({info['best_similarity']:.2f})"
                break

        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            image,
            label,
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2
        )

    filename = f"snapshot_{snapshot.id}_processed.jpg"
    path = os.path.join("media", output_dir, filename)
    cv2.imwrite(path, image)

    return f"{output_dir}/{filename}"


def recognize_attendance_from_snapshots_model(lecture=None, course_id=None,user=None, output_folder=None, threshold=0.50):
    """
    Process snapshots from a lecture to automatically mark attendance using face recognition
    """
    try:
        if not lecture:
            return {
                "success": False,
                "message": "No lecture provided"
            }
        
        if not ML_AVAILABLE:
            return {
                "success": False,
                "message": "ML features not available - InsightFace/ONNX Runtime not working"
            }

        # Initialize face analysis app
        print("[INFO] Initializing FaceAnalysis for recognition...")
        app = FaceAnalysis(providers=['CPUExecutionProvider'])
        app.prepare(ctx_id=0, det_size=(640, 640))
        print("[INFO] FaceAnalysis initialized successfully for recognition")

        # Get all students enrolled in the course
        # enrolled_students = Student.objects.filter().exclude(face_embeddings__isnull=True).exclude(face_embeddings='')
        enrolled_students = Student.objects.filter(
            courses__courses_id=course_id  # courses is the related_name in StudentCourses
        ).exclude(face_embeddings__isnull=True).exclude(face_embeddings='')

        if not enrolled_students.exists():
            return {
                "success": False,
                "message": "No students with face embeddings found for this course"
            }

        # Get snapshots for this lecture
        snapshots = Snapshot.objects.filter(lecture=lecture)
        total_snapshots = snapshots.count()

        if total_snapshots == 0:
            return {
                "success": False,
                "message": "No snapshots found for this lecture"
            }

        # Initialize results
        student_detections = {}  # track how many times each student was detected
        processed_snapshots = []

        # Process each snapshot
        for snapshot in snapshots:
            try:
                img_path = snapshot.image.path
                img = cv2.imread(img_path)
                if img is None:
                    print(f"Could not read snapshot: {img_path}")
                    continue

                faces = app.get(img)
                if len(faces) == 0:
                    print(f"No faces detected in snapshot: {snapshot.id}")
                    continue

                for face in faces:
                    face_embedding = face.embedding
                    best_match = None
                    best_similarity = 0

                    for student in enrolled_students:
                        try:
                            student_embeddings = json.loads(student.face_embeddings)
                            for stored_embedding in student_embeddings:
                                similarity = cosine_similarity([face_embedding], [stored_embedding])[0][0]
                                if similarity > best_similarity and similarity >= threshold:
                                    best_similarity = similarity
                                    best_match = student
                        except (json.JSONDecodeError, TypeError) as e:
                            print(f"Invalid embeddings for student {student.email}: {e}")
                            continue

                    if best_match:
                        student_id = str(best_match.id)
                        if student_id not in student_detections:
                            student_detections[student_id] = {
                                'student': best_match,
                                'detections': 0,
                                'best_similarity': 0
                            }

                        student_detections[student_id]['detections'] += 1
                        student_detections[student_id]['best_similarity'] = max(
                            student_detections[student_id]['best_similarity'],
                            best_similarity
                        )
                        student_detections[student_id]['last_embedding'] = face.embedding

                        print(f"[INFO] Detected {best_match.email} with similarity {best_similarity:.3f}")

                save_processed_snapshot(
                    snapshot=snapshot,
                    image=img.copy(),
                    faces=faces,
                    detections=student_detections
                )

                processed_snapshots.append({
                    'snapshot_id': snapshot.id,
                    'faces_detected': len(faces),
                    'timestamp': snapshot.created_at.isoformat()
                })

            except Exception as e:
                print(f"Failed to process snapshot {snapshot.id}: {str(e)}")
                continue

        # Now determine attendance based on >50% presence
        attendance_results = {}
        present_count = 0
        for student in enrolled_students:
            student_id = str(student.id)
            detection_info = student_detections.get(student_id)
            times_detected = detection_info['detections'] if detection_info else 0

            is_present = (times_detected / total_snapshots) > 0.5

            course = Course.objects.get(id=course_id)

            # Create or update attendance record
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                lecture=lecture,
                course=course,
                defaults={'status': 'present' if is_present else 'absent'},
                marked_by=user.teacher
            )
            if not created:
                attendance.status = 'present' if is_present else 'absent'
                attendance.marked_at = timezone.now()
                attendance.save()

            if is_present:
                present_count += 1

            attendance_results[student.email] = {
                'present': is_present,
                'detections': times_detected,
                'total_snapshots': total_snapshots,
                'best_similarity': detection_info['best_similarity'] if detection_info else 0
            }

        attendance_percentage = (present_count / enrolled_students.count() * 100) if enrolled_students.exists() else 0

        print(f"[SUCCESS] Processed {total_snapshots} snapshots, marked attendance for {enrolled_students.count()} students")

        return {
            "success": True,
            "attendance": attendance_results,
            "total_snapshots": total_snapshots,
            "total_students": enrolled_students.count(),
            "present_students": present_count,
            "attendance_percentage": round(attendance_percentage, 2),
            "processed_snapshots": processed_snapshots,
            "threshold_used": threshold,
            "message": f"Successfully processed attendance for {enrolled_students.count()} students"
        }

    except Exception as e:
        print(f"Face recognition failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Face recognition processing failed"
        }
