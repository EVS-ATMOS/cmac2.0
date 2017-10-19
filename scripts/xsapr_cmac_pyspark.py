#!/usr/bin/env python
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
import time
import stat

from cmac import cmac, quicklooks, get_sounding_times, get_sounding_file_name
from cmac import xsapr_clutter
from pyspark.sql import SparkSession


""" For dask we need the radar plotting routines all in one subroutine """ 
def run_cmac_and_plotting(radar_file_path, sounding_times, args):
    """ For dask we need the radar plotting routines all in one subroutine. """
    try:
        radar = pyart.io.read(radar_file_path)
    except TypeError:
        if args.bad_directory is None:
            path = (os.path.expanduser('~') + '/' + 'type_error_radars/')
        else:
            path = args.bad_directory
        print(radar_file_path + ' has encountered TypeError!')
        if not os.path.exists(path):
            os.makedirs(path)
            os.chmod(
                path,
                stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP)
        shutil.move(radar_file_path, path)
        return
    radar_start_date = netCDF4.num2date(radar.time['data'][0],
                                        radar.time['units'])

    # Load clutter files.
    clutter_file_path = args.clutter_file
    print('## Loading clutter file ' + clutter_file_path)
    clutter = pyart.io.read(clutter_file_path)
    print('## Reading dictionary...')
    clutter_field_dict = clutter.fields['xsapr_clutter']
    print('## Adding clutter field..')
    radar.add_field(
        'xsapr_clutter', clutter_field_dict, replace_existing=True)
    del clutter
    closest_time = min(sounding_times,
                       key=lambda d: abs(d - radar_start_date))
    sonde_file = get_sounding_file_name(args.sonde_path,
                                        closest_time)
    sonde = netCDF4.Dataset(sonde_file)
    cmac_radar = cmac(radar, sonde, alt=args.altitude)

    ## Free up some memory
    del radar
    sonde.close()
    year_str = "%04d" % radar_start_date.year
    month_str = "%02d" % radar_start_date.month
    day_str = "%02d" % radar_start_date.day
    hour_str = "%02d" % radar_start_date.hour
    minute_str = "%02d" % radar_start_date.minute
    second_str = "%02d" % radar_start_date.second

    if args.out_radar is None:
        the_path = (os.path.expanduser('~') + '/'+ year_str + month_str
                    + second_str + '/')
    else:
        the_path = (args.out_radar + '/' + year_str +  month_str
                    + day_str + '/')
    file_name = (the_path + '/sgpxsaprcmacsurI5.c1.' + year_str + month_str
                 + day_str + '.' + hour_str + minute_str + second_str + '.nc')

    if not os.path.exists(the_path):
        os.makedirs(the_path)
        os.chmod(
            the_path,
            stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
            stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP)

    pyart.io.write_cfradial(file_name, cmac_radar)
    print('## A CMAC radar object has been created at ' + file_name)
    img_directory = (args.image_directory + '/' + year_str + month_str
                     + day_str + '.' + hour_str + minute_str + second_str)
    if not os.path.exists(img_directory):
        os.makedirs(img_directory)
        os.chmod(
            img_directory,
            stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
            stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP)

    quicklooks(cmac_radar, image_directory=img_directory,
               sweep=args.sweep, max_lat=args.max_latitude,
               min_lat=args.min_latitude, max_lon=args.max_longitude,
               min_lon=args.min_longitude)
    print('## Quicklooks have been saved at ' + img_directory)
    print('##')
    del cmac_radar


def main():
    """ The main function utilizes the cmac function and quicklooks function
    to produce a CMAC radar and images pertaining to CMAC. """
    bt = time.time()
    parser = argparse.ArgumentParser(
        description='Create a radar object with applied CMAC2.0.')
    parser.add_argument(
        'radar_path', type=str, help=('Radar path to use for calculations.',
                                      'The program will search recursively',
                                      'for files in the directory. If',
                                      'a file is specified, every file',
                                      'in the list will be processed.'))
    parser.add_argument(
        'sonde_path', type=str,
        help='Sonde path to use for CMAC calculation.')
    parser.add_argument(
        'clutter_file', type=str,
        help='Path to clutter file')
    parser.add_argument(
        '-o', '--out_radar', type=str, default=None,
        help=('Out file path and name to use for the CMAC radar.',
              'If not provided, radar is written to users home',
              'directory.'))
    parser.add_argument(
        '-id', '--image_directory', type=str, default=None,
        help=('Path to image directory to save CMAC radar images.',
              'If not provided, images are written to users home',
              'directory.'))
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
        '-sched', '--scheduler_file', type=str, default='~/scheduler.json',
        help='Path to dask scheduler json file')
    parser.add_argument(
        '-bd', '--bad_directory', type=str, default=None,
        help=('Path to directory to place radar input files that'
              + ' can not be read by Py-ART due to TypeError'))

    
    args = parser.parse_args()

    radar_files = glob.glob(args.radar_path + '/**/*', recursive=True)
    sounding_times = get_sounding_times(args.sonde_path)
    
    # Connect to dask client
    spark = SparkSession\
            .builder\
            .appName("Cmac2.0")\
            .config("spark.executor.memory", "3g")\
            .getOrCreate()
    count = spark.sparkContext.parallelize(radar_files, numSlices=1000).map(
            lambda radar_files: run_cmac_and_plotting(radar_files,
                                                      sounding_times,
                                                      args)).collect()
    spark.stop()
    ## Do radar object loading on compute nodes. 
    if args.image_directory is None:
        print('## Quicklooks have been saved in your home directory.')
    else:
        print('## Quicklooks have been save to ' + args.image_directory)
    print('##')
    print('## CMAC 2.0 Completed')
    

if __name__ == '__main__':
    main()
