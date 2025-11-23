import cv2
import os
import numpy as np

def enhance_image(img):
    # Convert to LAB for better contrast handling
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # CLAHE contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)

    # Merge and convert back
    lab = cv2.merge((l, a, b))
    img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    # Sharpening filter
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    img = cv2.filter2D(img, -1, kernel)

    # Denoise
    img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

    return img


def enhance_snapshots(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    supported = {".jpg", ".jpeg", ".png"}

    for filename in os.listdir(input_folder):
        if not any(filename.lower().endswith(ext) for ext in supported):
            continue

        img_path = os.path.join(input_folder, filename)
        img = cv2.imread(img_path)

        if img is None:
            print(f"[ERROR] Failed to read {img_path}")
            continue

        enhanced_img = enhance_image(img)

        output_path = os.path.join(output_folder, filename)
        cv2.imwrite(output_path, enhanced_img)

        print(f"[ENHANCED] {filename} → {output_path}")

    print("\n[DONE] All snapshots enhanced successfully.")


# Example usage
input_folder = "snapshots"
output_folder = "snapshots_enhanced"

enhance_snapshots(input_folder, output_folder)
