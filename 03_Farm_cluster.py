"""
Example script to run WRF for a farm at the datapoint closest to a cluster centre.
Note for this example we use the clusters on the Denmark domain found when clustering on wind velocity
in the Denmark domain.
"""

# import necessary packages
import os
import subprocess
from netCDF4 import Dataset
import numpy as np
from distutils.dir_util import copy_tree
import multiprocessing as mp
import pandas as pd
from wind_turbine_fixed_square import wind_turbine_fn
import random
import argparse

def parallel_run(processes, turbine_list, wind_turbine):

    # set up parallelisations
    in_queue = mp.Queue()
    out_queue = mp.Queue()
    future_res = []

    for i in range(processes):
        future_res.append(mp.Process(target = wrf_run, args = (in_queue, out_queue)))
        future_res[-1].start()
        in_queue.put((turbine_list[i], wind_turbine, i))

    for i in range(processes):
        in_queue.put('stop')

def wrf_run(qin, qout):

    for (turbine_df, wind_turbine, iteration) in iter(qin.get, 'stop'):
        if wind_turbine:
            far = "w_"
        else:
            far = "no_"

        t = random.random()

        # set up folder where WRF will run
        path_name = "/rds/general/project/wrfwindpower/ephemeral/m_" + far + str(t)[2:6] + '_' + str(iteration)

        print(path_name)

        os.mkdir(path_name)
        os.chdir(path_name)

        os.mkdir('WRF')

        # copy WPS and WRF files
        copy_tree("/rds/general/user/mc4117/home/wrf_nano_data/wrf/WRF", path_name + '/WRF', preserve_symlinks=1)
        copy_tree("/rds/general/user/mc4117/home/wrf_nano_data/wrf/WPS", path_name + '/WPS', preserve_symlinks=1)

        os.chdir(path_name + '/WPS')

        # modify initialisation script to run for our problem
        file_wps = open('namelist.wps.orig').read()
        lines_wps = file_wps.split('\n')
        lines_wps[3] = lines_wps[3].replace('01-01-01_00', '07-12-02_12')
        lines_wps[4] = lines_wps[4].replace('01-01-02_00', '07-12-02_18')
        f_wps = open('namelist.wps', 'w+')
        for i in lines_wps:
            f_wps.write(i)
            f_wps.write('\n')
        f_wps.close()

        os.chdir(path_name + '/WPS')
        # run WPS so as to get the files needed to set up the WRF problem
        test = os.getcwd()
        subprocess.check_call("singularity exec -H " + str(test) + " --bind /rds/general/project/wrfwindpower/ephemeral,/rds/general/project/wrfwindpower/live,$TMPDIR:$TMPDIR /rds/general/project/wrfwindpower/live/wrf_ephemeral ./metgrid.exe", shell = True)

        os.chdir(path_name + "/WRF/test/em_real")

        # modify WRF file for our specific problem
        file = open('namelist.input.orig').read()
        lines = file.split('\n')
        lines[1] = lines[1].replace('2001', '2007')
        lines[2] = lines[2].replace('01', '12')
        lines[3] = lines[3].replace('01', '02')
        lines[4] = lines[4].replace('06', '12')
        lines[7] = lines[7].replace('2001', '2007')
        lines[8] = lines[8].replace('01', '12')
        lines[9] = lines[9].replace('02', '02')
        lines[10] = lines[10].replace('00', '18')
        if not wind_turbine:
            lines[101] = lines[101].replace('0, 1', '0, 0')
        f = open('namelist.input', 'w+')
        for i in lines:
            f.write(i)
            f.write('\n')
        f.close()

        subprocess.check_call("ln -sf ../../../WPS/met_em.d* .", shell = True)

        # get wind turbine placement
        if wind_turbine:
            turbine_df.to_csv(path_name + '/WRF/test/em_real/windturbines.txt', sep = ' ', header = False, index = False)

        # run WRF
        subprocess.check_call("singularity run --bind /rds/general/ephemeral/project/wrfwindpower/ephemeral:/rds/general/ephemeral/project/wrfwindpower/ephemeral /rds/general/project/wrfwindpower/live//wrf_ephemeral ./real.exe > /dev/null", shell = True)

        file = open('namelist.input').read()
        lines = file.split('\n')
        lines[10] = lines[10].replace('18', '15')
        f = open('namelist.input', 'w+')
        for i in lines:
            f.write(i)
            f.write('\n')
        f.close()

        subprocess.check_call("singularity run --bind /rds/general/ephemeral/project/wrfwindpower/ephemeral:/rds/general/ephemeral/project/wrfwindpower/ephemeral /rds/general/project/wrfwindpower/live/wrf_ephemeral ./wrf.exe > out.txt", shell = True)

        result = Dataset('wrfout_d02')

        # extract necessary outputs from WRF runs
        TKE = result['TKE_PBL'][:].data

        U = result['U'][:].data

        V = result['V'][:].data

        pressure = result['PSFC'][:].data

        if wind_turbine:
            fldr = 'wind_farm/'
        else:
            fldr = 'no_farm/'
        path_new = '/rds/general/project/wrfwindpower/live/wrf_results_mv_new/fixed_sq_farm'
        os.mkdir(path_new)
        np.save(path_new + '/tke.npy', TKE)
        np.save(path_new + '/u.npy', U)
        np.save(path_new + '/v.npy', V)
        np.save(path_new + '/press.npy', pressure)

        if wind_turbine:
            POWER = result['POWER'][:].data

            turbine_df.to_csv(path_new + '/windturbines.txt', sep = ' ', header = False, index = False)
            np.save(path_new + '/power.npy', POWER)

def main(processes, wind_turbine):
    turbine_list = wind_turbine_fn(processes)

    parallel_run(processes, turbine_list, wind_turbine)


CLI = argparse.ArgumentParser()

CLI.add_argument("--process", type = int, default = None)
CLI.add_argument("--turbine", type = str, default = None)

args = CLI.parse_args()

process = args.process
wind_turbine_str = args.turbine

if wind_turbine_str == "True":
    wind_turbine = True
elif wind_turbine_str == "False":
    wind_turbine = False
else:
    stop
print(wind_turbine)

main(process, wind_turbine)
