""" Code that plots fields from the CMAC radar object. """

import os
from datetime import datetime
import operator

import netCDF4
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pyart
import cmweather

from pyart.graph.common import (
    generate_radar_name, generate_radar_time_begin)

from .config import get_plot_values, get_field_names
from .gate_id import get_gate_id_categories, gate_id_has_category

plt.switch_backend('agg')


def quicklooks_rhi(radar, config, sweep=None, image_directory=None,
                   config_file=None, return_figs=False):
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
        Ignored when ``return_figs`` is True.
    config_file : str or None
        Path to a YAML file whose values override the built-in defaults for
        the named ``config`` radar.
    return_figs : bool, default False
        When True, return a dict mapping plot name -> matplotlib Figure and
        DO NOT write PNGs to disk. Used by pytest-mpl regression tests.
        When False (default), each figure is saved to ``image_directory``
        and closed, and the function returns None.

    """
    if image_directory is None and not return_figs:
        image_directory = os.path.expanduser('~')

    figures = {}

    radar_start_date = netCDF4.num2date(
        radar.time['data'][0], radar.time['units'],
        only_use_cftime_datetimes=False, only_use_python_datetimes=True)

    # Retrieve the plot parameter values based on the radar.
    plot_config = get_plot_values(config, config_file=config_file)
    field_config = get_field_names(config, config_file=config_file)
    save_name = plot_config['save_name']
    date_string = datetime.strftime(radar_start_date, '%Y%m%d.%H%M%S')
    combined_name = '.' + save_name + '.' + date_string

    # Soft-coded layout / range defaults with hard-coded fallbacks.
    figsize_single = plot_config.get('figsize_single', [12, 8])
    figsize_panel = plot_config.get('figsize_panel', [15, 10])
    sweep_fallback_nsweeps_lt = plot_config.get(
        'sweep_fallback_nsweeps_lt', 4)
    sweep_fallback = plot_config.get('sweep_fallback', 2)
    cat_colors_cfg = dict(plot_config.get(
        'cat_colors', {
            'rain': 'green',
            'multi_trip': 'red',
            'no_scatter': 'gray',
            'snow': 'cyan',
            'melting': 'yellow',
            'clutter': 'black',
            'terrain_blockage': 'brown'}))

    def _range(key, default):
        return plot_config.get(key, default)

    ymax = plot_config.get('ymax', 10)
    ymin = plot_config.get('ymin', 0)
    if sweep is None:
        if radar.nsweeps < sweep_fallback_nsweeps_lt:
            sweep = sweep_fallback
        else:
            sweep = plot_config['sweep']

    # Plot of the raw reflectivity from the radar.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=figsize_single)
    ax.set_aspect('auto')
    display.plot_rhi('reflectivity', sweep=sweep, ax=ax,
                         vmin=_range('reflectivity_raw_vmin', -8),
                         vmax=_range('reflectivity_raw_vmax', 64),
                         mask_outside=False,
                         cmap='HomeyerRainbow')
    plt.ylim(ymin, ymax)

    figures['reflectivity'] = fig

    # Four panel plot of gate_id, velocity_texture, reflectivity, and
    # cross_correlation_ratio.
    gate_id_field = radar.fields['gate_id']
    cat_dict = get_gate_id_categories(gate_id_field)
    print('##')
    print('## Keys for each gate id are as follows:')
    for label in sorted(cat_dict, key=cat_dict.get):
        print('##   ', str(label))
    sorted_cats = sorted(cat_dict.items(), key=operator.itemgetter(1))

    cat_colors = dict(cat_colors_cfg)
    lab_colors = [cat_colors[kitty[0]] for kitty in sorted_cats]
    cmap = matplotlib.colors.ListedColormap(lab_colors)

    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(2, 2, figsize=figsize_panel)
    ax[0, 0].set_aspect('auto')
    display.plot_rhi('gate_id', sweep=sweep, ax=ax[0, 0],
                     cmap=cmap, vmin=0, vmax=6)

    cbax = ax[0, 0]
    if ('ground_clutter' in radar.fields.keys()
            or gate_id_has_category(gate_id_field, 'terrain_blockage')):
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
    display.plot_rhi('reflectivity', sweep=sweep,
                         vmin=_range('reflectivity_vmin', -8),
                         vmax=_range('reflectivity_vmax', 40.0),
                         ax=ax[0, 1],
                         cmap='HomeyerRainbow')
    ax[1, 0].set_aspect('auto')
    display.plot_rhi('velocity_texture', sweep=sweep,
                     vmin=_range('velocity_texture_vmin', 0),
                     vmax=_range('velocity_texture_vmax', 14),
                     ax=ax[1, 0],
                     title=_generate_title(
                         radar, 'velocity_texture', sweep),
                     cmap='Spectral_r')

    rhv_field = field_config['cross_correlation_ratio']
    ax[1, 1].set_aspect('auto')
    display.plot_rhi(rhv_field, sweep=sweep,
                     vmin=_range('cross_correlation_ratio_vmin', .5),
                     vmax=_range('cross_correlation_ratio_vmax', 1),
                     ax=ax[1, 1],
                     cmap='Carbone42')
    for i in range(2):
        for j in range(2):
            ax[i, j].set_ylim([ymin, ymax])
    fig.tight_layout()
    figures['cmac_four_panel_plot'] = fig

    # Creating a plot with reflectivity corrected with gate ids.
    cmac_gates = pyart.correct.GateFilter(radar)
    cmac_gates.exclude_all()
    cmac_gates.include_equal('gate_id', cat_dict['rain'])
    cmac_gates.include_equal('gate_id', cat_dict['melting'])
    cmac_gates.include_equal('gate_id', cat_dict['snow'])

    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=figsize_single)
    ax.set_aspect('auto')
    display.plot_rhi('reflectivity', sweep=sweep,
                     vmin=_range('reflectivity_vmin', -8),
                     vmax=_range('reflectivity_vmax', 40),
                     mask_outside=False,
                     cmap='HomeyerRainbow',
                     title=_generate_title(
                         radar, 'masked_corrected_reflectivity',
                         sweep), ax=ax,
                     gatefilter=cmac_gates)
    plt.ylim(ymin, ymax)
    figures['masked_corrected_reflectivity'] = fig


    # Creating a plot with reflectivity corrected with attenuation.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=figsize_single)
    ax.set_aspect('auto')
    display.plot_rhi('corrected_reflectivity', sweep=sweep,
                     vmin=_range('corrected_reflectivity_vmin', 0),
                     vmax=_range('corrected_reflectivity_vmax', 40.0),
                     title=_generate_title(
                         radar, 'corrected_reflectivity',
                         sweep),
                     cmap='HomeyerRainbow',
                     ax=ax)
    plt.ylim(ymin, ymax)
    figures['corrected_reflectivity'] = fig

    # Creating a plot with differential phase.
    phase_field = field_config['input_phidp_field']
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=figsize_single)
    ax.set_aspect('auto')
    display.plot_rhi(phase_field, sweep=sweep, ax=ax)
    plt.ylim(ymin, ymax)
    figures['differential_phase'] = fig


    # Creating a plot of specific attenuation.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=figsize_single)
    ax.set_aspect('auto')
    display.plot_rhi('specific_attenuation', sweep=sweep,
                     vmin=_range('specific_attenuation_vmin', 0),
                     vmax=_range('specific_attenuation_vmax', 1.0),
                     ax=ax)
    plt.ylim(ymin, ymax)
    figures['specific_attenuation'] = fig

    # Creating a plot of corrected differential phase.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=figsize_single)
    ax.set_aspect('auto')
    display.plot_rhi('corrected_differential_phase', sweep=sweep,
                         title=_generate_title(
                             radar, 'corrected_differential_phase',
                             sweep), ax=ax)
    plt.ylim(ymin, ymax)
    figures['corrected_differential_phase'] = fig

    # Creating a plot of corrected specific differential phase.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=figsize_single)
    ax.set_aspect('auto')
    display.plot_rhi('corrected_specific_diff_phase', sweep=sweep,
                     vmin=_range('corrected_specific_diff_phase_vmin', 0),
                     vmax=_range('corrected_specific_diff_phase_vmax', 6),
                     title=_generate_title(
                         radar, 'corrected_specific_diff_phase',
                         sweep), ax=ax)
    plt.ylim(ymin, ymax)
    figures['corrected_specific_diff_phase'] = fig

    # Creating a plot with region dealias corrected velocity.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=figsize_single)
    ax.set_aspect('auto')
    display.plot_rhi('corrected_velocity', sweep=sweep,
                     cmap='balance',
                     vmin=_range('corrected_velocity_vmin', -60),
                     vmax=_range('corrected_velocity_vmax', 60),
                     ax=ax)
    plt.ylim(ymin, ymax)
    figures['corrected_velocity'] = fig

    # Creating a plot of rain rate A
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=figsize_single)
    ax.set_aspect('auto')
    display.plot_rhi('rain_rate_A', sweep=sweep,
                     vmin=_range('rain_rate_vmin', 0),
                     vmax=_range('rain_rate_vmax', 120), ax=ax)
    plt.ylim(ymin, ymax)
    figures['rain_rate_A'] = fig

    # Creating a plot of filtered corrected differential phase.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=figsize_single)
    ax.set_aspect('auto')
    display.plot_rhi('filtered_corrected_differential_phase', sweep=sweep,
                     title=_generate_title(
                         radar, 'filtered_corrected_differential_phase',
                         sweep), ax=ax, cmap='Theodore16')
    plt.ylim(ymin, ymax)
    figures['filtered_corrected_differential_phase'] = fig

    # Creating a plot of filtered corrected specific differential phase.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=figsize_single)
    ax.set_aspect('auto')
    display.plot_rhi('filtered_corrected_specific_diff_phase', sweep=sweep,
                     title=_generate_title(
                         radar, 'filtered_corrected_specific_diff_phase',
                         sweep), ax=ax, cmap='Theodore16')
    plt.ylim(ymin, ymax)
    figures['filtered_corrected_specific_diff_phase'] = fig

    # Creating a plot of corrected differential phase.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=figsize_single)
    ax.set_aspect('auto')
    display.plot_rhi('specific_differential_attenuation', sweep=sweep,
                     title=_generate_title(
                         radar, 'specific_differential_attenuation',
                         sweep), ax=ax, gatefilter=cmac_gates)
    plt.ylim(ymin, ymax)
    figures['specific_differential_attenuation'] = fig

    # Creating a plot of corrected differential phase.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=figsize_single)
    ax.set_aspect('auto')
    display.plot_rhi('path_integrated_differential_attenuation',
                     sweep=sweep,
                     title=_generate_title(
                         radar, 'path_integrated_differential_attenuation',
                         sweep), ax=ax, gatefilter=cmac_gates)
    plt.ylim(ymin, ymax)
    figures['path_integrated_differential_attenuation'] = fig

    # Creating a plot of corrected differential phase.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=figsize_single)
    ax.set_aspect('auto')
    display.plot_rhi('corrected_differential_reflectivity', sweep=sweep,
                     title=_generate_title(
                         radar, 'corrected_differential_reflectivity',
                         sweep), ax=ax, gatefilter=cmac_gates)
    plt.ylim(ymin, ymax)
    figures['corrected_differential_reflectivity'] = fig

    # Creating a plot with reflectivity corrected with attenuation.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=figsize_single)
    ax.set_aspect('auto')
    display.plot_rhi('normalized_coherent_power', sweep=sweep,
                     title=_generate_title(
                         radar, 'normalized_coherent_power',
                         sweep), ax=ax)
    plt.ylim(ymin, ymax)
    figures['normalized_coherent_power'] = fig

    # Creating a plot with reflectivity corrected with attenuation.
    display = pyart.graph.RadarDisplay(radar)
    fig, ax = plt.subplots(1, 1, figsize=figsize_single)
    ax.set_aspect('auto')
    display.plot_rhi('signal_to_noise_ratio', sweep=sweep,
                     title=_generate_title(
                         radar, 'signal_to_noise_ratio',
                         sweep), ax=ax)
    plt.ylim(ymin, ymax)
    figures['signal_to_noise_ratio'] = fig

    if return_figs:
        return figures

    for name, fig in figures.items():
        fig.savefig(
            os.path.join(image_directory, name + combined_name + '.png'))
        plt.close(fig)


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
