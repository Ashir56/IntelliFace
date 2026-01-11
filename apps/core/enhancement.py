import cv2
import numpy as np
import os

def enhance_image(img):

    try:
        # Convert to grayscale for processing
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced_gray = clahe.apply(gray)
        
        # Convert back to BGR
        enhanced = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2BGR)
        
        # Apply bilateral filter for noise reduction while preserving edges
        enhanced = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        # Sharpen the image
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        enhanced = cv2.filter2D(enhanced, -1, kernel)
        
        return enhanced
        
    except Exception as e:
        print(f"[ERROR] Image enhancement failed: {str(e)}")
        return img  # Return original image if enhancement fails


def enhance_snapshots(input_folder, output_folder):
    """
    Enhance all snapshots in a folder for better face recognition
    """
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        enhanced_count = 0
        
        for filename in os.listdir(input_folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                input_path = os.path.join(input_folder, filename)
                output_path = os.path.join(output_folder, filename)
                
                # Read image
                img = cv2.imread(input_path)
                if img is None:
                    print(f"[WARNING] Could not read image: {input_path}")
                    continue
                
                # Enhance image
                enhanced_img = enhance_image(img)
                
                # Save enhanced image
                cv2.imwrite(output_path, enhanced_img)
                enhanced_count += 1
                
                print(f"[INFO] Enhanced: {filename}")
        
        print(f"[SUCCESS] Enhanced {enhanced_count} images")
        return {
            "success": True,
            "enhanced_count": enhanced_count,
            "message": f"Successfully enhanced {enhanced_count} images"
        }
        
    except Exception as e:
        print(f"[ERROR] Snapshot enhancement failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Snapshot enhancement failed"
        }