""" Code that plots fields from the CMAC radar object. """

import os
from datetime import datetime
import operator

import cartopy.crs as ccrs
import netCDF4
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pyart

from pyart.graph.common import generate_radar_name
from pyart.graph.common import generate_radar_time_begin

plt.switch_backend('agg')


def quicklooks(radar, image_directory=None, sweep=3,
               max_lat=37.0, min_lat=36.0, max_lon=-97.0, min_lon=-98.3,
               dd_lobes=True):
    """
    Quicklooks, images produced with regards to CMAC

    Parameter
    ---------
    radar : Radar
        Radar object that has CMAC applied to it.

    Optional Parameters
    -------------------
    image_directory : str
        File path to the image folder of which to save the CMAC images. If no
        image file path is given, image path defaults to users home directory.
    sweep : int
        Sweep number to have plotted. Default is 3.
    max_lat : float
        Maximum latitude for plot bounds. Default is 37.0.
    min_lat : float
        Minimum latitude for plot bounds. Default is 36.0.
    max_lon : float
        Maximum longitude for plot bounds. Default is -97.0.
    min_lon : float
        Minimum longitude for plot bounds. Default is -98.3.
    dd_lobes : bool
        Plot DD lobes between i4 and i5 if = True.

    """

    if image_directory is None:
        image_directory = os.path.expanduser('~')

    radar_start_date = netCDF4.num2date(
        radar.time['data'][0], radar.time['units'])

    date_string = datetime.strftime(radar_start_date, '%Y%m%d.%H%M%S')
    arm_name = '.sgpxsaprcmacsurI5.c1.'
    combined_name = arm_name + date_string

    # Creating a plot of reflectivity before CMAC.
    lal = np.arange(min_lat, max_lat+.2, .2)
    lol = np.arange(min_lon, max_lon+.2, .2)
    grid_lat = np.arange(min_lat, max_lat, 0.01)
    grid_lon = np.arange(min_lon, max_lon, 0.01)
    i5 = [_dms_to_decimal(-97, 35, 37.68), _dms_to_decimal(36, 29, 29.4)]
    i4 = [_dms_to_decimal(-97, 21, 49.32), _dms_to_decimal(36, 34, 44.4)]
    bca = _get_bca(i4[0], i4[1], i5[0], i5[1], grid_lon, grid_lat)
    grid_lon, grid_lat = np.meshgrid(grid_lon, grid_lat)

    display = pyart.graph.RadarMapDisplayCartopy(radar)
    fig = plt.figure(figsize=[12, 8])
    display.plot_ppi_map('reflectivity', sweep=sweep, resolution='50m',
                         vmin=-8, vmax=64, mask_outside=False,
                         cmap=pyart.graph.cm.NWSRef,
                         min_lat=min_lat, min_lon=min_lon,
                         max_lat=max_lat, max_lon=max_lon,
                         lat_lines=lal, lon_lines=lol,
                         projection=ccrs.PlateCarree())
    if dd_lobes is True:
        plt.contour(grid_lon, grid_lat, bca,
                    levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                    colors='k')

    plt.savefig(
        image_directory
        + '/reflectivity' + combined_name + '.png')
    plt.close()

    # Four panel plot of gate_id, velocity_texture, reflectivity, and
    # cross_correlation_ratio.
    cat_dict = {}
    print('##')
    print('## Keys for each gate id are as follows:')
    for pair_str in radar.fields['gate_id']['notes'].split(','):
        print('##   ', str(pair_str))
        cat_dict.update({pair_str.split(':')[1]:int(pair_str.split(':')[0])})
    sorted_cats = sorted(cat_dict.items(), key=operator.itemgetter(1))
    cat_colors = {'rain': 'green',
                  'multi_trip': 'red',
                  'no_scatter': 'gray',
                  'snow': 'cyan',
                  'melting': 'yellow',
                  'clutter': 'black'}
    lab_colors = ['red', 'cyan', 'grey', 'green', 'yellow', 'black']
    lab_colors = [cat_colors[kitty[0]] for kitty in sorted_cats]
    cmap = matplotlib.colors.ListedColormap(lab_colors)

    display = pyart.graph.RadarMapDisplayCartopy(radar)
    fig = plt.figure(figsize=[15, 10])
    plt.subplot(2, 2, 1, projection=ccrs.PlateCarree())
    display.plot_ppi_map('gate_id', sweep=sweep, min_lon=min_lon,
                         max_lon=max_lon, min_lat=min_lat,
                         max_lat=max_lat, resolution='50m',
                         lat_lines=lal, lon_lines=lol, cmap=cmap,
                         vmin=0, vmax=5, projection=ccrs.PlateCarree())

    if dd_lobes is True:
        plt.contour(grid_lon, grid_lat, bca,
                    levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                    colors='k')

    cbax = plt.gca()
    tick_locs = np.linspace(0, len(sorted_cats) - 2, len(sorted_cats)) + 0.5
    display.cbs[-1].locator = matplotlib.ticker.FixedLocator(tick_locs)
    catty_list = [sorted_cats[i][0] for i in range(len(sorted_cats))]
    display.cbs[-1].formatter = matplotlib.ticker.FixedFormatter(catty_list)
    display.cbs[-1].update_ticks()
    plt.subplot(2, 2, 2, projection=ccrs.PlateCarree())
    display.plot_ppi_map('reflectivity', sweep=sweep, vmin=-8, vmax=64,
                         min_lon=min_lon, max_lon=max_lon, min_lat=min_lat,
                         max_lat=max_lat, lat_lines=lal, lon_lines=lol,
                         resolution='50m', cmap=pyart.graph.cm.NWSRef,
                         projection=ccrs.PlateCarree())
    if dd_lobes is True:
        plt.contour(grid_lon, grid_lat, bca,
                    levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                    colors='k')

    plt.subplot(2, 2, 3, projection=ccrs.PlateCarree())
    display.plot_ppi_map('velocity_texture', sweep=sweep, vmin=0, vmax=14,
                         min_lon=min_lon, max_lon=max_lon, min_lat=min_lat,
                         max_lat=max_lat, lat_lines=lal, lon_lines=lol,
                         resolution='50m',
                         title=_generate_title(
                             radar, 'velocity_texture', sweep),
                         cmap=pyart.graph.cm.NWSRef,
                         projection=ccrs.PlateCarree())
    if dd_lobes is True:
        plt.contour(grid_lon, grid_lat, bca, latlon='True',
                    levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                    colors='k')
    plt.subplot(2, 2, 4, projection=ccrs.PlateCarree())
    display.plot_ppi_map('cross_correlation_ratio', sweep=sweep, vmin=.5,
                         vmax=1, min_lon=min_lon, max_lon=max_lon,
                         min_lat=min_lat, max_lat=max_lat, lat_lines=lal,
                         lon_lines=lol, resolution='50m',
                         cmap=pyart.graph.cm.Carbone42,
                         projection=ccrs.PlateCarree())
    if dd_lobes is True:
        plt.contour(grid_lon, grid_lat, bca,
                    levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                    colors='k')
    plt.savefig(
        image_directory
        + '/cmac_four_panel_plot' + combined_name + '.png')
    plt.close()

    # Creating a plot with reflectivity corrected with gate ids.
    cmac_gates = pyart.correct.GateFilter(radar)
    cmac_gates.exclude_all()
    cmac_gates.include_equal('gate_id', cat_dict['rain'])
    cmac_gates.include_equal('gate_id', cat_dict['melting'])
    cmac_gates.include_equal('gate_id', cat_dict['snow'])

    display = pyart.graph.RadarMapDisplayCartopy(radar)
    fig = plt.figure(figsize=[12, 8])
    display.plot_ppi_map('reflectivity',
                         sweep=sweep, resolution='50m',
                         vmin=-8, vmax=64, mask_outside=False,
                         cmap=pyart.graph.cm.NWSRef,
                         title=_generate_title(
                             radar, 'masked_corrected_reflectivity',
                             sweep),
                         min_lat=min_lat, min_lon=min_lon,
                         max_lat=max_lat, max_lon=max_lon,
                         lat_lines=lal, lon_lines=lol,
                         gatefilter=cmac_gates,
                         projection=ccrs.PlateCarree())
    if dd_lobes is True:
        plt.contour(grid_lon, grid_lat, bca,
                    levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                    colors='k')
    plt.savefig(
        image_directory
        + '/masked_corrected_reflectivity' + combined_name + '.png')
    plt.close()

    # Creating a plot with reflectivity corrected with attenuation.
    display = pyart.graph.RadarMapDisplayCartopy(radar)
    fig = plt.figure(figsize=[12, 8])
    display.plot_ppi_map('attenuation_corrected_reflectivity', sweep=sweep,
                         vmin=0, vmax=60., resolution='50m',
                         title=_generate_title(
                             radar, 'attenuation_corrected_reflectivity',
                             sweep),
                         min_lat=min_lat, min_lon=min_lon,
                         max_lat=max_lat, max_lon=max_lon,
                         lat_lines=lal, lon_lines=lol,
                         projection=ccrs.PlateCarree())
    if dd_lobes is True:
        plt.contour(grid_lon, grid_lat, bca,
                    levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                    colors='k')
    plt.savefig(
        image_directory
        + '/attenuation_corrected_reflectivity' + combined_name + '.png')
    plt.close()

    # Creating a plot of specific attenuation.
    display = pyart.graph.RadarMapDisplayCartopy(radar)
    fig = plt.figure(figsize=[12, 8])
    display.plot_ppi_map('specific_attenuation', sweep=sweep, vmin=0,
                         vmax=1.0, resolution='50m',
                         min_lat=min_lat, min_lon=min_lon,
                         max_lat=max_lat, max_lon=max_lon,
                         lat_lines=lal, lon_lines=lol,
                         projection=ccrs.PlateCarree())
    if dd_lobes is True:
        plt.contour(grid_lon, grid_lat, bca,
                    levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                    colors='k')
    plt.savefig(
        image_directory
        + '/specific_attenuation' + combined_name + '.png')
    plt.close()

    # Creating a plot of corrected differential phase.
    display = pyart.graph.RadarMapDisplayCartopy(radar)
    fig = plt.figure(figsize=[12, 8])
    display.plot_ppi_map('corrected_differential_phase', sweep=sweep,
                         title=_generate_title(
                             radar, 'corrected_differential_phase',
                             sweep),
                         resolution='50m', min_lat=min_lat,
                         min_lon=min_lon, max_lat=max_lat, max_lon=max_lon,
                         lat_lines=lal, lon_lines=lol,
                         projection=ccrs.PlateCarree())
    if dd_lobes is True:
        plt.contour(grid_lon, grid_lat, bca,
                    levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                    colors='k')
    plt.savefig(
        image_directory
        + '/corrected_differential_phase' + combined_name + '.png')
    plt.close()

    # Creating a plot of corrected specific differential phase.
    display = pyart.graph.RadarMapDisplayCartopy(radar)
    fig = plt.figure(figsize=[12, 8])
    display.plot_ppi_map('corrected_specific_diff_phase', sweep=sweep,
                         vmin=0, vmax=6, resolution='50m',
                         title=_generate_title(
                             radar, 'corrected_specific_diff_phase',
                             sweep),
                         min_lat=min_lat, min_lon=min_lon, max_lat=max_lat,
                         max_lon=max_lon, lat_lines=lal, lon_lines=lol,
                         projection=ccrs.PlateCarree())
    if dd_lobes is True:
        plt.contour(grid_lon, grid_lat, bca,
                    levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                    colors='k')
    plt.savefig(
        image_directory
        + '/corrected_specific_diff_phase' + combined_name + '.png')
    plt.close()

    # Creating a plot with region dealias corrected velocity.
    nyq = radar.instrument_parameters['nyquist_velocity']['data'][0]
    display = pyart.graph.RadarMapDisplayCartopy(radar)
    fig = plt.figure(figsize=[12, 8])
    display.plot_ppi_map('corrected_velocity', sweep=sweep, resolution='50m',
                         cmap=pyart.graph.cm.NWSVel, vmin=-1.5*nyq,
                         vmax=1.5*nyq, min_lat=min_lat, min_lon=min_lon,
                         max_lat=max_lat, max_lon=max_lon, lat_lines=lal,
                         lon_lines=lol, projection=ccrs.PlateCarree())
    if dd_lobes is True:
        plt.contour(grid_lon, grid_lat, bca,
                    levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                    colors='k')
    plt.savefig(
        image_directory
        + '/corrected_velocity' + combined_name + '.png')
    plt.close()

    # Creating a plot of rain rate A
    display = pyart.graph.RadarMapDisplayCartopy(radar)
    fig = plt.figure(figsize=[12, 8])
    display.plot_ppi_map('rain_rate_A', sweep=sweep, resolution='50m',
                         vmin=0, vmax=120, min_lat=min_lat, min_lon=min_lon,
                         max_lat=max_lat, max_lon=max_lon, lat_lines=lal,
                         lon_lines=lol, projection=ccrs.PlateCarree())
    if dd_lobes is True:
        plt.contour(grid_lon, grid_lat, bca,
                    levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                    colors='k')
    plt.savefig(
        image_directory
        + '/rain_rate_A' + combined_name + '.png')
    plt.close()

    # Creating a plot of filtered corrected differential phase.
    display = pyart.graph.RadarMapDisplayCartopy(radar)
    fig = plt.figure(figsize=[12, 8])
    display.plot_ppi_map('filtered_corrected_differential_phase', sweep=sweep,
                         title=_generate_title(
                             radar, 'filtered_corrected_differential_phase',
                             sweep),
                         resolution='50m', min_lat=min_lat,
                         min_lon=min_lon, max_lat=max_lat, max_lon=max_lon,
                         lat_lines=lal, lon_lines=lol,
                         cmap=pyart.graph.cm.Theodore16,
                         projection=ccrs.PlateCarree())
    if dd_lobes is True:
        plt.contour(grid_lon, grid_lat, bca,
                    levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                    colors='k')
    plt.savefig(
        image_directory
        + '/filtered_corrected_differential_phase' + combined_name + '.png')
    plt.close()

    # Creating a plot of filtered corrected specific differential phase.
    display = pyart.graph.RadarMapDisplayCartopy(radar)
    fig = plt.figure(figsize=[12, 8])
    display.plot_ppi_map('filtered_corrected_specific_diff_phase', sweep=sweep,
                         title=_generate_title(
                             radar, 'filtered_corrected_specific_diff_phase',
                             sweep),
                         resolution='50m', min_lat=min_lat,
                         min_lon=min_lon, max_lat=max_lat, max_lon=max_lon,
                         lat_lines=lal, lon_lines=lol,
                         cmap=pyart.graph.cm.Theodore16,
                         projection=ccrs.PlateCarree())
    if dd_lobes is True:
        plt.contour(grid_lon, grid_lat, bca,
                    levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                    colors='k')
    plt.savefig(
        image_directory
        + '/filtered_corrected_specific_diff_phase' + combined_name + '.png')
    plt.close()


