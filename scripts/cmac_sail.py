from cmac import cmac, get_sounding_times, get_sounding_file_name, config, quicklooks_ppi
import pyart
import glob
import pyart
import datetime
import numpy as np
import netCDF4
import xarray as xr
import os
import subprocess
import re
import pyart
import gc
import inspect
import sys
import time
import dask.bag as db
import matplotlib.pyplot as plt

from distributed import LocalCluster, Client, wait, progress
#from dask_jobqueue import SLURMCluster
from copy import deepcopy

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

def parse_sonde_date(filename):
    fname = filename.split("/")[-1]
    return datetime.datetime.strptime(fname, 'gucsondewnpnM1.b1.%Y%m%d.%H%M%S.cdf')

def parse_radar_date(filename):
    fname = filename.split("/")[-1]
    return datetime.datetime.strptime(fname, "xprecipradar_guc_volume_%Y%m%d-%H%M%S.b1.nc")

def run_cmac_and_plotting(radar_file_path, rad_time, cmac_config, sonde_times,
                          sounding_files, clutter_file_path, geotiff,
                          out_path, img_directory, sweep=3, dd_lobes=False):
    """ For dask we need the radar plotting routines all in one subroutine. """
    match_datetime = re.search(r'\d{4}\d{2}\d{2}.\d{6}', radar_file_path)
    match_month = re.search(r'\d{4}\d{2}', radar_file_path)
    file_datetime = match_datetime.group()
    file_datetime = file_datetime.replace('-', '.')
    file_month = match_month.group()
    save_name = cmac_config['save_name']
    file_name = (out_path + file_month + '/' + save_name + '.'
                 + file_datetime + '.nc')
    
    if not os.path.exists(out_path + file_month + '/'):
        os.makedirs(out_path + file_month + '/')
        
    if os.path.exists(file_name):
        print("Skipping " + file_name)
        import gc
        gc.collect()
        return
    
    try:
        radar = pyart.io.read(radar_file_path)
    except TypeError:
        print(radar_file_path + ' has encountered TypeError!')
        return
    print(radar.nsweeps)

    nyquist_vel = {'data': 15.9 * np.ones((radar.nrays,)), 
                   'units': 'm/s', 'long_name': 'Nyquist velocity', 'standard_name': 'nyquist_velocity'}
    radar.instrument_parameters = {'nyquist_velocity': nyquist_vel}

    
    # For SAIL, discard all range values below 300 m
    beam_block = pyart.io.read('flag_radar.nc')
    radar.fields['cbb_flag'] = deepcopy(beam_block.fields['cbb_flag'])
    radar.fields['cbb_flag']['data'] = radar.fields['cbb_flag']['data'][:radar.nrays, :]
    del beam_block

    valid_rays = int(np.argwhere(radar.range["data"] >= 300.)[0])
    print(valid_rays)
    for field in radar.fields.keys():
        radar.fields[field]["data"] = radar.fields[field]["data"][:, valid_rays:]
    radar.range["data"] = radar.range["data"][valid_rays:]
    radar.ngates = len(radar.range["data"])
    #radar_start_date = netCDF4.num2date(radar.time['data'][0],
     #                                   radar.time['units'], 
      #                                  only_use_cftime_datetimes=False, only_use_python_datetimes=True)

    #year_str = "%04d" % radar_start_date.year
    #month_str = "%02d" % radar_start_date.month
    #day_str = "%02d" % radar_start_date.day
    #hour_str = "%02d" % radar_start_date.hour
    #minute_str = "%02d" % radar_start_date.minute
    #second_str = "%02d" % radar_start_date.second
    #save_name = cmac_config['save_name']
    #file_name = (out_path + year_str + month_str + '/' + save_name + '.'
     #            + year_str + month_str + day_str + '.' + hour_str
      #           + minute_str + second_str + '.nc')
    #radtime = radar_time[
    #rad_time = datetime.datetime.strptime(radar.time["units"][0:33], "seconds since %Y-%m-%dT%H:%M:%S")
    # Load clutter files.
    #clutter = pyart.io.read(
     #   clutter_file_path+'clutter_corcsapr2cfrppiM1.a1'
      #  + '.' + year_str + month_str + day_str + '.' + hour_str
       # + minute_str + second_str + '.nc')
    #clutter_field_dict = clutter.fields['ground_clutter']
    #radar.add_field(
     #   'ground_clutter', clutter_field_dict, replace_existing=True)
    #del clutter
    sonde_index = np.argmin(np.abs(sonde_times - rad_time))
    sounding_file = sounding_files[sonde_index]
    # Retrieve closest sonde in time to the time of the radar file.
    sonde = xr.open_dataset(sounding_file)
    # Running the cmac code to produce a cmac_radar object.
    processed = False
    while not processed:
        try:
            cmac_radar = cmac(radar, sonde, 'sail_xband_ppi', geotiff=geotiff,
                         meta_append='config')
            processed = True
        except ValueError:
            sonde.close()
            sonde_index += 1
            sounding_file = sounding_files[sonde_index]
            sonde = xr.open_dataset(sounding_file)

    #    del radar
    #    sonde.close()
    #    import gc
    #    gc.collect()
    #    return
    # Free up some memory.
    del radar
    sonde.close()

    
    # Produce the cmac_radar file from the cmac_radar object.
    # Check metadata and fill values
    out_ds = xr.open_dataset('dod.nc', mask_and_scale=False)


    pyart.io.write_cfradial(file_name, cmac_radar)
    
    def set_or_create_attr(var, attr_name, attr_value):
        if attr_name in var.ncattrs():
            var.setncattr(attr_name, attr_value)
            return
        var.UnusedNameAttribute = attr_value
        var.renameAttribute("UnusedNameAttribute", attr_name)
        return

    # NetCDF4 time coverage
    out_cdf = netCDF4.Dataset(file_name, mode="a")
    for var in out_cdf.variables.keys():
        print("Resetting: " + var)
        for attr in out_ds[var].attrs:
                if not out_ds[var].attrs[attr] == "":
                    #setattr(out_cdf[var], attr, out_ds[var].attrs[attr])
                    if "_FillValue" in attr:
                        out_cdf[var][:] = np.nan_to_num(
                                out_cdf[var][:],
                                out_ds[var].attrs["_FillValue"])
                    else:
                        set_or_create_attr(out_cdf[var], attr, out_ds[var].attrs[attr])

    out_cdf["range"].long_name = "Range to measurement volume"
    out_cdf["time"].long_name = "Time in Seconds from Volume Start"
    out_cdf.close()                      
    print('## A CMAC radar object has been created at ' + file_name)

    if not os.path.exists(img_directory + file_month):
        os.makedirs(img_directory + file_month)
        subprocess.call('chmod -R g+rw ' + img_directory, shell=True)
    img_directory = img_directory + file_month
    # Producing all the cmac_radar quicklooks.
    quicklooks_ppi(cmac_radar, 'sail_xband_ppi',
        dd_lobes=False, image_directory=img_directory)

    # Delete the cmac_radar object and move on to the next radar file.
    del cmac_radar
    plt.close('all')
    return

def process_t(index):
    meta_config = config.get_metadata('sail_xband_ppi')
    cmac_config = config.get_cmac_values('sail_xband_ppi')
    field_config = config.get_field_names('sail_xband_ppi')
    radar_file = file_list[index]
    radar_time = radar_times[index]
    run_cmac_and_plotting(radar_file, radar_time, cmac_config, sonde_times, sonde_file_list, None, None, out_path, img_dir) 
    
if __name__ == "__main__":
    print("process start time: ", time.strftime("%H:%M:%S"))
    month = sys.argv[1]
    path = '/gpfs/wolf/atm124/proj-shared/gucxprecipradarS2.00/glue_files/%s_glued/*.nc' % month
    sonde_path = '/gpfs/wolf/atm124/proj-shared/gucsondewnpnM1.b1/*.cdf'
    out_path = '/gpfs/wolf/atm124/proj-shared/gucxprecipradarcmacS2.c1/ppi/'
    img_dir = '/gpfs/wolf/atm124/proj-shared/gucxprecipradarcmacS2.c1/png/'
    file_list = sorted(glob.glob(path))
    sonde_file_list = glob.glob(sonde_path)
    radar_times = np.array([parse_radar_date(x) for x in file_list])
    sonde_times = np.array([parse_sonde_date(x) for x in sonde_file_list])
    #cluster = SLURMCluster(project="atm124", memory="256GB", processes=24, cores=128, n_workers=48, walltime="6:00:00",
    #        job_extra=["--nodes=2"])
    #process_t(0)
    #cluster = LocalCluster(n_workers=20, processes=True, threads_per_worker=1)
   
    ##for i in range(len(radar_times)):
    ##        process_t(i)
    with Client(cluster) as c:
        results = c.map(process_t, range(len(radar_times)))
        wait(results)
    print("processing finished: ", time.strftime("%H:%M:%S"))
