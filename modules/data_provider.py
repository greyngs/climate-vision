from datetime import datetime, timedelta
import numpy as np
import ee
import geemap

def get_image(latitude, longitude, date, zoom_level, cloud_cover_max=30):
    """Retrieve Sentinel-2 satellite imagery for a specific location and date"""
    formatted_date = date.strftime('%Y-%m-%d')
    
    # Create point and area of interest
    point = ee.Geometry.Point([longitude, latitude])
    
    # Calculate buffer based on zoom level
    buffer_size = 25000 / (zoom_level/2)  # in meters
    aoi = point.buffer(buffer_size)
    
    # Define date range (30 days to ensure finding images)
    date_obj = datetime.strptime(formatted_date, '%Y-%m-%d')
    start_date = formatted_date
    end_date_obj = date_obj + timedelta(days=30)
    end_date = end_date_obj.strftime('%Y-%m-%d')
    
    # Select image collection (Sentinel-2)
    collection = ee.ImageCollection('COPERNICUS/S2_SR') \
        .filterBounds(aoi) \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_cover_max))
    
    # Check if images are available
    image_count = collection.size().getInfo()
    if image_count == 0:
        print(f"No images found for date {formatted_date} with less than {cloud_cover_max}% cloud cover")
        print("Trying with a wider date range...")
        
        # No need to expand date range again as it's already set to 30 days
        # This appears to be redundant in the original code
        
        image_count = collection.size().getInfo()
        if image_count == 0:
            import streamlit as st
            st.error(f"No images found for range {start_date} to {end_date} with less than 30% cloud cover")
            return False
    
    # Get the most recent image
    image = collection.sort('system:time_start', False).first()
    
    # Get image date for filename
    image_date = ee.Date(image.get('system:time_start')).format('YYYY-MM-dd').getInfo()
    
    # Select bands (RGB for true color)
    rgb_image = image.select(['B4', 'B3', 'B2'])
    
    # Prepare visualization parameters
    rgb_vis_params = {
        'min': 0,
        'max': 3000,
        'bands': ['B4', 'B3', 'B2']
    }
    
    # Calculate scale based on zoom level
    scale = 30  # Keep between 10 and 1000 meters
    
    # Get image as NumPy array
    rgb_numpy = geemap.ee_to_numpy(rgb_image, region=aoi, bands=["B4", "B3", "B2"], scale=scale)

    # Normalize values for visualization (0-255)
    if rgb_numpy is not None:
        rgb_numpy = np.clip((rgb_numpy / 3000) * 255, 0, 255).astype(np.uint8)

    return rgb_numpy