# Still a work in progress, infant stage.
"""" Code that uses CMAC to remove and correct second trip returns. """

# from boto.s3.connection import S3Connection
from datetime import datetime
import netCDF4
import pyart

from . import processing_code


def cmac(radar, sonde, alt=320.0, **kwargs):
    """
    Corrected Moments in Antenna Coordinates

    Parameters
    ----------
    radar : Radar
        Radar object to use in the CMAC calculation.
    sonde : Object
        Object containing all the sonde data.

    Other Parameters
    ----------------
    alt : float
        Value to use as default altitude for the radar object.

    Returns
    -------
    radar : Radar
        Radar object with new CMAC added fields.

    """


    radar.altitude['data'][0] = alt

    radar_start_date = netCDF4.num2date(
        radar.time['data'][0], radar.time['units'])
    print(radar_start_date)
    ymd_string = datetime.strftime(radar_start_date, '%Y%m%d')
    hms_string = datetime.strftime(radar_start_date, '%H%M%S')
    print(ymd_string, hms_string)

    z_dict, temp_dict = pyart.retrieve.map_profile_to_gates(
        sonde.variables['tdry'][:], sonde.variables['alt'][:], radar)
    texture = processing_code.get_texture(radar)

    snr = pyart.retrieve.calculate_snr_from_reflectivity(radar)
    print('##')
    print('## Radar fields are being added:')
    radar.add_field('sounding_temperature', temp_dict, replace_existing=True)
    print('##    sounding_temperature')
    radar.add_field('height', z_dict, replace_existing=True)
    print('##    height')
    radar.add_field('SNR', snr, replace_existing=True)
    print('##    SNR')
    radar.add_field('velocity_texture', texture, replace_existing=True)
    print('##    velocity_texture')

    my_fuzz, cats = processing_code.do_my_fuzz(radar, **kwargs)
    print(my_fuzz['notes'])
    radar.add_field('gate_id', my_fuzz,
                    replace_existing=True)
    print('##    gate_id')
    print('##')
    print('## All CMAC fields have been added to the radar object.')
    return radar
