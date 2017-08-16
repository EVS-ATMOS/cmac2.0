""" 
Code that uses CMAC to remove and correct second trip returns, correct velocity,
produce a quasi-vertical profile, and more. """


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
    print('##', str(radar_start_date))
    # ymd_string = datetime.strftime(radar_start_date, '%Y%m%d')
    # hms_string = datetime.strftime(radar_start_date, '%H%M%S')
    # print('##', ymd_string, hms_string)

    z_dict, temp_dict = pyart.retrieve.map_profile_to_gates(
        sonde.variables['tdry'][:], sonde.variables['alt'][:], radar)
    texture = processing_code.get_texture(radar)

    snr = pyart.retrieve.calculate_snr_from_reflectivity(radar)
    print('##')
    print('## These radar fields are being added:')
    radar.add_field('sounding_temperature', temp_dict, replace_existing=True)
    print('##    sounding_temperature')
    radar.add_field('height', z_dict, replace_existing=True)
    print('##    height')
    radar.add_field('SNR', snr, replace_existing=True)
    print('##    SNR')
    radar.add_field('velocity_texture', texture, replace_existing=True)
    print('##    velocity_texture')

    print('##    gate_id')
    my_fuzz, cats = processing_code.do_my_fuzz(radar, **kwargs)
    radar.add_field('gate_id', my_fuzz,
                    replace_existing=True)
    cat_dict = {}
    for pair_str in radar.fields['gate_id']['notes'].split(','):
        cat_dict.update(
            {pair_str.split(':')[1]:int(pair_str.split(':')[0])})
    
    print('##    corrected_velocity')
    cmac_gates = pyart.correct.GateFilter(radar)
    cmac_gates.exclude_all()
    cmac_gates.include_equal('gate_id', cat_dict['rain'])
    cmac_gates.include_equal('gate_id', cat_dict['melting'])
    cmac_gates.include_equal('gate_id', cat_dict['snow'])
    corr_vel = pyart.correct.dealias_region_based(
        radar, vel_field='velocity', keep_original=False, 
        gatefilter=cmac_gates, centered=True)
    radar.add_field('corrected_velocity', corr_vel, replace_existing=True)

    print('##    corrected_differential_phase')
    phidp, kdp = pyart.correct.phase_proc_lp(radar, 0.0, debug=True)
    radar.add_field('corrected_differential_phase', phidp)
    print('##    corrected_specific_diff_phase')
    radar.add_field('corrected_specific_diff_phase', kdp)

    print('##    specific_attenuation')
    spec_at, cor_z_atten = pyart.correct.calculate_attenuation(
        radar, 0, refl_field='reflectivity',
        ncp_field='normalized_coherent_power',
        rhv_field='cross_correlation_ratio',
        phidp_field='corrected_differential_phase')
    radar.add_field('specific_attenuation', spec_at)
    print('##    corrected_reflectivity_attenuation')
    radar.add_field('corrected_reflectivity_attenuation', cor_z_atten)

    print('##')
    print('## All CMAC fields have been added to the radar object.')
    print('##')

    print('## A quasi-vertical profile is being created.')
    qvp = processing_code.retrieve_qvp(radar, radar.fields['height']['data'])
    radar.qvp = qvp
    print('## The quasi-vertical profile has been created and',
          'can be accessed with radar.qvp')
    return radar
