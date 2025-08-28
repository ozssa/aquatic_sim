import cv2
import numpy as np
import os
import platform

def remove_white_background(input_path="aquatic_sim/assets/input/fish.jpg", output_path="aquatic_sim/assets/output/fish_transparent.png", threshold=240):
    """
    Enhanced background removal with multiple techniques
    """
    if platform.system() == "Emscripten":
        print("⚠️ Image processing skipped in Pyodide environment")
        return True
    
    try:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Image {input_path} not found")
        
        img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise FileNotFoundError(f"Failed to read {input_path}")
        
        print(f"Processing image: {input_path}")
        print(f"Image size: {img.shape}")

        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
        elif len(img.shape) == 3 and img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        elif len(img.shape) == 3 and img.shape[2] == 4:
            pass
        else:
            raise ValueError(f"Unsupported image format: {img.shape}")

        success = _remove_by_color_threshold(img, threshold, output_path)
        if success:
            return True
        
        success = _remove_by_edge_detection(img, output_path)
        if success:
            return True
        
        success = _remove_by_adaptive_threshold(img, output_path)
        return success
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def _remove_by_color_threshold(img, threshold, output_path):
    """Method 1: Simple color thresholding"""
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
        
        kernel = np.ones((3,3), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return False

        largest_contour = max(contours, key=cv2.contourArea)
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [largest_contour], -1, 255, -1)
        
        mask = cv2.GaussianBlur(mask, (3, 3), 0)
        img[:, :, 3] = mask
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, img)
        print(f"✅ Method 1 succeeded: {output_path}")
        return True
        
    except Exception as e:
        print(f"Method 1 failed: {e}")
        return False

def _remove_by_edge_detection(img, output_path):
    """Method 2: Edge detection based removal"""
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        kernel = np.ones((3,3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=2)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return False
            
        largest_contour = max(contours, key=cv2.contourArea)
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [largest_contour], -1, 255, -1)
        
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=3)
        img[:, :, 3] = mask
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, img)
        print(f"✅ Method 2 succeeded: {output_path}")
        return True
        
    except Exception as e:
        print(f"Method 2 failed: {e}")
        return False

def _remove_by_adaptive_threshold(img, output_path):
    """Method 3: Adaptive thresholding"""
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        adaptive_thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        kernel = np.ones((5,5), np.uint8)
        adaptive_thresh = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)
        adaptive_thresh = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(adaptive_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return False
            
        min_area = img.shape[0] * img.shape[1] * 0.01
        valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]
        
        if not valid_contours:
            return False
            
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, valid_contours, -1, 255, -1)
        
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        img[:, :, 3] = mask
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, img)
        print(f"✅ Method 3 succeeded: {output_path}")
        return True
        
    except Exception as e:
        print(f"Method 3 failed: {e}")
        return False

def enhance_fish_image(input_path, output_path=None):
    """
    Enhance fish image for better animation
    """
    if platform.system() == "Emscripten":
        print("⚠️ Image enhancement skipped in Pyodide environment")
        return True
    
    if output_path is None:
        name, ext = os.path.splitext(input_path)
        output_path = f"{name}_enhanced{ext}"
    
    try:
        img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            return False
            
        lab = cv2.cvtColor(img[:,:,:3], cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        if img.shape[2] == 4:
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_BGR2BGRA)
            enhanced[:,:,3] = img[:,:,3]
        
        cv2.imwrite(output_path, enhanced)
        print(f"✅ Enhanced image saved: {output_path}")
        return True
        
    except Exception as e:
        print(f"Enhancement failed: {e}")
        return False

if __name__ == "__main__" and platform.system() != "Emscripten":
    input_file = "aquatic_sim/assets/input/fish.jpg"
    output_file = "aquatic_sim/assets/output/fish_transparent.png"
    
    if remove_white_background(input_file, output_file):
        print("✅ Processing completed successfully!")
        enhance_fish_image(output_file, "aquatic_sim/assets/output/fish_enhanced.png")
    else:
        print("❌ Processing failed!")