""" Module that uses CMAC 2.0 to remove and correct second trip returns,
correct velocity and more. A new radar object is then created with all CMAC
2.0 products. """

import copy
import json
import sys

import netCDF4
import numpy as np
import pyart

from .cmac_processing import (
    do_my_fuzz, get_melt, get_texture, fix_phase_fields)
from .config import get_cmac_values, get_field_names, get_metadata

def cmac(radar, sonde, config, flip_velocity=False,
         meta_append=None, verbose=True):
    """
    Corrected Moments in Antenna Coordinates

    Parameters
    ----------
    radar : Radar
        Radar object to use in the CMAC calculation.
    sonde : Object
        Object containing all the sonde data.
    config : str
        A string pointing to dictionaries containing values for CMAC 2.0
        specific to a radar.

    Other Parameters
    ----------------
    meta_append : dict, json and None
        Value key pairs to attend to global attributes. If None,
        a default metadata will be created. The metadata can also
        be created by providing a dictionary or a json file.
    verbose : bool
        If True, this will display more statistics.

    Returns
    -------
    radar : Radar
        Radar object with new CMAC added fields.

    """
    # Retrieve values from the configuration file.
    cmac_config = get_cmac_values(config)
    field_config = get_field_names(config)
    meta_config = get_metadata(config)

    # Obtaining variables needed for fuzzy logic.
    radar.altitude['data'][0] = cmac_config['site_alt']

    radar_start_date = netCDF4.num2date(
        radar.time['data'][0], radar.time['units'])
    print('##', str(radar_start_date))

    temp_field = field_config['temperature']
    alt_field = field_config['altitude']
    vel_field = field_config['velocity']

    if flip_velocity:
        radar.fields[vel_field]['data'] = radar.fields[
            vel_field]['data'] * -1.0
    z_dict, temp_dict = pyart.retrieve.map_profile_to_gates(
        sonde.variables[temp_field][:], sonde.variables[alt_field][:], radar)
    texture = get_texture(radar, vel_field)

    snr = pyart.retrieve.calculate_snr_from_reflectivity(radar)

    if not verbose:
        print('## Adding radar fields...')

    if verbose:
        print('##')
        print('## These radar fields are being added:')

    radar.add_field('sounding_temperature', temp_dict, replace_existing=True)
    radar.add_field('height', z_dict, replace_existing=True)
    radar.add_field('signal_to_noise_ratio', snr, replace_existing=True)
    radar.add_field('velocity_texture', texture, replace_existing=True)
    if verbose:
        print('##    sounding_temperature')
        print('##    height')
        print('##    signal_to_noise_ratio')
        print('##    velocity_texture')

    # Performing fuzzy logic to obtain the gate ids.
    rhv_field = field_config['cross_correlation_ratio']
    ncp_field = field_config['normalized_coherent_power']
    my_fuzz, _ = do_my_fuzz(radar, rhv_field, ncp_field, tex_start=2.4,
                            tex_end=2.7, verbose=verbose)
    radar.add_field('gate_id', my_fuzz,
                    replace_existing=True)

    if 'xsapr_clutter' in radar.fields.keys():
        # Adding fifth gate id, clutter.
        clutter_data = radar.fields['xsapr_clutter']['data']
        gate_data = radar.fields['gate_id']['data']
        clutter_data[gate_data == 0] = 0
        clutter_data[gate_data == 3] = 0
        radar.fields['gate_id']['data'][clutter_data == 1] = 5
        notes = radar.fields['gate_id']['notes']
        radar.fields['gate_id']['notes'] = notes + ',5:clutter'
        radar.fields['gate_id']['valid_max'] = 5
    cat_dict = {}
    for pair_str in radar.fields['gate_id']['notes'].split(','):
        cat_dict.update(
            {pair_str.split(':')[1]:int(pair_str.split(':')[0])})

    if verbose:
        print('##    gate_id')

    # Corrected velocity using pyart's region dealiaser.
    cmac_gates = pyart.correct.GateFilter(radar)
    cmac_gates.exclude_all()
    cmac_gates.include_equal('gate_id', cat_dict['rain'])
    cmac_gates.include_equal('gate_id', cat_dict['melting'])
    cmac_gates.include_equal('gate_id', cat_dict['snow'])

    # Create a simulated velocity field from the sonde object.
    u_field = field_config['u_wind']
    v_field = field_config['v_wind']
    u_wind = sonde.variables[u_field][:]
    v_wind = sonde.variables[v_field][:]
    alt_field = field_config['altitude']
    sonde_alt = sonde.variables[alt_field][:]
    profile = pyart.core.HorizontalWindProfile.from_u_and_v(
        sonde_alt, u_wind, v_wind)
    sim_vel = pyart.util.simulated_vel_from_profile(radar, profile)
    radar.add_field('simulated_velocity', sim_vel, replace_existing=True)

    # Create the corrected velocity field from the region dealias algorithm.
    corr_vel = pyart.correct.dealias_region_based(
        radar, vel_field=vel_field, ref_vel_field='simulated_velocity',
        keep_original=False, gatefilter=cmac_gates, centered=True)

    radar.add_field('corrected_velocity', corr_vel, replace_existing=True)
    if verbose:
        print('##    corrected_velocity')
        print('##    simulated_velocity')

    fzl = get_melt(radar)

    ref_offset = cmac_config['ref_offset']
    self_const = cmac_config['self_const']
    # Calculating differential phase fields.
    phidp, kdp = pyart.correct.phase_proc_lp_gf(
        radar, gatefilter=cmac_gates, offset=ref_offset, debug=True,
        nowrap=50, fzl=fzl, self_const=self_const)
    phidp_filt, kdp_filt = fix_phase_fields(
        copy.deepcopy(kdp), copy.deepcopy(phidp), radar.range['data'],
        cmac_gates)

    radar.add_field('corrected_differential_phase', phidp,
                    replace_existing=True)
    radar.add_field('filtered_corrected_differential_phase', phidp_filt,
                    replace_existing=True)
    radar.add_field('corrected_specific_diff_phase', kdp,
                    replace_existing=True)
    radar.add_field('filtered_corrected_specific_diff_phase', kdp_filt,
                    replace_existing=True)
    if verbose:
        print('##    corrected_specific_diff_phase')
        print('##    filtered_corrected_specific_diff_phase')
        print('##    corrected_differential_phase')
        print('##    filtered_corrected_differential_phase')

    # Calculating attenuation by using pyart.
    refl_field = field_config['reflectivity']
    attenuation_a_coef = cmac_config['attenuation_a_coef']
    c_coef = cmac_config['c_coef']
    d_coef = cmac_config['d_coef']
    beta_coef = cmac_config['beta_coef']
    zdr_field = field_config['differential_reflectivity']

    radar.fields['corrected_differential_reflectivity'] = copy.deepcopy(
        radar.fields[zdr_field])
    radar.fields['corrected_reflectivity'] = copy.deepcopy(
        radar.fields[refl_field])
    radar.fields['corrected_reflectivity']['data'] = np.ma.masked_where(
        cmac_gates.gate_excluded,
        radar.fields['corrected_reflectivity']['data'])

    # Get specific differential attenuation.
    # Need height over 0C isobar.
    iso0 = np.ma.mean(radar.fields['height']['data'][
        np.where(np.abs(radar.fields['sounding_temperature']['data']) < 0.1)])
    radar.fields['height_over_iso0'] = copy.deepcopy(radar.fields['height'])
    radar.fields['height_over_iso0']['data'] -= iso0

    (spec_at, pia_dict, cor_z, spec_diff_at,
     pida_dict, cor_zdr) = pyart.correct.calculate_attenuation_zphi(
         radar, temp_field='sounding_temperature',
         iso0_field='height_over_iso0',
         zdr_field='corrected_differential_reflectivity',
         pia_field='path_integrated_attenuation',
         refl_field='corrected_reflectivity', c=c_coef, d=d_coef,
         a_coef=attenuation_a_coef, beta=beta_coef)
    cor_zdr['data'] += cmac_config['zdr_offset']
    radar.add_field('specific_attenuation', spec_at, replace_existing=True)
    radar.add_field('path_integrated_attenuation', pia_dict,
                    replace_existing=True)
    radar.add_field('corrected_reflectivity', cor_z, replace_existing=True)
    radar.add_field('specific_differential_attenuation', spec_diff_at,
                    replace_existing=True)
    radar.add_field('path_integrated_differential_attenuation', pida_dict,
                    replace_existing=True)
    radar.add_field('corrected_differential_reflectivity', cor_zdr,
                    replace_existing=True)

    cat_dict = {}
    for pair_str in radar.fields['gate_id']['notes'].split(','):
        if verbose:
            print(pair_str)
        cat_dict.update({pair_str.split(':')[1]: int(pair_str.split(':')[0])})

    rain_gates = pyart.correct.GateFilter(radar)
    rain_gates.exclude_all()
    rain_gates.include_equal('gate_id', cat_dict['rain'])
    spec_at['data'][rain_gates.gate_excluded] = 0.0

    # Calculating rain rate.
    R = 51.3 * (radar.fields['specific_attenuation']['data']) ** 0.81
    rainrate = copy.deepcopy(radar.fields['specific_attenuation'])
    rainrate['data'] = R
    rainrate['valid_min'] = 0.0
    rainrate['valid_max'] = 400.0
    rainrate['standard_name'] = 'rainfall_rate'
    rainrate['long_name'] = 'rainfall_rate'
    rainrate['least_significant_digit'] = 1
    rainrate['units'] = 'mm/hr'
    radar.fields.update({'rain_rate_A': rainrate})

    # This needs to be updated to a gatefilter.
    mask = radar.fields['reflectivity']['data'].mask

    radar.fields['rain_rate_A']['data'][np.where(mask)] = 0.0
    radar.fields['rain_rate_A'].update({
        'comment': ('Rain rate calculated from specific_attenuation,',
                    ' R=51.3*specific_attenuation**0.81, note R=0.0 where',
                    ' norm coherent power < 0.4 or rhohv < 0.8')})

    if verbose:
        print('## Rainfall rate as a function of A ##')

    print('##')
    print('## All CMAC fields have been added to the radar object.')
    print('##')

    # Adding the metadata to the cmac radar object.
    print('## Appending metadata')
    command_line = ''
    for item in sys.argv:
        command_line = command_line + ' ' + item
    if meta_append is None:
        meta = {
            'site_id': 'sgp',
            'data_level': 'c1',
            'comment': (
                'This is highly experimental and initial data. There are many',
                'known and unknown issues. Please do not use before',
                'contacting the Translator responsible scollis@anl.gov'),
            'attributions': (
                'This data is collected by the ARM Climate Research facility.',
                'Radar system is operated by the radar engineering team',
                'radar@arm.gov and the data is processed by the precipitation',
                'radar products team. LP code courtesy of Scott Giangrande',
                'BNL.'),
            'version': '2.0 lite',
            'vap_name': 'cmac',
            'known_issues': (
                'False phidp jumps in insect regions. Still uses old',
                'Giangrande code.'),
            'developers': 'Robert Jackson, ANL. Zachary Sherman, ANL.',
            'translator': 'Scott Collis, ANL.',
            'mentors': ('Nitin Bharadwaj, PNNL. Bradley Isom, PNNL.',
                        'Joseph Hardin, PNNL. Iosif Lindenmaier, PNNL.')}
    else:
        if meta_append.lower().endswith('.json'):
            with open(meta_append, 'r') as infile:
                meta = json.load(infile)
        elif meta_append == 'config':
            meta = meta_config
        else:
            raise RuntimeError('Must provide the file name of the json file',
                               'or say config to use the meta data from',
                               'config.py')

    radar.metadata.clear()
    radar.metadata.update(meta)
    radar.metadata['command_line'] = command_line
    return radar
