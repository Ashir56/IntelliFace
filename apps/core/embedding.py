import cv2
import json

# Try to import InsightFace with proper error handling
try:
    from insightface.app import FaceAnalysis
    INSIGHTFACE_AVAILABLE = True
    print("[INFO] InsightFace loaded successfully")
except ImportError as e:
    print(f"[ERROR] Failed to import InsightFace: {e}")
    INSIGHTFACE_AVAILABLE = False
    FaceAnalysis = None

def student_picture_embedding(student):
    """
    Generate face embeddings for a student from their uploaded images
    """
    if not INSIGHTFACE_AVAILABLE:
        print("[WARNING] InsightFace not available - face embedding disabled")
        student.face_embeddings = json.dumps([])
        student.save()
        return {
            "success": False,
            "embeddings_count": 0,
            "message": "InsightFace not available - ML features disabled"
        }
    
    try:
        # Initialize face analysis app with error handling
        print("[INFO] Initializing FaceAnalysis...")
        app = FaceAnalysis(providers=['CPUExecutionProvider'])
        app.prepare(ctx_id=0, det_size=(640, 640))
        print("[INFO] FaceAnalysis initialized successfully")
        
        embeddings = []
        
        for student_image in student.images.all():
            try:
                img_path = student_image.image.path
                img = cv2.imread(img_path)
                
                if img is None:
                    print(f"[WARNING] Could not read image: {img_path}")
                    continue
                
                faces = app.get(img)
                
                if len(faces) == 0:
                    print(f"[WARNING] No faces detected in image: {img_path}")
                    continue
                
                face = max(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
                
                # Get embedding
                embedding = face.embedding.tolist()
                embeddings.append(embedding)
                
                print(f"[INFO] Generated embedding for {student.email} from {img_path}")
                
            except Exception as e:
                print(f"[ERROR] Failed to process image {student_image.image.path}: {str(e)}")
                continue
        
        if embeddings:
            student.face_embeddings = json.dumps(embeddings)
            student.save()
            
            print(f"[SUCCESS] Generated {len(embeddings)} embeddings for {student.email}")
            return {
                "success": True,
                "embeddings_count": len(embeddings),
                "message": f"Successfully generated {len(embeddings)} face embeddings"
            }
        else:
            print(f"[ERROR] No valid embeddings generated for {student.email}")
            return {
                "success": False,
                "embeddings_count": 0,
                "message": "No valid face embeddings could be generated"
            }
            
    except Exception as e:
        print(f"[ERROR] Face embedding failed for {student.email}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Face embedding generation failed"
        }