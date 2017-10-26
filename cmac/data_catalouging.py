""" Determines the closest sounding file by datetime to a radar file. """

import datetime
import glob
import pyart
import os
import netCDF4

from . import cmac, quicklooks

def run_cmac_and_plotting(radar_file_path, sounding_times, args):
    import pyart
    from cmac import cmac, quicklooks
    import os
    from netCDF4 import num2date, Dataset
    import netCDF4
    import stat

    """ For IPCluster need the radar plotting routines all in one subroutine. """
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
    radar_start_date = num2date(radar.time['data'][0],
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
    sonde = Dataset(sonde_file)
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
               min_lon=args.min_longitude, dd_lobes=args.dd_lobes)
    print('## Quicklooks have been saved at ' + img_directory)
    print('##')
    del cmac_radar


def get_sounding_times(sonde_path):
    """ This function parses the time periods from a list of SGP
    sonde files. """
    file_list = glob.glob(sonde_path + '/*.cdf')
    time_list = []
    for file_name in file_list:
        time_list.append(
            datetime.datetime.strptime(
                file_name, (sonde_path + 'sgpsondewnpnC1.b1.'
                            + '%Y%m%d.%H%M%S.cdf')))
    return time_list


def get_sounding_file_name(sonde_path, time):
    """ This function will give a filename of a sounding corresponding
    to given time. """
    year_str = "%04d" % time.year
    month_str = "%02d" % time.month
    day_str = "%02d" % time.day
    hour_str = "%02d" % time.hour
    minute_str = "%02d" % time.minute
    second_str = "%02d" % time.second

    file_name = (sonde_path + 'sgpsondewnpnC1.b1.' + year_str + month_str +
                 day_str + '.' + hour_str + minute_str + second_str + '.cdf')
    print(file_name)
    return file_name
