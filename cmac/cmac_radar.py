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
    do_my_fuzz, get_melt, get_texture, fix_phase_fields, gen_clutter_field_from_refl, beam_block)
from .config import get_cmac_values, get_field_names, get_metadata

def cmac(radar, sonde, config, geotiff=None, flip_velocity=False,
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
    geotiff : str
        Filepath for a geotiff, if provided, will generate a beam blockage
        gate id.
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

    # Over write site altitude

    if 'site_alt' in cmac_config.keys():
        radar.altitude['data'][0] = cmac_config['site_alt']

    # Obtaining variables needed for fuzzy logic.

    radar_start_date = netCDF4.num2date(
        radar.time['data'][0], radar.time['units'],
        only_use_cftime_datetimes=False, only_use_python_datetimes=True)
    print('##', str(radar_start_date))

    temp_field = field_config['temperature']
    alt_field = field_config['altitude']
    vel_field = field_config['velocity']

    if 'gen_clutter_from_refl' not in cmac_config.keys():
        cmac_config['gen_clutter_from_refl'] = False

    if cmac_config['gen_clutter_from_refl']:
        new_clutter_field = gen_clutter_field_from_refl(radar, field_config['input_clutter_corrected_reflectivity'],
                                                        field_config['reflectivity'],
                                                        diff_dbz=cmac_config['gen_clutter_from_refl_diff'],
                                                        max_h=cmac_config['gen_clutter_from_refl_alt'])
        radar.add_field(field_config['clutter'], new_clutter_field, replace_existing=True)

    # ZDR offsets

    if 'zdr_offset' in cmac_config.keys():
        if 'offset_zdrs' in cmac_config.keys():
            for fld in cmac_config['offset_zdrs']:
                radar.fields[fld]['data'] += cmac_config['zdr_offset']
        else:
            radar.fields[field_config['input_zdr']]['data'] += cmac_config['zdr_offset']


    # flipping phidp
    if 'flip_phidp' not in cmac_config.keys():
        cmac_config['flip_phidp'] = False

    if cmac_config['flip_phidp']:
        if 'phidp_flipped' in cmac_config.keys(): # user specifies fields to flip
            for fld in cmac_config['phidp_flipped']:
                radar.fields[fld]['data'] = radar.fields[fld]['data'] * -1.0
        else:  # just flip defined phidp field
            radar.fields[field_config['input_phidp_field']]['data'] = radar.fields[field_config['input_phidp_field']]['data']*-1.0

    if flip_velocity:
        radar.fields[vel_field]['data'] = radar.fields[
            vel_field]['data'] * -1.0
    z_dict, temp_dict = pyart.retrieve.map_profile_to_gates(
        sonde.variables[temp_field][:], sonde.variables[alt_field][:], radar)

    if 'clutter_mask_z_for_texture' not in cmac_config.keys():
        cmac_config['clutter_mask_z_for_texture'] = False

    if cmac_config['clutter_mask_z_for_texture']:
        masked_vr = copy.deepcopy(radar.fields[vel_field])
        masked_vr['data'] = np.ma.masked_where(radar.fields['ground_clutter']['data'] == 1, masked_vr['data'])
        masked_vr['data'][radar.fields['ground_clutter']['data'] == 1] = np.nan
        radar.add_field('clutter_masked_velocity', masked_vr, replace_existing=True)

        texture = get_texture(radar, 'clutter_masked_velocity')
        texture['data'][np.isnan(texture['data'])] = 0.0
    else:
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

    if 'mbfs' not in cmac_config:
        cmac_config['mbfs'] = None

    if 'hard_const' not in cmac_config:
        cmac_config['hard_const'] = None

    # Specifically for dealing with the ingested C-SAPR2 data

    my_fuzz, _ = do_my_fuzz(radar, rhv_field, ncp_field, verbose=verbose,
                            custom_mbfs=cmac_config['mbfs'],
                            custom_hard_constraints=cmac_config['hard_const'])

    radar.add_field('gate_id', my_fuzz,
                    replace_existing=True)

    if 'ground_clutter' or 'clutter' in radar.fields.keys():
        # Adding fifth gate id, clutter.
        clutter_data = radar.fields['ground_clutter']['data']
        gate_data = radar.fields['gate_id']['data']
        radar.fields['gate_id']['data'][clutter_data == 1] = 5
        notes = radar.fields['gate_id']['notes']
        radar.fields['gate_id']['notes'] = notes + ',5:clutter'
        radar.fields['gate_id']['valid_max'] = 5

    if geotiff is not None:
        pbb_all, cbb_all = beam_block(
            radar, geotiff, cmac_config['radar_height_offset'],
            cmac_config['beam_width'])
        radar.fields['gate_id']['data'][cbb_all > 0.70] = 6
        notes = radar.fields['gate_id']['notes']
        radar.fields['gate_id']['notes'] = notes + ',6:beam_block'
        radar.fields['gate_id']['valid_max'] = 6
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
    
    # Is the freezing level realistic? If not, assume
    ref_offset = cmac_config['ref_offset']
    self_const = cmac_config['self_const']
    # Calculating differential phase fields.

    radar.fields['differential_phase']['data'][
        radar.fields['differential_phase']['data']<0] += 360.0
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
    rr_a = cmac_config['rain_rate_a_coef']
    rr_b = cmac_config['rain_rate_b_coef']
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
    phidp_field = field_config['phidp_field']
    
    (spec_at, pia_dict, cor_z, spec_diff_at,
     pida_dict, cor_zdr) = pyart.correct.calculate_attenuation_zphi(
         radar, temp_field='sounding_temperature',
         iso0_field='height_over_iso0',
         zdr_field=field_config['zdr_field'],
         pia_field=field_config['pia_field'],
         phidp_field=field_config['phidp_field'],
         refl_field=field_config['refl_field'], c=c_coef, d=d_coef,
         a_coef=attenuation_a_coef, beta=beta_coef,
         gatefilter=cmac_gates)

    #  cor_zdr['data'] += cmac_config['zdr_offset'] Now taken care of at start
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
    
    # Calculating rain rate.
    R = rr_a * (radar.fields['specific_attenuation']['data']) ** rr_b
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


def area_coverage(radar, precip_threshold=10.0, convection_threshold=40.0):
    """ Returns percent coverage of precipitation and convection. """
    temp_radar = radar.extract_sweeps([0])
    ref = temp_radar.fields['corrected_reflectivity']['data']
    total_len = len(ref.flatten())
    ref_10_len = len(np.argwhere(ref >= precip_threshold))
    ref_40_len = len(np.argwhere(ref >= convection_threshold))
    ref_10_per = (ref_10_len/total_len)*100
    ref_40_per = (ref_40_len/total_len)*100
    del temp_radar
    return ref_10_per, ref_40_per
