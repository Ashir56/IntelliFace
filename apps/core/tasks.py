from celery import shared_task
from django.utils import timezone

from .utils import capture_snapshot
from ..users.models import Lecture

@shared_task
def capture_snapshots_for_active_lectures():
    active_lectures = Lecture.objects.filter(end_time__isnull=True)
    results = []
    
    for lecture in active_lectures:
        lecture_results = []
        
        for camera in lecture.class_ref.cameras.all():
            try:
                result = capture_snapshot(camera, lecture)
                lecture_results.append(f"Captured snapshot for camera {camera.id}")
            except Exception as e:
                lecture_results.append(f"Error capturing from camera {camera.id}: {str(e)}")
        
        results.append({
            'lecture_id': lecture.id,
            'results': lecture_results
        })
    
    return {
        "message": "Snapshot capture task completed (no recognition processing)",
        "results": results,
        "processed_lectures": len(active_lectures)
    }


@shared_task
def process_lecture_attendance(lecture_id):
    try:
        lecture = Lecture.objects.get(id=lecture_id)
        result = recognize_attendance_from_snapshots_model(lecture=lecture)
        
        return {
            "success": True,
            "lecture_id": lecture_id,
            "result": result
        }
    except Lecture.DoesNotExist:
        return {
            "success": False,
            "error": f"Lecture {lecture_id} not found"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }