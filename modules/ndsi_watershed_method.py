import cv2
import numpy as np

def ndsi_watershed(ndsi_image):
    """
    Specialized watershed segmentation function for NDSI (Normalized Difference Snow Index) images.
    
    Args:
        ndsi_image: Input NDSI image as a single-channel NumPy array (0-255)
        
    Returns:
        Segmented image with watershed contours
    """
    # Ensure the image is in uint8 format
    if ndsi_image.dtype != np.uint8:
        ndsi_image = np.clip(ndsi_image, 0, 255).astype(np.uint8)
    
    # Create a copy of the original NDSI for processing
    gray = ndsi_image.copy()
    
    # Create color image for visualization and watershed
    image_viz = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    
    # Apply contrast enhancement to highlight snow areas
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Apply bilateral filter - preserves edges while reducing noise
    filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)
    
    # For NDSI, higher values indicate snow/ice
    # Apply adaptive thresholding with negative offset to catch snow areas
    thresh_upper = cv2.adaptiveThreshold(
        filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, -3
    )
    
    # Also get Otsu threshold for more global approach
    otsu_value, thresh_otsu = cv2.threshold(
        filtered, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    
    # For NDSI, we can also set a direct threshold for snow (typically values > 0.4 in original scale)
    # In the 0-255 scale, this would be around 178
    _, thresh_direct = cv2.threshold(filtered, 170, 255, cv2.THRESH_BINARY)
    
    # Combine these approaches
    thresh_combined = cv2.bitwise_or(thresh_upper, thresh_otsu)
    thresh_combined = cv2.bitwise_or(thresh_combined, thresh_direct)
    
    # Apply morphological operations to clean up the binary image
    kernel = np.ones((3, 3), np.uint8)
    opened = cv2.morphologyEx(thresh_combined, cv2.MORPH_OPEN, kernel, iterations=1)
    thresh_cleaned = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    # Find sure background area
    kernel_bg = np.ones((5, 5), np.uint8)
    sure_bg = cv2.dilate(thresh_cleaned, kernel_bg, iterations=3)
    
    # Finding sure foreground area using distance transform
    dist_transform = cv2.distanceTransform(thresh_cleaned, cv2.DIST_L2, 5)
    
    # Normalize distance transform for better visualization and thresholding
    dist_norm = cv2.normalize(dist_transform, None, 0, 1.0, cv2.NORM_MINMAX)
    
    # Threshold to get the peaks (probable centers of snow patches)
    # Adaptive threshold based on maximum distance value
    dist_max = dist_norm.max()
    threshold_val = max(0.3, 0.6 * dist_max)  # At least 0.3, or 60% of the max
    _, sure_fg = cv2.threshold(dist_norm, threshold_val, 1.0, cv2.THRESH_BINARY)
    sure_fg = np.uint8(sure_fg * 255)
    
    # Finding unknown region
    unknown = cv2.subtract(sure_bg, sure_fg)
    
    # Marker labelling
    _, markers = cv2.connectedComponents(sure_fg)
    
    # Add one to all labels so that sure background is not 0, but 1
    markers = markers + 1
    
    # Mark the region of unknown with zero
    markers[unknown == 255] = 0
    
    # Apply watershed
    cv2.watershed(image_viz, markers)
    
    # Create result visualization
    # Mark watershed boundary lines in red
    image_viz[markers == -1] = [0, 0, 255]
    
    # Highlight snow regions based on NDSI value
    for label in np.unique(markers):
        if label > 1:  # Skip background (1) and boundary markers (-1)
            # Create mask for this segment
            mask = np.zeros_like(gray, dtype=np.uint8)
            mask[markers == label] = 255
            
            # Get mean NDSI value in this segment
            mean_val = cv2.mean(gray, mask=mask)[0]
            
            # Color likely snow areas (higher NDSI values) in blue
            if mean_val > 180:  # Likely snow
                # Add blue tint to probable snow regions
                image_viz[markers == label, 0] = np.minimum(255, image_viz[markers == label, 0] + 70)
            elif mean_val > 140:  # Possible snow
                # Add light blue tint
                image_viz[markers == label, 0] = np.minimum(255, image_viz[markers == label, 0] + 40)
    
    return image_viz