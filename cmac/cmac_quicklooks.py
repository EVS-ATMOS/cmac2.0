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

from pyart.graph.common import (
    generate_radar_name, generate_radar_time_begin)

from .config import get_plot_values, get_field_names

plt.switch_backend('agg')


def quicklooks(radar, config, image_directory=None,
               dd_lobes=True):
    """
    Quicklooks, images produced with regards to CMAC

    Parameter
    ---------
    radar : Radar
        Radar object that has CMAC applied to it.
    config : str
        A string of the radar name found from config.py that contains values
        for plotting, specific to that radar.

    Optional Parameters
    -------------------
    image_directory : str
        File path to the image folder of which to save the CMAC images. If no
        image file path is given, image path defaults to users home directory.
    dd_lobes : bool
        Plot DD lobes between radars if dd_lobes is True.

    """
    if image_directory is None:
        image_directory = os.path.expanduser('~')

    radar_start_date = netCDF4.num2date(
        radar.time['data'][0], radar.time['units'],
        only_use_cftime_datetimes=False, only_use_python_datetimes=True)

    # Retrieve the plot parameter values based on the radar.
    plot_config = get_plot_values(config)
    field_config = get_field_names(config)
    save_name = plot_config['save_name']
    date_string = datetime.strftime(radar_start_date, '%Y%m%d.%H%M%S')
    combined_name = '.' + save_name + '.' + date_string

    #min_lat = plot_config['min_lat']
    #max_lat = plot_config['max_lat']
    #min_lon = plot_config['min_lon']
    #max_lon = plot_config['max_lon']

    max_lat = radar.gate_latitude['data'].max() + .1
    min_lat = radar.gate_latitude['data'].min() - .1
    max_lon = radar.gate_longitude['data'].max() + .1
    min_lon = radar.gate_longitude['data'].min() - .1

    # Creating a plot of reflectivity before CMAC.
    lal = np.arange(min_lat, max_lat, .5)
    lol = np.arange(min_lon, max_lon, .5)

    if dd_lobes:
        grid_lat = np.arange(min_lat, max_lat, 0.01)
        grid_lon = np.arange(min_lon, max_lon, 0.01)

        facility = plot_config['facility']
        if facility == 'I4':
            dms_radar1_coords = [plot_config['site_i4_dms_lon'],
                                 plot_config['site_i4_dms_lat']]
            dms_radar2_coords = [plot_config['site_i5_dms_lon'],
                                 plot_config['site_i5_dms_lat']]
        elif facility == 'I5':
            dms_radar1_coords = [plot_config['site_i5_dms_lon'],
                                 plot_config['site_i5_dms_lat']]
            dms_radar2_coords = [plot_config['site_i4_dms_lon'],
                                 plot_config['site_i4_dms_lat']]
        elif facility == 'I6':
            dms_radar1_coords = [plot_config['site_i6_dms_lon'],
                                 plot_config['site_i6_dms_lat']]
            dms_radar2_coords = [plot_config['site_i4_dms_lon'],
                                 plot_config['site_i4_dms_lat']]

        dec_radar1 = [_dms_to_decimal(
            dms_radar1_coords[0][0], dms_radar1_coords[0][1],
            dms_radar1_coords[0][2]), _dms_to_decimal(
                dms_radar1_coords[1][0], dms_radar1_coords[1][1],
                dms_radar1_coords[1][2])]
        dec_radar2 = [_dms_to_decimal(
            dms_radar2_coords[0][0], dms_radar2_coords[0][1],
            dms_radar2_coords[0][2]), _dms_to_decimal(
                dms_radar2_coords[1][0], dms_radar2_coords[1][1],
                dms_radar2_coords[1][2])]

        bca = _get_bca(dec_radar2[0], dec_radar2[1], dec_radar1[0],
                       dec_radar1[1], grid_lon, grid_lat)
        grid_lon, grid_lat = np.meshgrid(grid_lon, grid_lat)

    sweep = plot_config['sweep']

    # Plot of the raw reflectivity from the radar.
    display = pyart.graph.RadarMapDisplay(radar)
    fig, ax = plt.subplots(1, 1, 
                           subplot_kw=dict(projection=ccrs.PlateCarree()), 
                           figsize=[12, 8])
    display.plot_ppi_map('reflectivity', sweep=sweep, resolution='50m', ax=ax,
                         vmin=-8, vmax=64, mask_outside=False,
                         cmap=pyart.graph.cm_colorblind.HomeyerRainbow,
                         min_lat=min_lat, min_lon=min_lon,
                         max_lat=max_lat, max_lon=max_lon,
                         lat_lines=lal, lon_lines=lol,
                         projection=ccrs.PlateCarree())
    if dd_lobes:
        ax.contour(grid_lon, grid_lat, bca,
                   levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                   colors='k')

    fig.savefig(
        image_directory
        + '/reflectivity' + combined_name + '.png')
    del fig, ax

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
                  'melting': 'yellow'}
    lab_colors = ['red', 'cyan', 'grey', 'green', 'yellow']
    if 'ground_clutter' in radar.fields.keys():
        cat_colors['clutter'] = 'black'
        lab_colors = np.append(lab_colors, 'black')
    if 'terrain_blockage' in radar.fields['gate_id']['notes']:
        cat_colors['terrain_blockage'] = 'brown'
        lab_colors = np.append(lab_colors, 'brown')
    lab_colors = [cat_colors[kitty[0]] for kitty in sorted_cats]
    cmap = matplotlib.colors.ListedColormap(lab_colors)

    display = pyart.graph.RadarMapDisplay(radar)
    fig, ax = plt.subplots(2, 2,
              figsize=[15, 10], subplot_kw=dict(projection=ccrs.PlateCarree()))
    display.plot_ppi_map('gate_id', sweep=sweep, min_lon=min_lon, ax=ax[0, 0],
                         max_lon=max_lon, min_lat=min_lat,
                         max_lat=max_lat, resolution='50m',
                         lat_lines=lal, lon_lines=lol, cmap=cmap,
                         vmin=0, vmax=6, projection=ccrs.PlateCarree())

    if dd_lobes:
        ax[0,0].contour(grid_lon, grid_lat, bca,
                        levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                        colors='k')

    cbax = ax[0,0]
    if 'ground_clutter' in radar.fields.keys() or 'terrain_blockage' in radar.fields['gate_id']['notes']:
        tick_locs = np.linspace(
            0, len(sorted_cats) - 2, len(sorted_cats)) + 0.5
    else:
        tick_locs = np.linspace(
            0, len(sorted_cats) - 1, len(sorted_cats)) + 0.5
    display.cbs[-1].locator = matplotlib.ticker.FixedLocator(tick_locs)
    catty_list = [sorted_cats[i][0] for i in range(len(sorted_cats))]
    display.cbs[-1].formatter = matplotlib.ticker.FixedFormatter(catty_list)
    display.cbs[-1].update_ticks()
    
    display.plot_ppi_map('reflectivity', sweep=sweep, vmin=-8, vmax=64, 
                         ax=ax[0, 1], min_lon=min_lon, max_lon=max_lon,
                         min_lat=min_lat,
                         max_lat=max_lat, lat_lines=lal, lon_lines=lol,
                         resolution='50m',
                         cmap=pyart.graph.cm_colorblind.HomeyerRainbow,
                         projection=ccrs.PlateCarree())
    if dd_lobes:
        ax[0,1].contour(grid_lon, grid_lat, bca,
                        levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                        colors='k')

    display.plot_ppi_map('velocity_texture', sweep=sweep, vmin=0, vmax=14,
                         min_lon=min_lon, max_lon=max_lon, min_lat=min_lat,
                         max_lat=max_lat, lat_lines=lal, lon_lines=lol,
                         resolution='50m', ax=ax[1, 0],
                         title=_generate_title(
                             radar, 'velocity_texture', sweep),
                         cmap=pyart.graph.cm.NWSRef,
                         projection=ccrs.PlateCarree())
    if dd_lobes:
        ax[1,0].contour(grid_lon, grid_lat, bca, latlon='True',
                        levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                         colors='k')
    
    rhv_field = field_config['cross_correlation_ratio']
    display.plot_ppi_map(rhv_field, sweep=sweep, vmin=.5,
                         vmax=1, min_lon=min_lon, max_lon=max_lon,
                         min_lat=min_lat, max_lat=max_lat, lat_lines=lal,
                         lon_lines=lol, resolution='50m', ax=ax[1, 1],
                         cmap=pyart.graph.cm.Carbone42,
                         projection=ccrs.PlateCarree())
    if dd_lobes:
        ax[1,1].contour(grid_lon, grid_lat, bca,
                        levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                        colors='k')
    fig.savefig(
        image_directory
        + '/cmac_four_panel_plot' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

    # Creating a plot with reflectivity corrected with gate ids.
    cmac_gates = pyart.correct.GateFilter(radar)
    cmac_gates.exclude_all()
    cmac_gates.include_equal('gate_id', cat_dict['rain'])
    cmac_gates.include_equal('gate_id', cat_dict['melting'])
    cmac_gates.include_equal('gate_id', cat_dict['snow'])

    display = pyart.graph.RadarMapDisplay(radar)
    fig, ax = plt.subplots(1, 1, subplot_kw=dict(projection=ccrs.PlateCarree()),
                          figsize=[12, 8])
    display.plot_ppi_map('reflectivity',
                         sweep=sweep, resolution='50m',
                         vmin=-8, vmax=64, mask_outside=False,
                         cmap=pyart.graph.cm_colorblind.HomeyerRainbow,
                         title=_generate_title(
                             radar, 'masked_corrected_reflectivity',
                             sweep), ax=ax,
                         min_lat=min_lat, min_lon=min_lon,
                         max_lat=max_lat, max_lon=max_lon,
                         lat_lines=lal, lon_lines=lol,
                         gatefilter=cmac_gates,
                         projection=ccrs.PlateCarree())
    if dd_lobes:
        ax.contour(grid_lon, grid_lat, bca,
                   levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                   colors='k')
    fig.savefig(
        image_directory
        + '/masked_corrected_reflectivity' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display


    # Creating a plot with reflectivity corrected with attenuation.
    display = pyart.graph.RadarMapDisplay(radar)
    fig, ax = plt.subplots(1, 1, subplot_kw=dict(projection=ccrs.PlateCarree()),
                           figsize=[12, 8])
    display.plot_ppi_map('corrected_reflectivity', sweep=sweep,
                         vmin=0, vmax=60., resolution='50m',
                         title=_generate_title(
                             radar, 'corrected_reflectivity',
                             sweep),
                         cmap=pyart.graph.cm_colorblind.HomeyerRainbow,
                         min_lat=min_lat, min_lon=min_lon,
                         max_lat=max_lat, max_lon=max_lon,
                         lat_lines=lal, lon_lines=lol, ax=ax,
                         projection=ccrs.PlateCarree())
    if dd_lobes:
        ax.contour(grid_lon, grid_lat, bca,
                   levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                   colors='k')
    fig.savefig(
        image_directory
        + '/corrected_reflectivity' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

    # Creating a plot with differential phase.
    display = pyart.graph.RadarMapDisplay(radar)
    fig, ax = plt.subplots(1, 1, subplot_kw=dict(projection=ccrs.PlateCarree()),
                          figsize=[12, 8])
    display.plot_ppi_map('differential_phase', sweep=sweep,
                         resolution='50m', ax=ax,
                         min_lat=min_lat, min_lon=min_lon,
                         max_lat=max_lat, max_lon=max_lon,
                         lat_lines=lal, lon_lines=lol,
                         projection=ccrs.PlateCarree())
    fig.savefig(
        image_directory
        + '/differential_phase' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display


    # Creating a plot of specific attenuation.
    display = pyart.graph.RadarMapDisplay(radar)
    fig, ax = plt.subplots(1, 1, subplot_kw=dict(projection=ccrs.PlateCarree()),
                          figsize=[12, 8])
    display.plot_ppi_map('specific_attenuation', sweep=sweep, vmin=0,
                         vmax=1.0, resolution='50m', ax=ax,
                         min_lat=min_lat, min_lon=min_lon,
                         max_lat=max_lat, max_lon=max_lon,
                         lat_lines=lal, lon_lines=lol,
                         projection=ccrs.PlateCarree())
    if dd_lobes:
        ax.contour(grid_lon, grid_lat, bca,
                    levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                    colors='k')
    fig.savefig(
        image_directory
        + '/specific_attenuation' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

    # Creating a plot of corrected differential phase.
    display = pyart.graph.RadarMapDisplay(radar)
    fig, ax = plt.subplots(1, 1, subplot_kw=dict(projection=ccrs.PlateCarree()),
                          figsize=[12, 8])
    display.plot_ppi_map('corrected_differential_phase', sweep=sweep,
                         title=_generate_title(
                             radar, 'corrected_differential_phase',
                             sweep), ax=ax,
                         resolution='50m', min_lat=min_lat,
                         min_lon=min_lon, max_lat=max_lat, max_lon=max_lon,
                         lat_lines=lal, lon_lines=lol,
                         projection=ccrs.PlateCarree())
    if dd_lobes:
        ax.contour(grid_lon, grid_lat, bca,
                   levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                   colors='k')
    fig.savefig(
        image_directory
        + '/corrected_differential_phase' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

    # Creating a plot of corrected specific differential phase.
    display = pyart.graph.RadarMapDisplay(radar)
    fig, ax = plt.subplots(1, 1, subplot_kw=dict(projection=ccrs.PlateCarree()),
                          figsize=[12, 8])
    display.plot_ppi_map('corrected_specific_diff_phase', sweep=sweep,
                         vmin=0, vmax=6, resolution='50m',
                         title=_generate_title(
                             radar, 'corrected_specific_diff_phase',
                             sweep), ax=ax,
                         min_lat=min_lat, min_lon=min_lon, max_lat=max_lat,
                         max_lon=max_lon, lat_lines=lal, lon_lines=lol,
                         projection=ccrs.PlateCarree())
    if dd_lobes:
        ax.contour(grid_lon, grid_lat, bca,
                   levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                   colors='k')
    fig.savefig(
        image_directory
        + '/corrected_specific_diff_phase' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

    # Creating a plot with region dealias corrected velocity.
    display = pyart.graph.RadarMapDisplay(radar)
    fig, ax = plt.subplots(1, 1, subplot_kw=dict(projection=ccrs.PlateCarree()),
                          figsize=[12, 8])
    display.plot_ppi_map('corrected_velocity', sweep=sweep, resolution='50m',
                         cmap=pyart.graph.cm.NWSVel, vmin=-30, ax=ax,
                         vmax=30, min_lat=min_lat, min_lon=min_lon,
                         max_lat=max_lat, max_lon=max_lon, lat_lines=lal,
                         lon_lines=lol, projection=ccrs.PlateCarree())
    if dd_lobes:
        ax.contour(grid_lon, grid_lat, bca,
                   levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                   colors='k')
    fig.savefig(
        image_directory
        + '/corrected_velocity' + combined_name + '.png')
    plt.close(fig) 
    del fig, ax, display

    # Creating a plot of rain rate A
    display = pyart.graph.RadarMapDisplay(radar)
    fig, ax = plt.subplots(1, 1, subplot_kw=dict(projection=ccrs.PlateCarree()),
                          figsize=[12, 8])
    display.plot_ppi_map('rain_rate_A', sweep=sweep, resolution='50m',
                         vmin=0, vmax=120, min_lat=min_lat, min_lon=min_lon,
                         max_lat=max_lat, ax=ax, max_lon=max_lon, lat_lines=lal,
                         lon_lines=lol, projection=ccrs.PlateCarree())
    if dd_lobes:
        ax.contour(grid_lon, grid_lat, bca,
                   levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                   colors='k')
    fig.savefig(
        image_directory
        + '/rain_rate_A' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

    # Creating a plot of filtered corrected differential phase.
    display = pyart.graph.RadarMapDisplay(radar)
    fig, ax = plt.subplots(1, 1, subplot_kw=dict(projection=ccrs.PlateCarree()),
                          figsize=[12, 8])
    display.plot_ppi_map('filtered_corrected_differential_phase', sweep=sweep,
                         title=_generate_title(
                             radar, 'filtered_corrected_differential_phase',
                             sweep),
                         resolution='50m', min_lat=min_lat, ax=ax,
                         min_lon=min_lon, max_lat=max_lat, max_lon=max_lon,
                         lat_lines=lal, lon_lines=lol,
                         cmap=pyart.graph.cm.Theodore16,
                         projection=ccrs.PlateCarree())
    if dd_lobes:
        ax.contour(grid_lon, grid_lat, bca,
                    levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                    colors='k')
    fig.savefig(
        image_directory
        + '/filtered_corrected_differential_phase' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

    # Creating a plot of filtered corrected specific differential phase.
    display = pyart.graph.RadarMapDisplay(radar)
    fig, ax = plt.subplots(1, 1, subplot_kw=dict(projection=ccrs.PlateCarree()),
                          figsize=[12, 8])
    display.plot_ppi_map('filtered_corrected_specific_diff_phase', sweep=sweep,
                         title=_generate_title(
                             radar, 'filtered_corrected_specific_diff_phase',
                             sweep), ax=ax,
                         resolution='50m', min_lat=min_lat,
                         min_lon=min_lon, max_lat=max_lat, max_lon=max_lon,
                         lat_lines=lal, lon_lines=lol,
                         cmap=pyart.graph.cm.Theodore16,
                         projection=ccrs.PlateCarree())
    if dd_lobes:
        ax.contour(grid_lon, grid_lat, bca,
                    levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                    colors='k')
    fig.savefig(
        image_directory
        + '/filtered_corrected_specific_diff_phase' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

    # Creating a plot of corrected differential phase.
    display = pyart.graph.RadarMapDisplay(radar)
    fig, ax = plt.subplots(1, 1, subplot_kw=dict(projection=ccrs.PlateCarree()),
                          figsize=[12, 8])
    display.plot_ppi_map('specific_differential_attenuation', sweep=sweep,
                         title=_generate_title(
                             radar, 'specific_differential_attenuation',
                             sweep), ax=ax,
                         resolution='50m', min_lat=min_lat,
                         min_lon=min_lon, max_lat=max_lat, max_lon=max_lon,
                         lat_lines=lal, lon_lines=lol, gatefilter=cmac_gates,
                         projection=ccrs.PlateCarree())
    if dd_lobes:
        ax.contour(grid_lon, grid_lat, bca,
                   levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                   colors='k')
    fig.savefig(
        image_directory
        + '/specific_differential_attenuation' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

    # Creating a plot of corrected differential phase.
    display = pyart.graph.RadarMapDisplay(radar)
    fig, ax = plt.subplots(1, 1, subplot_kw=dict(projection=ccrs.PlateCarree()),
                          figsize=[12, 8])
    display.plot_ppi_map('path_integrated_differential_attenuation',
                         sweep=sweep,
                         title=_generate_title(
                             radar, 'path_integrated_differential_attenuation',
                             sweep), ax=ax,
                         resolution='50m', min_lat=min_lat,
                         min_lon=min_lon, max_lat=max_lat, max_lon=max_lon,
                         lat_lines=lal, lon_lines=lol, gatefilter=cmac_gates,
                         projection=ccrs.PlateCarree())
    if dd_lobes:
        ax.contour(grid_lon, grid_lat, bca,
                   levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                   colors='k')
    fig.savefig(
        image_directory
        + '/path_integrated_differential_attenuation' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

    # Creating a plot of corrected differential phase.
    display = pyart.graph.RadarMapDisplay(radar)
    fig, ax = plt.subplots(1, 1, subplot_kw=dict(projection=ccrs.PlateCarree()),
                          figsize=[12, 8])
    display.plot_ppi_map('corrected_differential_reflectivity', sweep=sweep,
                         title=_generate_title(
                             radar, 'corrected_differential_reflectivity',
                             sweep), ax=ax,
                         resolution='50m', min_lat=min_lat,
                         min_lon=min_lon, max_lat=max_lat, max_lon=max_lon,
                         lat_lines=lal, lon_lines=lol, gatefilter=cmac_gates,
                         projection=ccrs.PlateCarree())
    if dd_lobes:
        ax.contour(grid_lon, grid_lat, bca,
                    levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                    colors='k')
    fig.savefig(
        image_directory
        + '/corrected_differential_reflectivity' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

    # Creating a plot with reflectivity corrected with attenuation.
    display = pyart.graph.RadarMapDisplay(radar)
    fig, ax = plt.subplots(1, 1, subplot_kw=dict(projection=ccrs.PlateCarree()),
                           figsize=[12, 8])
    display.plot_ppi_map('normalized_coherent_power', sweep=sweep,
                         resolution='50m',
                         title=_generate_title(
                             radar, 'normalized_coherent_power',
                             sweep),
                         min_lat=min_lat, min_lon=min_lon,
                         max_lat=max_lat, max_lon=max_lon,
                         lat_lines=lal, lon_lines=lol, ax=ax,
                         projection=ccrs.PlateCarree())
    if dd_lobes:
        ax.contour(grid_lon, grid_lat, bca,
                   levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                   colors='k')
    fig.savefig(
        image_directory
        + '/normalized_coherent_power' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

   # Creating a plot with reflectivity corrected with attenuation.
    display = pyart.graph.RadarMapDisplay(radar)
    fig, ax = plt.subplots(1, 1, subplot_kw=dict(projection=ccrs.PlateCarree()),
                           figsize=[12, 8])
    display.plot_ppi_map('signal_to_noise_ratio', sweep=sweep,
                         resolution='50m',
                         title=_generate_title(
                             radar, 'signal_to_noise_ratio',
                             sweep),
                         min_lat=min_lat, min_lon=min_lon,
                         max_lat=max_lat, max_lon=max_lon,
                         lat_lines=lal, lon_lines=lol, ax=ax,
                         projection=ccrs.PlateCarree())
    if dd_lobes:
        ax.contour(grid_lon, grid_lat, bca,
                   levels=[np.pi/6, 5*np.pi/6], linewidths=2,
                   colors='k')
    fig.savefig(
        image_directory
        + '/signal_to_noise_ratio' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display


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
