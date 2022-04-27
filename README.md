# Deforestation

This repository contains code developed towards detecting deforestation from satellite images using deep learning. At first, the work focuses on the Amazon rainforest and particularly its Brazilian part as it contains most data. Later, the work will focus on transfering the methods to other geographical regions that contain tropical rainforest, incl. Indonesia and the Congo Basin.


## Data 
Input data is at this point Sentinel-2 images. At a later stage, data from Sentinel-1 and other sensors will be also used.

To create labels, existing public data on forest cover, forest loss and deforestation alerts will be used.


### Input data processing

Sentinel-2 time series have been acquired from Google Earth Engine. Data from after 2018 contain a classification layer that assigns a class to each pixel at 20m resolution. This layer was used to mask out all pixels classified as clouds or cloud shadows.


### Reference data processing

Brief description of each dataset:

DETER
- based on data from multiple sensors, 
- updated with every new acquisition, but published monthly?
- manually verified, 
- polygons
- managed by INPE, 
- quite noisy, polygons oversimplifed; both FP and FN

PRODES
- yearly
- manually verified
- raster (30m); maybe also available as vector
- managed by INPE
- high quality
- ignores deforestations under 6.25ha

MapBiomas
- updated approx. monthly
- polygons
- overcomplicated polygons
- varying quality, but sometimes can be extremely precise
- some manual work also included
- sometimes very inprecise date

GLAD
- managed by UMD
- based on Landsat
- points
- GLAD-S2?

RADD
- managed by WUR
- based on Sentinel-1
- points
- catches more of the border between F/NF

### Generating training data

At first, one training example will consist of a pair of images taken at times T_1 and T_2, each of size B*W*H, where B is number of bands and W,H are width and height, respectively. At the moment, B=4 and the used bands are R,G,B and NIR (all bands with 10m resolution and also commonly used bands for vegetation mapping). Height and width are to be determined.

What remains to be determined is whether no-data values are allowed in the training images and if so, how they are handled.


Label to such training example will be a binary segmentation mask. This mask of size 1*W*H has values of 1 in areas where deforestation happened between T_1 and T_2. The rest of the segmentation mask values are set to 0.

The label segmentation mask will be generated from available data on deforestation. The available data sources that are considered include DETER, PRODES, MapBiomas, GLAD, RADD. 
 

