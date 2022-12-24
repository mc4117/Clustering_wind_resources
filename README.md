# Clustering_wind_resources
This repository contains the code to accompany the following paper:

Mariana C. A. Clare, Simon C. Warder, Robert Neal, B. Bhaskaran, Matthew D. Piggott **An unsupervised learning approach for predicting wind farm power and downstream wakes using weather patterns**

The paper combines the weather patterns found using k-means clustering of ERA5 data with the accurate numerical model [WRF](https://www.mmm.ucar.edu/models/wrf) to determine both accurate long-term wind farm power estimates and long-term predictions of power loss due to wakes from upstream farms.

The first file `01_Optimum_num_clusters.ipynb` shows an example of how to determine the optimum number of clusters to use for k-means clustering. The example shown is for clustering on ERA5 wind velocity data on the small Denmark domain.

The second file `02_Six_clusters.ipynb` shows how to obtain the actual clusters once the optimum number has been estimated. Again the example shown is for clustering on ERA5 wind velocity data on the small Denmark domain.

The third file `03_Farm_cluster.py` gives an example of how to run the numerical model WRF with the weather patterns found by clustering, in order to obtain predictions of power output and downstream wake from a wind farm.

The fourth file `04_Power_prediction.ipynb` gives an example of how to post-process the outputs of only six WRF simulations to obtain an accurate long-term prediction of wind farm power output.

The fifth file `05_Downstream_wake_prediction.ipynb` gives an example of how to post-process the outputs of only six WRF simulations to obtain an accurate long-term prediction of downstream wake from a wind farm.

The other files in this repository are supplementary files used to run the scripts detailed above.
