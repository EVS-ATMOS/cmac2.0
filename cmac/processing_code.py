"""
cmac.processing_code
======================
Common core processing code across the AGU poster.

.. autosummary::
    :toctree: generated/

"""

""" This code was written by Scott Collis. I did some pep8 changes,
name changes and updated the velocity texture function."""


import copy
import os
import time
import datetime
import fnmatch
import netCDF4
import numpy as np
import pyart
import skfuzzy as fuzz
from scipy import integrate

from csu_radartools import csu_kdp
from scipy import ndimage, interpolate


def snr_and_sounding(radar, soundings_dir, override_file=None):
    if override_file is None:
        radar_start_date = netCDF4.num2date(radar.time['data'][0],
                                            radar.time['units'])
        sonde_pattern = datetime.datetime.strftime(
            radar_start_date, 'sgpgriddedsondeC1.c0.%Y%m%d.*')
        all_sonde_files = os.listdir(soundings_dir)
        sonde_name = fnmatch.filter(all_sonde_files, sonde_pattern)[0]
        print(sonde_pattern, sonde_name)
        interp_sonde = netCDF4.Dataset(os.path.join(soundings_dir, sonde_name))
    else:
        sonde_name = override_file
        interp_sonde = netCDF4.Dataset(sonde_name)

    temperatures = interp_sonde.variables['temp'][:]
    times = interp_sonde.variables['time'][:]
    heights = interp_sonde.variables['height'][:]
    my_profile = pyart.retrieve.fetch_radar_time_profile(interp_sonde, radar)
    print(my_profile['temp'].shape)
    print(my_profile['height'])
    info_dict = {'long_name': 'Sounding temperature at gate',
                 'standard_name': 'temperature',
                 'valid_min': -100,
                 'valid_max': 100,
                 'units': 'degrees Celsius'}
    z_dict, temp_dict = pyart.retrieve.map_profile_to_gates(
        my_profile['temp'], my_profile['height'] * 1000.0, radar)
    snr = pyart.retrieve.calculate_snr_from_reflectivity(radar)
    return z_dict, temp_dict, snr


def get_texture(radar, nyq=None):
    """ Calculates velocity texture field. """
    if nyq is None:
        nyq = radar.instrument_parameters['nyquist_velocity']['data'][0]
    else:
        nyq = nyq
    start_time = time.time()
    std_dev = pyart.util.angular_texture_2d(radar.fields['velocity']['data'],
                                            4, nyq)
    filtered_data = ndimage.filters.median_filter(std_dev, size=(4, 4))
    texture_field = pyart.config.get_metadata('velocity')
    texture_field['data'] = filtered_data
    total_time = time.time() - start_time
    return texture_field


