""" Module that uses CMAC 2.0 to remove and correct second trip returns,
correct velocity and more. A new radar object is then created with all CMAC
2.0 products. """

import copy
import json
import sys

import xarray as xr
import numpy as np
import pyart
import netCDF4

from .cmac_processing import (
    do_my_fuzz, get_melt, get_texture, fix_phase_fields, gen_clutter_field_from_refl, beam_block,
    snow_rate)
from .config import get_cmac_values, get_field_names, get_metadata, get_zs_relationships

def cmac(radar, sonde, config, geotiff=None, flip_velocity=False,
         meta_append=None, verbose=True, snow_density=1):
    """
    Corrected Moments in Antenna Coordinates

    Parameters
    ----------
    radar : Radar
        Radar object to use in the CMAC calculation.
    sonde : xarray Dataset
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
    snow_density : float
        1 / Snow water equivalent ratio for snowfall rate

    Returns
    -------
    radar : Radar
        Radar object with new CMAC added fields.

    """
    # Retrieve values from the configuration file.
    cmac_config = get_cmac_values(config)
    field_config = get_field_names(config)
    meta_config = get_metadata(config)
    zs_relationship_dict = get_zs_relationships()
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
        new_clutter_field = gen_clutter_field_from_refl(
            radar, field_config['input_clutter_corrected_reflectivity'],
            field_config['reflectivity'],
            diff_dbz=cmac_config['gen_clutter_from_refl_diff'],
            max_h=cmac_config['gen_clutter_from_refl_alt'])
        radar.add_field(
            field_config['clutter'], new_clutter_field, replace_existing=True)
        radar.fields[field_config['clutter']]['units'] = '1'
        radar.fields[field_config['clutter']]['valid_max'] = 1
        radar.fields[field_config['clutter']]['valid_min'] = 0
    # ZDR offsets
    if 'zdr_offset' in cmac_config.keys():
        if 'offset_zdrs' in cmac_config.keys():
            for fld in cmac_config['offset_zdrs']:
                radar.fields[fld]['data'] += cmac_config['zdr_offset']
        else:
            radar.fields[
                field_config['input_zdr']]['data'] += cmac_config['zdr_offset']


    # flipping phidp
    if 'flip_phidp' not in cmac_config.keys():
        cmac_config['flip_phidp'] = False

    if cmac_config['flip_phidp']:
        # user specifies fields to flip
        if 'phidp_flipped' in cmac_config.keys():
            for fld in cmac_config['phidp_flipped']:
                radar.fields[fld]['data'] = radar.fields[fld]['data'] * -1.0
        else:  # just flip defined phidp field
            radar.fields[
                field_config['input_phidp_field']]['data'] = radar.fields[
                    field_config['input_phidp_field']]['data']*-1.0

    if flip_velocity:
        radar.fields[vel_field]['data'] = radar.fields[
            vel_field]['data'] * -1.0
    z_dict, temp_dict = pyart.retrieve.map_profile_to_gates(
        sonde.variables[temp_field][:], sonde.variables[alt_field][:], radar)

    if 'clutter_mask_z_for_texture' not in cmac_config.keys():
        cmac_config['clutter_mask_z_for_texture'] = False

    if cmac_config['clutter_mask_z_for_texture']:
        masked_vr = copy.deepcopy(radar.fields[vel_field])
        if 'ground_clutter' in radar.fields.keys():
            masked_vr['data'] = np.ma.masked_where(radar.fields['ground_clutter']['data'] == 1, masked_vr['data'])
            masked_vr['data'][radar.fields['ground_clutter']['data'] == 1] = np.nan
        radar.add_field('clutter_masked_velocity', masked_vr, replace_existing=True)

        texture = get_texture(radar, 'clutter_masked_velocity')
        texture['data'][np.isnan(texture['data'])] = 0.0
    else:
        texture = get_texture(radar, vel_field)
    
    if field_config['signal_to_noise_ratio'] is None:
        snr = pyart.retrieve.calculate_snr_from_reflectivity(radar)

    if not verbose:
        print('## Adding radar fields...')

    if verbose:
        print('##')
        print('## These radar fields are being added:')
    temp_dict['units'] = 'degC'
    z_dict['units'] = 'm'
    radar.add_field('sounding_temperature', temp_dict, replace_existing=True)
    radar.add_field('height', z_dict, replace_existing=True)
    if field_config['signal_to_noise_ratio'] is None:
        radar.add_field('signal_to_noise_ratio', snr, replace_existing=True)
    else:
        radar.fields['signal_to_noise_ratio'] = radar.fields.pop(field_config['signal_to_noise_ratio'])
        
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

    if 'ground_clutter' in radar.fields.keys():
        # Adding fifth gate id, clutter.
        clutter_data = radar.fields['ground_clutter']['data']
        gate_data = radar.fields['gate_id']['data'].copy()
        radar.fields['gate_id']['data'][clutter_data == 1] = 5
        notes = radar.fields['gate_id']['notes']
        radar.fields['gate_id']['notes'] = notes + ',5:clutter'
        radar.fields['gate_id']['valid_max'] = 5
        radar.fields['gate_id']['valid_max'] = 0
    
    if 'classification_mask' in radar.fields.keys():
        clutter_data = radar.fields['classification_mask']['data']
        gate_data = radar.fields['gate_id']['data'].copy()
        radar.fields['gate_id']['data'][clutter_data == 8] = 5
        radar.fields['gate_id']['data'][clutter_data == 16] = 5
        radar.fields['gate_id']['data'][clutter_data == 4] = 5
        radar.fields['gate_id']['data'][clutter_data == 1] = 0
        radar.fields['gate_id']['data'][clutter_data == 2] = 0
        radar.fields['gate_id']['data'][gate_data == 0] = 0
        notes = radar.fields['gate_id']['notes']
        radar.fields['gate_id']['notes'] = notes + ',5:clutter'
        radar.fields['gate_id']['valid_max'] = 5
        radar.fields['gate_id']['valid_max'] = 0

    if geotiff is not None:
        pbb_all, cbb_all = beam_block(
            radar, geotiff, cmac_config['radar_height_offset'],
            cmac_config['beam_width'])
        radar.fields['gate_id']['data'][cbb_all > 0.30] = 6
        notes = radar.fields['gate_id']['notes']
        radar.fields['gate_id']['notes'] = notes + ',6:terrain_blockage'
        radar.fields['gate_id']['valid_max'] = 6

        pbb_dict = pbb_to_dict(pbb_all)
        cbb_dict = cbb_to_dict(cbb_all)
        radar.add_field('partial_beam_blockage', pbb_dict)
        radar.add_field('cumulative_beam_blockage', cbb_dict)

    if 'cbb_flag' in radar.fields.keys():
        cbb = radar.fields['cbb_flag']['data']
        radar.fields['gate_id']['data'][cbb == 1] = 6
        notes = radar.fields['gate_id']['notes']
        radar.fields['gate_id']['notes'] = notes + ',6:terrain_blockage'
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
    u_wind = sonde[u_field].values
    v_wind = sonde[v_field].values
    alt_field = field_config['altitude']
    sonde_alt = sonde[alt_field].values
    profile = pyart.core.HorizontalWindProfile.from_u_and_v(
        sonde_alt, u_wind, v_wind)
    sim_vel = pyart.util.simulated_vel_from_profile(radar, profile)
    radar.add_field('simulated_velocity', sim_vel, replace_existing=True)

    # Create the corrected velocity field from the region dealias algorithm.
    speckled_cmac_gates = pyart.correct.despeckle_field(
        radar, vel_field, gatefilter=cmac_gates)
    corr_vel = pyart.correct.dealias_region_based(
        radar, vel_field=vel_field, ref_vel_field='simulated_velocity',
        keep_original=False, gatefilter=speckled_cmac_gates, centered=True)

    radar.add_field('corrected_velocity', corr_vel, replace_existing=True)
    if verbose:
        print('##    corrected_velocity')
        print('##    simulated_velocity')

    fzl = get_melt(radar)
    
    # Is the freezing level realistic? If not, assume
    
    ref_offset = cmac_config['ref_offset']
    self_const = cmac_config['self_const']
    # Calculating differential phase fields.
    radar.fields[field_config['input_phidp_field']]['data'][
        radar.fields[field_config['input_phidp_field']]['data'] < 0] += 360.0
    kdp_gates = copy.deepcopy(cmac_gates)
    kdp_gates.exclude_above('height', fzl)

    phidp, kdp = pyart.correct.phase_proc_lp_gf(
        radar, gatefilter=kdp_gates, offset=ref_offset, debug=True, LP_solver='cylp',
        nowrap=50, fzl=fzl, self_const=self_const, phidp_field=field_config['input_phidp_field'],
        refl_field=field_config['reflectivity'])
    print("Processed phase")
    # We do not use KDP, phase above freezing level
    kdp_gates = copy.deepcopy(cmac_gates)
    kdp_gates.exclude_above('height', fzl)
    phidp_filt, kdp_filt = fix_phase_fields(
        copy.deepcopy(kdp), copy.deepcopy(phidp), radar.range['data'],
        cmac_gates)

    radar.add_field('corrected_differential_phase', phidp,
                    replace_existing=True)
    radar.fields['corrected_differential_phase']['long_name'] = 'Corrected differential propagation phase shift'
    radar.add_field('filtered_corrected_differential_phase', phidp_filt,
                    replace_existing=True)
    radar.fields[
        'filtered_corrected_differential_phase']['long_name'] = 'Filtered corrected differential propagation phase shift'
    radar.add_field('corrected_specific_diff_phase', kdp,
                    replace_existing=True)
    radar.add_field('filtered_corrected_specific_diff_phase', kdp_filt,
                    replace_existing=True)
    radar.fields[
        'filtered_corrected_specific_diff_phase']['long_name'] = 'Filtered Corrected Specific differential phase (KDP)'
    radar.fields['filtered_corrected_differential_phase']['long_name'] = 'Filtered Corrected Differential Phase'
    if 'clutter_masked_velocity' in radar.fields.keys():
        radar.fields['clutter_masked_velocity']['long_name'] = 'Radial mean Doppler velocity, positive for motion away from the instrument, clutter removed'
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
    radar.fields['height_over_iso0']['long_name'] = 'Height of radar beam over freezing level'
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

    radar.fields['corrected_velocity']['units'] = 'm/s'
    if 'valid_min' not in radar.fields['corrected_velocity'].keys():
        radar.fields['corrected_velocity']['valid_min'] = -100.0

    if 'valid_max' not in radar.fields['corrected_velocity'].keys():
        radar.fields['corrected_velocity']['valid_max'] = 100.0

    radar.fields['corrected_velocity']['valid_min'] = np.round(
        radar.fields['corrected_velocity']['valid_min'], 4)
    radar.fields['corrected_velocity']['valid_max'] = np.round(
        radar.fields['corrected_velocity']['valid_max'], 4)
    radar.fields['simulated_velocity']['units'] = 'm/s'
    radar.fields['velocity_texture']['units'] = 'm/s'
    radar.fields['unfolded_differential_phase']['long_name'] = 'Unfolded differential propagation phase shift'
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

    mask = cmac_gates.gate_excluded

    rain_rate_comment = (
        'Rain rate calculated from specific_attenuation,'
        + ' R=%s*specific_attenuation**%s, note R=0.0 where' % (
            str(rr_a), str(rr_b))
        + ' norm coherent power < 0.4 or rhohv < 0.8')
    radar.fields['rain_rate_A'].update({
        'comment': rain_rate_comment})

    snow_gates = pyart.correct.GateFilter(radar)
    snow_gates.exclude_all()
    snow_gates.include_equal('gate_id', cat_dict['snow'])
    if verbose:
        print('## Rainfall rate as a function of A ##')

    
    for zs_key in zs_relationship_dict.keys():
        abbreviation = zs_relationship_dict[zs_key]["abbreviation"]
        A = zs_relationship_dict[zs_key]["A"]
        B = zs_relationship_dict[zs_key]["B"]
        radar = snow_rate(radar, 1 / snow_density, A, B, zs_key, abbreviation)
        radar.fields['snow_rate_%s' % abbreviation]['data'] = np.ma.masked_where(snow_gates.gate_excluded,
            radar.fields['snow_rate_%s' % abbreviation]['data'])


    # Calculating snowfall rate

    if verbose:
        print("## Snowfall rate from Z-S relationship")

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
            'site_id': None,
            'data_level': 'sgp',
            'comment': 'This is highly experimental and initial data. '
                       + 'There are many known and unknown issues. Please do '
                       + 'not use before contacting the Translator responsible '
                       + 'scollis@anl.gov',
            'attributions': 'This data is collected by the ARM Climate Research '
                            + 'facility. Radar system is operated by the radar '
                            + 'engineering team radar@arm.gov and the data is '
                            + 'processed by the precipitation radar products '
                            + 'team. LP code courtesy of Scott Giangrande, BNL.',
            'version': '2.0 lite',
            'vap_name': 'cmac',
            'known_issues': 'False phidp jumps in insect regions. Still uses '
                            + 'old Giangrande code.',
            'developers': 'Robert Jackson, ANL. Zachary Sherman, ANL.',
            'translator': 'Scott Collis, ANL.',
            'mentors': 'Bradley Isom, PNNL., Iosif Lindenmaier, PNNL.',
            'Conventions': 'CF/Radial instrument_parameters ARM-1.3'}
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


def pbb_to_dict(pbb_all):
    """ Function that takes the pbb_all array and turns
    it into a dictionary to be used and added to the
    pyart radar object. """
    pbb_dict = {}
    pbb_dict['coordinates'] = 'elevation azimuth range'
    pbb_dict['units'] = '1'
    pbb_dict['data'] = pbb_all
    pbb_dict['standard_name'] = 'partial_beam_block'
    pbb_dict['long_name'] = 'Partial Beam Block Fraction'
    pbb_dict['comment'] = 'Partial beam block fraction due to terrain.'
    return pbb_dict


def cbb_to_dict(cbb_all):
    """ Function that takes the cbb_all array and turns
    it into a dictionary to be used and added to the
    pyart radar object. """
    cbb_dict = {}
    cbb_dict['coordinates'] = 'elevation azimuth range'
    cbb_dict['units'] = '1'
    cbb_dict['data'] = cbb_all
    cbb_dict['standard_name'] = 'cumulative_beam_block'
    cbb_dict['long_name'] = 'Cumulative Beam Block Fraction'
    cbb_dict['comment'] = 'Cumulative beam block fraction due to terrain.'
    return cbb_dict
