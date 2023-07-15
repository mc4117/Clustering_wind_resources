"""
Script to generate text file for placement of wind farm used to run WRF simulation
"""

import numpy as np
import pandas as pd

def wind_turbine_fn(processes):

    # file used as reference for farm layout
    f = open('/rds/general/user/mc4117/home/wrf_simulations/windturbines_old.txt').read().split('\n')
    lat_turbines = []
    
    for line in f[:-1]:
        split_line = line.split(' ')
        lat_turbines.append(float(split_line[0]))
    
    lat_unique = np.array(pd.DataFrame(lat_turbines).drop_duplicates().sort_values([0]))
    
    # set the distance between the wind turbines to be 7 rotor diameters 
    lat_diff = lat_unique[1] - lat_unique[0]
    
    
    lat_max = 56.631912
    lat_min = 54.07763
    
    lon_max = 7.7304993
    lon_min = 5.5336914
    
    turbine_df_list = []
    
    for i in range(processes):
    
        # set origin points of wind farm
        origin_point_lat = 55.354771
        origin_point_lon = 6.63209535
        
        # shift the wind farm to the right location using the old farm layout from the txt file
        new_lat_turb = [float(i*lat_diff/2 + origin_point_lat) for i in range(10)]
    
        new_lon_turb = [float(i*lat_diff/2 + origin_point_lon) for i in range(10)]
    
        # check that the farm does not exceed the domain
        if max(new_lon_turb) > lon_max - (85*10*lon_diff*0.1):
            print(i)
            stop
        if max(new_lat_turb) > lat_max - (14*10*lat_diff*0.1):
            print(i)
            stop
        if min(new_lat_turb) < lat_min + (14*10*lat_diff*0.1):
            print(i)
            stop
        if min(new_lon_turb) < lon_min + (85*10*lon_diff*0.1):
            print(i)
            stop
    
    
        lon_mesh, lat_mesh = np.meshgrid(new_lon_turb, new_lat_turb)
        
        lon_flatten = lon_mesh.flatten()
        lat_flatten = lat_mesh.flatten()    
        

        turbine_list = [6 for _ in range(len(lon_flatten))]
    
        # set structure for wind turbine text file
        turbine_df = pd.concat([pd.DataFrame(lat_flatten, columns = ['lat']), pd.DataFrame(lon_flatten, columns = ['lon']), pd.DataFrame(turbine_list, columns = ['type'])], axis  = 1)
    
        turbine_df_list.append(turbine_df)

    return turbine_df_list

