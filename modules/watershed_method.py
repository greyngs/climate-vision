import cv2
import numpy as np

def watershed(image):
    """Segment image using watershed algorithm with snow detection focus"""
    # Convert image to proper format
    if image.dtype != np.uint8:
        image = (image * 255).astype(np.uint8) if image.max() <= 1.0 else image.astype(np.uint8)
    
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    # Enhance contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray_eq = clahe.apply(gray)
    
    # Apply blur to reduce noise
    blurred = cv2.GaussianBlur(gray_eq, (5, 5), 0)
    
    # Apply Otsu threshold for automatic detection
    otsu_thresh, _ = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    
    # Adjust threshold to better detect snow (high values)
    snow_thresh = min(255, otsu_thresh + 30)
    
    # Apply threshold
    _, thresh = cv2.threshold(blurred, snow_thresh, 255, cv2.THRESH_BINARY)
    
    # Morphological operations to clean noise
    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    # Find markers for Watershed
    sure_bg = cv2.dilate(thresh, kernel, iterations=3)
    
    # Enhanced distance transform for more precise markers
    dist_transform = cv2.distanceTransform(thresh, cv2.DIST_L2, 5)
    dist_transform_normalized = cv2.normalize(dist_transform, None, 0, 1.0, cv2.NORM_MINMAX)
    
    # Adaptive threshold for distance transform
    sure_fg_threshold = 0.6 * dist_transform_normalized.max()
    _, sure_fg = cv2.threshold(dist_transform_normalized, sure_fg_threshold, 1.0, cv2.THRESH_BINARY)
    sure_fg = np.uint8(sure_fg * 255)
    
    # Unknown region
    unknown = cv2.subtract(sure_bg, sure_fg)
    
    # Label regions with connected components
    _, markers = cv2.connectedComponents(sure_fg)
    
    # Ensure background is different from 0
    markers = markers + 1
    
    # Mark unknown region with 0
    markers[unknown == 255] = 0
    
    # Prepare image for watershed
    image_watershed = image.copy()
    
    # Apply watershed
    cv2.watershed(image_watershed, markers)
    
    # Draw segmentation contours (in red)
    image_watershed[markers == -1] = [255, 0, 0]
    
    return image_watershed