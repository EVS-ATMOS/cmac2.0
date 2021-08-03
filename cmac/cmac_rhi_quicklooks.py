""" Code that plots fields from the CMAC radar object. """

import os
from datetime import datetime
import operator

import netCDF4
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pyart

from pyart.graph.common import (
    generate_radar_name, generate_radar_time_begin)

from .config import get_plot_values, get_field_names

plt.switch_backend('agg')


def quicklooks_rhi(radar, config, sweep=None, image_directory=None):
    """
    Quicklooks RHI, images produced with regards to CMAC

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

    ymax = 10
    ymin = 0
    if sweep is None:
        if radar.nsweeps < 4:
            sweep = 2
        else:
            sweep = plot_config['sweep']

    # Plot of the raw reflectivity from the radar.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=[12, 8])
    ax.set_aspect('auto')
    display.plot_rhi('reflectivity', sweep=sweep, ax=ax,
                         vmin=-8, vmax=64, mask_outside=False,
                         cmap=pyart.graph.cm_colorblind.HomeyerRainbow)
    plt.ylim(ymin, ymax)

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

    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(2, 2, figsize=[15, 10])
    ax[0, 0].set_aspect('auto')
    display.plot_rhi('gate_id', sweep=sweep, ax=ax[0, 0],
                     cmap=cmap, vmin=0, vmax=6)
    plt.ylim(ymin, ymax)

    cbax = ax[0, 0]
    if 'ground_clutter' in radar.fields.keys() or 'terrain_blockage' in radar.fields['gate_id']['notes']:
        tick_locs = np.linspace(
            0, len(sorted_cats) - 1, len(sorted_cats)) + 0.5
    else:
        tick_locs = np.linspace(
            0, len(sorted_cats), len(sorted_cats)) + 0.5
    display.cbs[-1].locator = matplotlib.ticker.FixedLocator(tick_locs)
    catty_list = [sorted_cats[i][0] for i in range(len(sorted_cats))]
    display.cbs[-1].formatter = matplotlib.ticker.FixedFormatter(catty_list)
    display.cbs[-1].update_ticks()
    ax[0, 1].set_aspect('auto')
    display.plot_rhi('reflectivity', sweep=sweep, vmin=-8, vmax=40.0, 
                         ax=ax[0, 1],
                         cmap=pyart.graph.cm_colorblind.HomeyerRainbow)
    plt.ylim(ymin, ymax)
    ax[1, 0].set_aspect('auto')
    display.plot_rhi('velocity_texture', sweep=sweep, vmin=0, vmax=14,
                     ax=ax[1, 0],
                     title=_generate_title(
                         radar, 'velocity_texture', sweep),
                     cmap=pyart.graph.cm.NWSRef)
    plt.ylim(ymin, ymax)
    
    rhv_field = field_config['cross_correlation_ratio']
    ax[1, 1].set_aspect('auto')
    display.plot_rhi(rhv_field, sweep=sweep, vmin=.5,
                     vmax=1, ax=ax[1, 1],
                     cmap=pyart.graph.cm.Carbone42)
    plt.ylim(ymin, ymax)
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

    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=[12, 8])
    ax.set_aspect('auto')
    display.plot_rhi('reflectivity', sweep=sweep,
                     vmin=-8, vmax=40, mask_outside=False,
                     cmap=pyart.graph.cm_colorblind.HomeyerRainbow,
                     title=_generate_title(
                         radar, 'masked_corrected_reflectivity',
                         sweep), ax=ax,
                     gatefilter=cmac_gates)
    plt.ylim(ymin, ymax)
    fig.savefig(
        image_directory
        + '/masked_corrected_reflectivity' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display


    # Creating a plot with reflectivity corrected with attenuation.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=[12, 8])
    ax.set_aspect('auto')
    display.plot_rhi('corrected_reflectivity', sweep=sweep,
                     vmin=0, vmax=40.0,
                     title=_generate_title(
                         radar, 'corrected_reflectivity',
                         sweep),
                     cmap=pyart.graph.cm_colorblind.HomeyerRainbow,
                     ax=ax)
    plt.ylim(ymin, ymax)
    fig.savefig(
        image_directory
        + '/corrected_reflectivity' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

    # Creating a plot with differential phase.
    phase_field = field_config['input_phidp_field']
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=[12, 8])
    ax.set_aspect('auto')
    display.plot_rhi(phase_field, sweep=sweep, ax=ax)
    plt.ylim(ymin, ymax)
    fig.savefig(
        image_directory
        + '/differential_phase' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display


    # Creating a plot of specific attenuation.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=[12, 8])
    ax.set_aspect('auto')
    display.plot_rhi('specific_attenuation', sweep=sweep, vmin=0,
                     vmax=1.0,  ax=ax)
    plt.ylim(ymin, ymax)
    fig.savefig(
        image_directory
        + '/specific_attenuation' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

    # Creating a plot of corrected differential phase.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=[12, 8])
    ax.set_aspect('auto')
    display.plot_rhi('corrected_differential_phase', sweep=sweep,
                         title=_generate_title(
                             radar, 'corrected_differential_phase',
                             sweep), ax=ax)
    plt.ylim(ymin, ymax)
    fig.savefig(
        image_directory
        + '/corrected_differential_phase' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

    # Creating a plot of corrected specific differential phase.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=[12, 8])
    ax.set_aspect('auto')
    display.plot_rhi('corrected_specific_diff_phase', sweep=sweep,
                     vmin=0, vmax=6,
                     title=_generate_title(
                         radar, 'corrected_specific_diff_phase',
                         sweep), ax=ax)
    plt.ylim(ymin, ymax)
    fig.savefig(
        image_directory
        + '/corrected_specific_diff_phase' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

    # Creating a plot with region dealias corrected velocity.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=[12, 8])
    ax.set_aspect('auto')
    display.plot_rhi('corrected_velocity', sweep=sweep,
                     cmap=pyart.graph.cm.NWSVel, vmin=-30, ax=ax,
                     vmax=30)
    plt.ylim(ymin, ymax)
    fig.savefig(
        image_directory
        + '/corrected_velocity' + combined_name + '.png')
    plt.close(fig) 
    del fig, ax, display

    # Creating a plot of rain rate A
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=[12, 8])
    ax.set_aspect('auto')
    display.plot_rhi('rain_rate_A', sweep=sweep, vmin=0, vmax=120, ax=ax)
    plt.ylim(ymin, ymax)
    fig.savefig(
        image_directory
        + '/rain_rate_A' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

    # Creating a plot of filtered corrected differential phase.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=[12, 8])
    ax.set_aspect('auto')
    display.plot_rhi('filtered_corrected_differential_phase', sweep=sweep,
                     title=_generate_title(
                         radar, 'filtered_corrected_differential_phase',
                         sweep), ax=ax, cmap=pyart.graph.cm.Theodore16)
    plt.ylim(ymin, ymax)
    fig.savefig(
        image_directory
        + '/filtered_corrected_differential_phase' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

    # Creating a plot of filtered corrected specific differential phase.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=[12, 8])
    ax.set_aspect('auto')
    display.plot_rhi('filtered_corrected_specific_diff_phase', sweep=sweep,
                     title=_generate_title(
                         radar, 'filtered_corrected_specific_diff_phase',
                         sweep), ax=ax, cmap=pyart.graph.cm.Theodore16)
    plt.ylim(ymin, ymax)
    fig.savefig(
        image_directory
        + '/filtered_corrected_specific_diff_phase' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

    # Creating a plot of corrected differential phase.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=[12, 8])
    ax.set_aspect('auto')
    display.plot_rhi('specific_differential_attenuation', sweep=sweep,
                     title=_generate_title(
                         radar, 'specific_differential_attenuation',
                         sweep), ax=ax, gatefilter=cmac_gates)
    plt.ylim(ymin, ymax)
    fig.savefig(
        image_directory
        + '/specific_differential_attenuation' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

    # Creating a plot of corrected differential phase.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=[12, 8])
    ax.set_aspect('auto')
    display.plot_rhi('path_integrated_differential_attenuation',
                     sweep=sweep,
                     title=_generate_title(
                         radar, 'path_integrated_differential_attenuation',
                         sweep), ax=ax, gatefilter=cmac_gates)
    plt.ylim(ymin, ymax)
    fig.savefig(
        image_directory
        + '/path_integrated_differential_attenuation' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

    # Creating a plot of corrected differential phase.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=[12, 8])
    ax.set_aspect('auto')
    display.plot_rhi('corrected_differential_reflectivity', sweep=sweep,
                     title=_generate_title(
                         radar, 'corrected_differential_reflectivity',
                         sweep), ax=ax, gatefilter=cmac_gates)
    plt.ylim(ymin, ymax)
    fig.savefig(
        image_directory
        + '/corrected_differential_reflectivity' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

    # Creating a plot with reflectivity corrected with attenuation.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=[12, 8])
    ax.set_aspect('auto')
    display.plot_rhi('normalized_coherent_power', sweep=sweep,
                     title=_generate_title(
                         radar, 'normalized_coherent_power',
                         sweep), ax=ax)
    plt.ylim(ymin, ymax)
    fig.savefig(
        image_directory
        + '/normalized_coherent_power' + combined_name + '.png')
    plt.close(fig)
    del fig, ax, display

    # Creating a plot with reflectivity corrected with attenuation.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=[12, 8])
    ax.set_aspect('auto')
    display.plot_rhi('signal_to_noise_ratio', sweep=sweep,
                     title=_generate_title(
                         radar, 'signal_to_noise_ratio',
                         sweep), ax=ax)
    plt.ylim(ymin, ymax)
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