# Moment : [[start_up, finish_up, start_down, finish_down], weight]
def cum_score_fuzzy_logic(radar, mbfs=None,
                          debug=False, ret_scores=False,
                          hard_const=None):
    if mbfs is None:
        second_trip = {'velocity_texture': [[0, 0, 1.8, 2], 1.0],
                       'cross_correlation_ratio': [[.5, .7, 1, 1], 0.0],
                       'normalized_coherent_power': [[0, 0, .5, .6], 3.0],
                       'height': [[0, 0, 5000, 8000], 1.0],
                       'sounding_temperature': [[-100, -100, 100, 100], 0.0],
                       'SNR': [[15, 20, 1000, 1000], 1.0]}

        rain = {'differential_phase_texture': [[0, 0, 80, 90], 1.0],
                'cross_correlation_ratio': [[0.94, 0.96, 1, 1], 1.0],
                'normalized_coherent_power': [[0.4, 0.5, 1, 1], 1.0],
                'height': [[0, 0, 5000, 6000], 0.0],
                'sounding_temperature': [[0, 3, 100, 100], 2.0],
                'SNR': [[8, 10, 1000, 1000], 1.0]}

        snow = {'differential_phase_texture': [[0, 0, 80, 90], 1.0],
                'cross_correlation_ratio': [[0.85, 0.9, 1, 1], 1.0],
                'normalized_coherent_power': [[0.4, 0.5, 1, 1], 1.0],
                'height': [[0, 0, 25000, 25000], 0.0],
                'sounding_temperature': [[-100, -100, 0, 1.], 2.0],
                'SNR': [[8, 10, 1000, 1000], 1.0]}

        no_scatter = {'differential_phase_texture': [[90, 90, 400, 400], 0.0],
                      'cross_correlation_ratio': [[0, 0, 0.1, 0.2], 0.0],
                      'normalized_coherent_power': [[0, 0, 0.1, 0.2], 0.0],
                      'height': [[0, 0, 25000, 25000], 0.0],
                      'sounding_temperature': [[-100, -100, 100, 100], 0.0],
                      'SNR': [[-100, -100, 8, 10], 6.0]}

        melting = {'differential_phase_texture': [[20, 30, 80, 90], 0.0],
                   'cross_correlation_ratio': [[0.6, 0.7, .94, .96], 4.],
                   'normalized_coherent_power': [[0.4, 0.5, 1, 1], 0],
                   'height': [[0, 0, 25000, 25000], 0.0],
                   'sounding_temperature': [[-1., 0, 3.5, 5], 2.],
                   'SNR': [[8, 10, 1000, 1000], 0.0]}

        mbfs = {'multi_trip': second_trip, 'rain': rain, 'snow': snow,
                'no_scatter': no_scatter, 'melting': melting}

    flds = radar.fields
    scores = {}
    for key in mbfs.keys():
        if debug:
            print('##    Doing', key)
        this_score = np.zeros(
            flds[list(flds.keys())[0]]['data'].shape).flatten() * 0.0
        for MBF in mbfs[key].keys():
            this_score = fuzz.trapmf(
                flds[MBF]['data'].flatten(),
                mbfs[key][MBF][0]) * mbfs[key][MBF][1] + this_score

        this_score = this_score.reshape(
            flds[list(flds.keys())[0]]['data'].shape)
        scores.update({key: ndimage.filters.median_filter(
            this_score, size=[3, 4])})

    if hard_const is not None:
        # hard_const = [[class, field, (v1, v2)], ...]
        for this_const in hard_const:
            if debug:
                print('##    Doing hard constraining', this_const[0])
            key = this_const[0]
            const = this_const[1]
            fld_data = radar.fields[const]['data']
            lower = this_const[2][0]
            upper = this_const[2][1]
            const_area = np.where(np.logical_and(fld_data >= lower,
                                                 fld_data <= upper))
            if debug:
                print('##    ', str(const_area))
            scores[key][const_area] = 0.0
    stacked_scores = np.dstack([scores[key] for key in scores.keys()])
    #sum_of_scores = stacked_scores.sum(axis = 2)
    #print(sum_of_scores.shape)
    #norm_stacked_scores = stacked_scores
    max_score = stacked_scores.argmax(axis=2)

    gid = {}
    gid['data'] = max_score
    gid['units'] = ''
    gid['standard_name'] = 'gate_id'
    strgs = ''
    i = 0
    for key in scores.keys():
        strgs = strgs + str(i) + ':' + key + ','
        i = i + 1
    gid['long_name'] = 'Classification of dominant scatterer'
    gid['notes'] = strgs[0:-1]
    gid['valid_max'] = max_score.max()
    gid['valid_min'] = 0.0

    if ret_scores is False:
        rv = (gid, scores.keys())
    else:
        rv = (gid, scores.keys(), scores)
    return rv


