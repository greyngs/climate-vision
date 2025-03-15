# Climate Change Analysis with Watershed

This web application lets users visualize and analyze changes in snow and ice coverage by utilizing the **watershed** segmentation algorithm on satellite images.

![Application screenshot](assets/app_images/Screenshot%202025-03-15%20123746.png)
![Watershed segmentation](assets/app_images/Screenshot%202025-03-15%20131158.png)

## 🌟 Features

- **Geographic exploration**: Choose locations interactively on a map
- **Temporal analysis**: Compare satellite images from two different dates
- **Automatic segmentation**: Employs the watershed algorithm to identify snow and ice areas
- **Change visualization**: Easily spot differences in snow coverage

## 🚀 Demo

You can check out the application here: [https://climate-vision-hphx3uabw6d3y558h4zu44.streamlit.app/](https://climate-vision-hphx3uabw6d3y558h4zu44.streamlit.app/)

## 💻 Technologies Used

- **Python**: The primary language for development
- **Streamlit**: The framework powering the user interface
- **OpenCV**: For image processing and the watershed algorithm
- **Google Earth Engine**: Provides access to historical satellite imagery
- **Folium**: For creating interactive map visualizations

## 🔮 Future Work

- Assessing the affected areas and calculating percentage changes
- Using the Normalized Difference Snow Index (NDSI) to enhance detection
- Incorporating historical Landsat images for a more extended analysis
- Comparing various segmentation algorithms

## 🔍 About Watershed

The watershed algorithm is a technique for image segmentation that relies on topography. It views the image as a topographic landscape where:
- Bright areas are like "mountains"
- Dark areas are akin to "valleys"

This algorithm mimics the flooding of the landscape starting from local low points, forming partitions when different flood basins converge.

When it comes to detecting snow and ice, the watershed method shines due to its knack for pinpointing clear edges between regions with varying brightness levels.