# Still a work in progress, infant stage.
"""" Code that uses CMAC to remove and correct second trip returns. """


# from boto.s3.connection import S3Connection
from datetime import datetime
import operator
import netCDF4
import pyart

from . import processing_code


def cmac(radar_file, sounde_file, alt=320.0, write_radar=False,
         filename_radar=None, write_grid=True, filename_grid=None,
         **kwargs):
    """
    Corrected Moments in Antenna Coordinates

    Parameters
    ----------
    radar_file : str
        Filename and location of radar file to do CMAC calculations on.
        Radar  object is also used to add new CMAC fields to, such as
        gate_id.
    sound_file : str
        Filename and location of sounde file to use for CMAC calculation.

    Other Parameters
    ----------------
    alt : float
        Value to use as default altitude for the radar object.
    write_radar : bool
        Whether or not to write the radar object with added CMAC fields
        to netCDF. Default is False.
    write_grid : bool
        Whether or not to write the grid object with added CMAC fields
        and CMAC corrections to netCDF. Default is True.
    filename_radar : str
        Filename to create for radar.
    filename_grid : str
        Filename to create for grid.

    Returns
    -------
    radar : Radar
        Radar object with new CMAC added fields.
    grid : Grid
        Grid object with new CMAC added fields.

    """

    # radar, sndfile, altitude,
    radar = pyart.io.read(radar_file)
    radar.altitude['data'][0] = alt

    radar_start_date = netCDF4.num2date(
        radar.time['data'][0], radar.time['units'])
    print(radar_start_date)
    ymd_string = datetime.strftime(radar_start_date, '%Y%m%d')
    hms_string = datetime.strftime(radar_start_date, '%H%M%S')
    print(ymd_string, hms_string)

    sonde = netCDF4.Dataset(sounde_file)
    print(sonde.variables.keys())

    z_dict, temp_dict = pyart.retrieve.map_profile_to_gates(
        sonde.variables['tdry'][:], sonde.variables['alt'][:], radar)
    texture = processing_code.get_texture(radar)

    snr = pyart.retrieve.calculate_snr_from_reflectivity(radar)

    radar.add_field('sounding_temperature', temp_dict, replace_existing=True)
    radar.add_field('height', z_dict, replace_existing=True)
    radar.add_field('SNR', snr, replace_existing=True)
    radar.add_field('velocity_texture', texture, replace_existing=True)
    print(radar.fields.keys())

    my_fuzz, cats = processing_code.do_my_fuzz(radar)
    print(my_fuzz['notes'])
    radar.add_field('gate_id', my_fuzz,
                    replace_existing=True)

    print(radar.fields['gate_id']['notes'])
    cat_dict = {}
    for pair_str in radar.fields['gate_id']['notes'].split(','):
        print(pair_str)
        cat_dict.update(
            {pair_str.split(':')[1]:int(pair_str.split(':')[0])})

    sorted_cats = sorted(cat_dict.items(), key=operator.itemgetter(1))

    happy_gates = pyart.correct.GateFilter(radar)
    happy_gates.exclude_all()
    happy_gates.include_equal('gate_id', cat_dict['rain'])
    happy_gates.include_equal('gate_id', cat_dict['melting'])
    happy_gates.include_equal('gate_id', cat_dict['snow'])

    grid = pyart.map.grid_from_radars(
        (radar, ), grid_shape=(46, 251, 251),
        grid_limits=((0, 15000.0), (-50000, 50000), (-50000, 50000)),
        fields=list(radar.fields.keys()), gridding_algo="map_gates_to_grid",
        weighting_function='BARNES', gatefilters=(happy_gates, ),
        min_radius=200.0, **kwargs)

    if write_radar:
        pyart.io.write_cfradial(filename_radar, radar)

    if write_grid:
        pyart.io.write_grid(filename_grid, grid)
