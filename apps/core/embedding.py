import cv2
from insightface.app import FaceAnalysis
import json

def student_picture_embedding(student):
    try:
        app = FaceAnalysis(providers=['CPUExecutionProvider'])
        app.prepare(ctx_id=0, det_size=(640, 640))
        
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
            
            print(f"Generated {len(embeddings)} embeddings for {student.email}")
            return {
                "success": True,
                "embeddings_count": len(embeddings),
                "message": f"Successfully generated {len(embeddings)} face embeddings"
            }
        else:
            print(f"No valid embeddings generated for {student.email}")
            return {
                "success": False,
                "embeddings_count": 0,
                "message": "No valid face embeddings could be generated"
            }
            
    except Exception as e:
        print(f"Face embedding failed for {student.email}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Face embedding generation failed"
        }