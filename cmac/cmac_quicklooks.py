import os
import operator

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pyart


def quicklooks(radar, image_directory=None, sweep=3,
               max_lat=37.0, min_lat=36.0, max_lon=-97.0, min_lon=-98.3):
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

    """

    if image_directory is None:
        image_directory = os.path.expanduser('~')

    # Plot of reflectivity before CMAC.
    lal = np.arange(min_lat, max_lat, .2)
    lol = np.arange(min_lon, max_lon, .2)

    display = pyart.graph.RadarMapDisplay(radar)
    fig = plt.figure(figsize=[10, 8])
    display.plot_ppi_map('reflectivity', sweep=sweep, resolution='c',
                         vmin=-8, vmax=64, mask_outside=False,
                         cmap=pyart.graph.cm.NWSRef,
                         min_lat=min_lat, min_lon=min_lon,
                         max_lat=max_lat, max_lon=max_lon,
                         lat_lines=lal, lon_lines=lol)
    plt.savefig(image_directory + '/cmac_uncorrected_reflectivity.png')

    # Four panel plot of gate_id, velocity_texture, reflectivity, and
    # cross_correlation_ratio.
    cat_dict = {}
    print('##')
    print('## Keys for each gate id are as follows:')
    for pair_str in radar.fields['gate_id']['notes'].split(','):
        print('##    ' + str(pair_str))
        cat_dict.update({pair_str.split(':')[1]:int(pair_str.split(':')[0])})
    sorted_cats = sorted(cat_dict.items(), key=operator.itemgetter(1))
    lab_colors=['green', 'cyan', 'blue', 'red', 'grey']
    cmap = matplotlib.colors.ListedColormap(lab_colors)

    display = pyart.graph.RadarMapDisplay(radar)
    fig = plt.figure(figsize=[15, 10])
    plt.subplot(2, 2, 1) 
    display.plot_ppi_map('gate_id', sweep=sweep, min_lon=min_lon,
                         max_lon=max_lon, min_lat=min_lat,
                         max_lat=max_lat, resolution='l', cmap=cmap,
                         vmin=0, vmax=5)
    cbax = plt.gca()
    # labels = [item.get_text() for item in cbax.get_xticklabels()]
    # my_display.cbs[-1].ax.set_yticklabels(cats)
    tick_locs = np.linspace(0, len(sorted_cats) - 1, len(sorted_cats)) + 0.5
    display.cbs[-1].locator = matplotlib.ticker.FixedLocator(tick_locs)
    catty_list = [sorted_cats[i][0] for i in range(len(sorted_cats))]
    display.cbs[-1].formatter = matplotlib.ticker.FixedFormatter(catty_list)
    display.cbs[-1].update_ticks()
    plt.subplot(2, 2, 2) 
    display.plot_ppi_map('reflectivity', sweep=sweep, vmin=-8, vmax=64,
                         min_lon=min_lon, max_lon=max_lon, min_lat=min_lat, max_lat=max_lat,
                         resolution='l', cmap=pyart.graph.cm.NWSRef)

    plt.subplot(2, 2, 3) 
    display.plot_ppi_map('velocity_texture', sweep=sweep, vmin=0, vmax=14, 
                         min_lon=min_lon, max_lon=max_lon, min_lat=min_lat, max_lat=max_lat,
                         resolution='l', cmap=pyart.graph.cm.NWSRef)
    plt.subplot(2, 2, 4) 
    display.plot_ppi_map('cross_correlation_ratio', sweep=sweep, vmin=.5,
                         vmax=1, min_lon=min_lon, max_lon=max_lon,
                         min_lat=min_lat, max_lat=max_lat, resolution='l',
                         cmap=pyart.graph.cm.Carbone42)
    plt.savefig(image_directory + '/cmac_four_panel_plot.png')

    # Plot of reflectivity with applied gates.
    cmac_gates = pyart.correct.GateFilter(radar)
    cmac_gates.exclude_all()
    cmac_gates.include_equal('gate_id', cat_dict['rain'])
    cmac_gates.include_equal('gate_id', cat_dict['melting'])
    cmac_gates.include_equal('gate_id', cat_dict['snow'])

    display = pyart.graph.RadarMapDisplay(radar)
    fig = plt.figure(figsize=[10, 8])
    display.plot_ppi_map('reflectivity', sweep=sweep, resolution='c',
                         vmin=-8, vmax=64, mask_outside=False,
                         cmap=pyart.graph.cm.NWSRef,
                         min_lat=min_lat, min_lon=min_lon,
                         max_lat=max_lat, max_lon=max_lon,
                         lat_lines=lal, lon_lines=lol,
                         gatefilter=cmac_gates)
    plt.savefig(image_directory + '/cmac_corrected_reflectivity.png')