def do_my_fuzz(radar, tex_start=2.0, tex_end=2.1):
    print('##')
    print('## CMAC calculation using fuzzy logic:')
    second_trip = {'velocity_texture': [[tex_start, tex_end, 130., 130.], 4.0],
                   'cross_correlation_ratio': [[.5, .7, 1, 1], 0.0],
                   'normalized_coherent_power': [[0, 0, .5, .6], 1.0],
                   'height': [[0, 0, 5000, 8000], 0.0],
                   'sounding_temperature': [[-100, -100, 100, 100], 0.0],
                   'SNR': [[5, 10, 1000, 1000], 1.0]}

    rain = {'velocity_texture': [[0, 0, tex_start, tex_end], 1.0],
            'cross_correlation_ratio': [[0.97, 0.98, 1, 1], 1.0],
            'normalized_coherent_power': [[0.4, 0.5, 1, 1], 1.0],
            'height': [[0, 0, 5000, 6000], 0.0],
            'sounding_temperature': [[2., 5., 100, 100], 2.0],
            'SNR': [[8, 10, 1000, 1000], 1.0]}

    snow = {'velocity_texture': [[0, 0, tex_start, tex_end], 1.0],
            'cross_correlation_ratio': [[0.65, 0.9, 1, 1], 1.0],
            'normalized_coherent_power': [[0.4, 0.5, 1, 1], 1.0],
            'height': [[0, 0, 25000, 25000], 0.0],
            'sounding_temperature': [[-100, -100, .5, 4.], 2.0],
            'SNR': [[8, 10, 1000, 1000], 1.0]}

    no_scatter = {'velocity_texture': [[tex_start, tex_end, 330., 330.], 2.0],
                  'cross_correlation_ratio': [[0, 0, 0.1, 0.2], 0.0],
                  'normalized_coherent_power': [[0, 0, 0.1, 0.2], 0.0],
                  'height': [[0, 0, 25000, 25000], 0.0],
                  'sounding_temperature': [[-100, -100, 100, 100], 0.0],
                  'SNR': [[-100, -100, 5, 10], 4.0]}

    melting = {'velocity_texture': [[0, 0, tex_start, tex_end], 0.0],
               'cross_correlation_ratio': [[0.6, 0.65, .9, .96], 2.0],
               'normalized_coherent_power': [[0.4, 0.5, 1, 1], 0],
               'height': [[0, 0, 25000, 25000], 0.0],
               'sounding_temperature': [[0, 0.1, 2, 4], 4.0],
               'SNR': [[8, 10, 1000, 1000], 0.0]}

    mbfs = {'multi_trip': second_trip, 'rain': rain, 'snow': snow,
            'no_scatter': no_scatter, 'melting': melting}

    hard_const = [['melting', 'sounding_temperature', (10, 100)],
                  ['multi_trip', 'height', (10000, 1000000)],
                  ['melting', 'sounding_temperature', (-10000, -2)],
                  ['rain', 'sounding_temperature', (-1000, -5)],
                  ['melting', 'velocity_texture', (3, 300)]]

    gid_fld, cats = cum_score_fuzzy_logic(radar, mbfs=mbfs, debug=True,
                                          hard_const=hard_const)
    rain_val = list(cats).index('rain')
    snow_val = list(cats).index('snow')
    melt_val = list(cats).index('melting')
    return _fix_rain_above_bb(gid_fld, rain_val, melt_val, snow_val), cats


def get_melt(radar, melt_cat=None):
    if melt_cat is None:
        cat_dict = {}
        for pair_str in radar.fields['gate_id']['notes'].split(','):
            cat_dict.update(
                {pair_str.split(':')[1]: int(pair_str.split(':')[0])})

        melt_cat = cat_dict['melting']

    melt_locations = np.where(radar.fields['gate_id']['data'] == melt_cat)
    kinda_cold = np.where(radar.fields['sounding_temperature']['data'] < 0)
    fzl_sounding = radar.gate_altitude['data'][kinda_cold].min()
    if len(melt_locations[0] > 1):
        fzl_pid = radar.gate_altitude['data'][melt_locations].min()
        fzl = (fzl_pid + fzl_sounding) / 2.0
    else:
        fzl = fzl_sounding

    print(fzl)
    if fzl > 5000:
        fzl = 3500.0

    return fzl

def fix_phase_fields(orig_kdp, orig_phidp, rrange, happy_kdp,
                     max_kdp=15.0):

    orig_kdp['data'][happy_kdp.gate_excluded] = 0.0
    orig_kdp['data'][orig_kdp['data']>max_kdp] = max_kdp
    interg = integrate.cumtrapz(orig_kdp['data'], rrange, axis=1)
    print(interg.shape)
    print(orig_phidp['data'].shape)
    orig_phidp['data'][:,0:-1] = interg/len(rrange)
    return orig_phidp, orig_kdp