def _generate_title(radar, field, sweep):
    """ Generates a title for each plot. """
    time_str = generate_radar_time_begin(radar).isoformat() + 'Z'
    fixed_angle = radar.fixed_angle['data'][sweep]
    line_one = "%s %.1f Deg. %s " % (generate_radar_name(radar), fixed_angle,
                                     time_str)
    field_name = str(field)
    field_name = field_name.replace('_', ' ')
    field_name = field_name[0].upper() + field_name[1:]
    return line_one + '\n' + field_name


def _get_bca(rad1_lon, rad1_lat, rad2_lon, rad2_lat,
             grid_lon, grid_lat):
    # Beam crossing angle needs cartesian coordinate.
    p = ccrs.PlateCarree()
    p = p.as_geocentric()
    rad1 = p.transform_points(ccrs.PlateCarree().as_geodetic(),
                              np.array(rad1_lon),
                              np.array(rad1_lat))
    rad2 = p.transform_points(ccrs.PlateCarree().as_geodetic(),
                              np.array(rad2_lon),
                              np.array(rad2_lat))
    grid_lon, grid_lat = np.meshgrid(grid_lon, grid_lat)
    grid = p.transform_points(ccrs.PlateCarree().as_geodetic(),
                              grid_lon, grid_lat,
                              np.zeros(grid_lon.shape))

    # Create grid with Radar 1 in center.
    x = grid[:, :, 0] - rad1[0, 0]
    y = grid[:, :, 1] - rad1[0, 1]
    rad2 = rad2 - rad1
    a = np.sqrt(np.multiply(x, x) + np.multiply(y, y))
    b = np.sqrt(pow(x - rad2[0, 0], 2) + pow(y - rad2[0, 1], 2))
    c = np.sqrt(rad2[0, 0] * rad2[0, 0] + rad2[0, 1] * rad2[0, 1])
    theta_1 = np.arccos(x/a)
    theta_2 = np.arccos((x - rad2[0, 1]) / b)
    return np.arccos((a*a + b*b - c*c) / (2*a*b))


def _dms_to_decimal(degrees, minutes, seconds):
    if degrees > 0:
        return degrees + minutes/60 + seconds/3600
    else:
        return degrees - minutes/60 - seconds/3600
