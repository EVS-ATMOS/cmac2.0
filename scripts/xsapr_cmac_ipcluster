#!/usr/bin/env ipython
""" Creates a radar object with applied CMAC 2.0 and quicklooks pertaining
to CMAC 2.0. """

import os

from matplotlib import use
use('agg')
import argparse
import netCDF4
import pyart
import glob
import datetime
import platform
import numpy as np
import subprocess
import stat

from ipyparallel import Client
from cmac import get_sounding_file_name, get_sounding_times, run_cmac_and_plotting
from time import sleep, time


""" For dask we need the radar plotting routines all in one subroutine """ 

if __name__ == '__main__':
    """ For dask we need the radar plotting routines all in one subroutine """
    """ The main function utilizes the cmac function and quicklooks function
    to produce a CMAC radar and images pertaining to CMAC. """
    parser = argparse.ArgumentParser(
        description='Create a radar object with applied CMAC2.0.')
    parser.add_argument(
        'radar_path', type=str, help=('Radar path to use for calculations.' +
                                      'The program will search recursively' + 
                                      'for files in the directory.'))
    parser.add_argument(
        'sonde_path', type=str,
        help='Sonde path to use for CMAC calculation.')
    parser.add_argument(
        'clutter_file', type=str,
        help='Path to clutter file')
    parser.add_argument(
        '-o', '--out_radar', type=str, default=None,
        help=('Out file path and name to use for the CMAC radar.'
              + ' If not provided, radar is written to users home'
              + ' directory.'))
    parser.add_argument(
        '-id', '--image_directory', type=str, default=None,
        help=('Path to image directory to save CMAC radar images.'
              + ' If not provided, images are written to users home'
              + ' directory.'))
    parser.add_argument(
        '-alt', '--altitude', type=float, default=320.0,
        help='Value to use as default altitude for the radar object')
    parser.add_argument(
        '-sw', '--sweep', type=int, default=3,
        help='Value for the sweep to plot.')
    parser.add_argument(
        '-maxlat', '--max_latitude', type=float, default=37.0,
        help='Value to use as max latitude for the bounds of the plots.')
    parser.add_argument(
        '-minlat', '--min_latitude', type=float, default=36.0,
        help='Value to use as min latitude for the bounds of the plots.')
    parser.add_argument(
        '-maxlon', '--max_longitude', type=float, default=-97.0,
        help='Value to use as max longitude for the bounds of the plots.')
    parser.add_argument(
        '-minlon', '--min_longitude', type=float, default=-98.3,
        help='Value to use as min longitude for the bounds of the plots.')
    parser.add_argument(
        '-bd', '--bad_directory', type=str, default=None,
        help=('Path to directory to place radar input files that'
              + ' can not be read by Py-ART due to TypeError'))
    parser.add_argument('--dd-lobes', dest='dd_lobes', action='store_true',
                        help='Plot Dual Doppler lobes between i4 and i5.')
    parser.add_argument('--no-dd-lobes', dest='dd_lobes', action='store_false',
                        help=('Do not plot Dual Doppler lobes' +
                             ' between i4 and i5.'))

    parser.set_defaults(dd_lobes=False)
    args = parser.parse_args()
    if os.path.isdir(args.radar_path):
        radar_files = glob.glob(args.radar_path + '/**/*XSW*', recursive=True)
    elif os.path.isfile(args.radar_path):
        with open(args.radar_path) as f:
            radar_files = f.readlines()
        radar_files = [x.strip() for x in radar_files]
    else:
        raise IOError('The specified radar path does not exist!')

    sounding_times = get_sounding_times(args.sonde_path)

    # Connect to IPCluster
    state = 0
    while state == 0:
        try:
            My_Cluster = Client(profile='mpi')
            My_View = My_Cluster[:]
            state = 1
        except:
            state = 0
            print('Cluster not ready!')
            sleep(10)

    My_View.block = False

    result_list = []
    print('## Python version: ' + str(platform.python_version()))
    print('## Opened IPython cluster')
    by = time()
       
    My_View.execute('import matplotlib')
    My_View.execute('matplotlib.use("agg")')
    My_View.execute('import pyart')
    My_View.execute('import numpy as np')
    My_View.execute('from cmac import run_cmac_and_plotting')
    My_View.execute('import netCDF4')
    My_View.push({'sounding_times':sounding_times, 'args':args, 
                  })
    the_function = lambda the_file: run_cmac_and_plotting(
        the_file, sounding_times, args) 
    for i in range(0,len(radar_files), 300):
        the_files = radar_files[i:i+(np.min([len(radar_files), i+299]))]
        result=My_View.map_async(the_function, the_files)
        result.get()
        My_View.wait()


    ## Do radar object loading on compute nodes. 
    if args.image_directory is None:
        print('## Quicklooks have been saved in your home directory.')
    else:
        print('## Quicklooks have been saved to ' + args.image_directory)
    print('##')
    print('## CMAC 2.0 Completed')
    perm_image = 'chmod -R g+rw ' + args.image_directory
    perm_radar = 'chmod -R g+rw ' + args.out_radar
    subprocess.call(perm_image, shell=True)
    subprocess.call(perm_radar, shell=True)
    print('##')
    print('## CMAC 2.0 Completed in ' + str(time() - bt) + ' s')
    client.shutdown()