def return_csu_kdp(radar):
    dzN = _extract_unmasked_data(radar, 'reflectivity')
    dpN = _extract_unmasked_data(radar, 'differential_phase')
    # Range needs to be supplied as a variable, and it needs to be
    # the same shape as dzN, etc.
    rng2d, az2d = np.meshgrid(radar.range['data'], radar.azimuth['data'])
    bt = time.time()
    kdN, fdN, sdN = csu_kdp.calc_kdp_bringi(
        dp=dpN, dz=dzN, rng=rng2d/1000.0, thsd=12, gs=250.0, window=5)
    print(time.time()-bt, 'seconds to run')
    csu_kdp_field = _csu_to_field(
        kdN, radar, units='deg/km', long_name='Specific Differential Phase',
        standard_name='Specific Differential Phase', dz_field='reflectivity')
    csu_filt_dp = _csu_to_field(
        fdN, radar, units='deg', long_name='Filtered Differential Phase',
        standard_name='Filtered Differential Phase', dz_field='reflectivity')
    csu_kdp_sd = _csu_to_field(
        sdN, radar, units='deg', long_name='Standard Deviation of Differential Phase',
        standard_name='Standard Deviation of Differential Phase', dz_field='reflectivity')
    return  csu_kdp_field, csu_filt_dp, csu_kdp_sd


def retrieve_qvp(radar, hts, flds=None):
    """ Calculates a quasi-vertical profile. """
    if flds is None:
        flds = ['differential_phase', 'cross_correlation_ratio',
                'spectrum_width', 'reflectivity',
                'differential_reflectivity']
    desired_angle = 20.0
    index = abs(radar.fixed_angle['data'] - desired_angle).argmin()
    ss = radar.sweep_start_ray_index['data'][index]
    se = radar.sweep_end_ray_index['data'][index]
    mid = int((ss+se)/2)
    z = radar.gate_altitude['data'][mid, :]
    qvp = {}
    for fld in flds:
        this_fld = radar.get_field(index, fld)[:, :].mean(axis=0)
        intery = interpolate.interp1d(
            z, this_fld, bounds_error=False, fill_value='extrapolate')
        ithis = intery(hts)
        qvp.update({fld:ithis})
    qvp.update({'time': radar.time})
    qvp.update({'height': hts})
    return qvp


def _fix_rain_above_bb(gid_fld, rain_class, melt_class, snow_class):
    print(snow_class)
    new_gid = copy.deepcopy(gid_fld)
    for ray_num in range(new_gid['data'].shape[0]):
        if melt_class in new_gid['data'][ray_num, :]:
            max_loc = np.where(new_gid['data'][ray_num, :] == melt_class)[0].max()
            rain_above_locs = np.where(
                new_gid['data'][ray_num, max_loc:] == rain_class)[0] + max_loc
            new_gid['data'][ray_num, rain_above_locs] = snow_class
    return new_gid


def _extract_unmasked_data(radar, field, bad=-32768):
    """ Simplify getting unmasked radar fields from Py-ART. """
    return radar.fields[field]['data'].filled(fill_value=bad)


def _csu_to_field(field, radar, units='unitless', long_name='Hydrometeor ID',
                 standard_name='Hydrometeor ID', dz_field='ZC'):
    """ Adds a newly created field to the Py-ART radar object. If reflectivity
    is a masked array, make the new field masked the same as reflectivity. """
    fill_value = -32768
    masked_field = np.ma.asanyarray(field)
    masked_field.mask = masked_field == fill_value
    if hasattr(radar.fields[dz_field]['data'], 'mask'):
        setattr(masked_field, 'mask',
                np.logical_or(
                    masked_field.mask, radar.fields[dz_field]['data'].mask))
        fill_value = radar.fields[dz_field]['_FillValue']
    field_dict = {'data': masked_field,
                  'units': units,
                  'long_name': long_name,
                  'standard_name': standard_name,
                  '_FillValue': fill_value}
    return field_dict
