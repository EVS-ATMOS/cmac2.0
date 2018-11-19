""" Determines the closest sounding file by datetime to a radar file. """

import datetime
import glob


def get_sounding_times(sonde_path, sonde_name):
    """ This function parses the time periods from a list of SGP
    sonde files. """
    file_list = glob.glob(sonde_path + '/*.cdf')
    time_list = []
    for file_name in file_list:
        time_list.append(
            datetime.datetime.strptime(
                file_name, (sonde_path + sonde_name
                            + '.%Y%m%d.%H%M%S.cdf')))
    return time_list


def get_sounding_file_name(sonde_path, sonde_name, time):
    """ This function will give a filename of a sounding corresponding
    to given time. """
    year_str = "%04d" % time.year
    month_str = "%02d" % time.month
    day_str = "%02d" % time.day
    hour_str = "%02d" % time.hour
    minute_str = "%02d" % time.minute
    second_str = "%02d" % time.second

    file_name = (sonde_path + sonde_name + '.' + year_str + month_str +
                 day_str + '.' + hour_str + minute_str + second_str + '.cdf')
    print(file_name)
    return file_name
