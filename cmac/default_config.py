"""
Configuration file for the Corrected Moments Antenna Coordinates (CMAC2.0).

The values for a number of parameters that change depending on which radar is
being used.

"""



##############################################################################
# Default metadata
#
# The DEFAULT_METADATA dictionary contains dictionaries which provide the
# default metadata for each radar.
##############################################################################

_DEFAULT_METADATA = {
    # X-SAPR I6 PPI metadata.
    'xsapr_i6_ppi': {
        'site_id': 'sgp',
        'facility_id': 'I6' + ': ' + 'Deer Creek, OK',
        'data_level': 'c1',
        'comment': (
            'This is highly experimental and initial data. There are many',
            'known and unknown issues. Please do not use before',
            'contacting the Translator responsible scollis@anl.gov'),
        'attributions': (
            'This data is collected by the ARM Climate Research facility.',
            'Radar system is operated by the radar engineering team',
            'radar@arm.gov and the data is processed by the precipitation',
            'radar products team. LP code courtesy of Scott Giangrande BNL.'),
        'version': '2.0 lite',
        'vap_name': 'cmac',
        'known_issues': (
            'False phidp jumps in insect regions. Still uses old',
            'Giangrande code.'),
        'developers': 'Robert Jackson, ANL. Zachary Sherman, ANL.',
        'translator': 'Scott Collis, ANL.',
        'mentors': ('Nitin Bharadwaj, PNNL. Bradley Isom, PNNL.',
                    'Joseph Hardin, PNNL. Iosif Lindenmaier, PNNL.')},

    # X-SAPR I5 PPI metadata.
    'xsapr_i5_ppi': {
        'site_id': 'sgp',
        'facility_id': 'I5' + ': ' + 'Garber, OK',
        'data_level': 'c1',
        'comment': (
            'This is highly experimental and initial data. There are many',
            'known and unknown issues. Please do not use before',
            'contacting the Translator responsible scollis@anl.gov'),
        'attributions': (
            'This data is collected by the ARM Climate Research facility.',
            'Radar system is operated by the radar engineering team',
            'radar@arm.gov and the data is processed by the precipitation',
            'radar products team. LP code courtesy of Scott Giangrande BNL.'),
        'version': '2.0 lite',
        'vap_name': 'cmac',
        'known_issues': (
            'False phidp jumps in insect regions. Still uses old',
            'Giangrande code.'),
        'developers': 'Robert Jackson, ANL. Zachary Sherman, ANL.',
        'translator': 'Scott Collis, ANL.',
        'mentors': ('Nitin Bharadwaj, PNNL. Bradley Isom, PNNL.',
                    'Joseph Hardin, PNNL. Iosif Lindenmaier, PNNL.')},

    # X-SAPR I5 PPI metadata.
    'xsapr_i5_cfr_ppi': {
        'site_id': 'sgp',
        'facility_id': 'I5' + ': ' + 'Garber, OK',
        'data_level': 'c1',
        'comment': (
            'This is highly experimental and initial data. There are many',
            'known and unknown issues. Please do not use before',
            'contacting the Translator responsible scollis@anl.gov'),
        'attributions': (
            'This data is collected by the ARM Climate Research facility.',
            'Radar system is operated by the radar engineering team',
            'radar@arm.gov and the data is processed by the precipitation',
            'radar products team. LP code courtesy of Scott Giangrande BNL.'),
        'version': '2.0 lite',
        'vap_name': 'cmac',
        'known_issues': (
            'False phidp jumps in insect regions. Still uses old',
            'Giangrande code.'),
        'developers': 'Robert Jackson, ANL. Zachary Sherman, ANL.',
        'translator': 'Scott Collis, ANL.',
        'mentors': ('Nitin Bharadwaj, PNNL. Bradley Isom, PNNL.',
                    'Joseph Hardin, PNNL. Iosif Lindenmaier, PNNL.')},

    # X-SAPR I4 PPI metadata.
    'xsapr_i4_ppi': {
        'site_id': 'sgp',
        'facility_id': 'I4' + ': ' + 'Billings, OK',
        'data_level': 'c1',
        'comment': (
            'This is highly experimental and initial data. There are many',
            'known and unknown issues. Please do not use before',
            'contacting the Translator responsible scollis@anl.gov'),
        'attributions': (
            'This data is collected by the ARM Climate Research facility.',
            'Radar system is operated by the radar engineering team',
            'radar@arm.gov and the data is processed by the precipitation',
            'radar products team. LP code courtesy of Scott Giangrande BNL.'),
        'version': '2.0 lite',
        'vap_name': 'cmac',
        'known_issues': (
            'False phidp jumps in insect regions. Still uses old',
            'Giangrande code.'),
        'developers': 'Robert Jackson, ANL. Zachary Sherman, ANL.',
        'translator': 'Scott Collis, ANL.',
        'mentors': ('Nitin Bharadwaj, PNNL. Bradley Isom, PNNL.',
                    'Joseph Hardin, PNNL. Iosif Lindenmaier, PNNL.')},

    # X-SAPR I6 Sector metadata.
    'xsapr_i6_sec': {
        'site_id': 'sgp',
        'facility_id': 'I6' + ': ' + 'Deer Creek, OK',
        'data_level': 'c1',
        'comment': (
            'This is highly experimental and initial data. There are many',
            'known and unknown issues. Please do not use before',
            'contacting the Translator responsible scollis@anl.gov'),
        'attributions': (
            'This data is collected by the ARM Climate Research facility.',
            'Radar system is operated by the radar engineering team',
            'radar@arm.gov and the data is processed by the precipitation',
            'radar products team. LP code courtesy of Scott Giangrande BNL.'),
        'version': '2.0 lite',
        'vap_name': 'cmac',
        'known_issues': (
            'False phidp jumps in insect regions. Still uses old',
            'Giangrande code.'),
        'developers': 'Robert Jackson, ANL. Zachary Sherman, ANL.',
        'translator': 'Scott Collis, ANL.',
        'mentors': ('Nitin Bharadwaj, PNNL. Bradley Isom, PNNL.',
                    'Joseph Hardin, PNNL. Iosif Lindenmaier, PNNL.')},

    # X-SAPR I5 Sector metadata.
    'xsapr_i5_sec': {
        'site_id': 'sgp',
        'facility_id': 'I5' + ': ' + 'Garber, OK',
        'data_level': 'c1',
        'comment': (
            'This is highly experimental and initial data. There are many',
            'known and unknown issues. Please do not use before',
            'contacting the Translator responsible scollis@anl.gov'),
        'attributions': (
            'This data is collected by the ARM Climate Research facility.',
            'Radar system is operated by the radar engineering team',
            'radar@arm.gov and the data is processed by the precipitation',
            'radar products team. LP code courtesy of Scott Giangrande BNL.'),
        'version': '2.0 lite',
        'vap_name': 'cmac',
        'known_issues': (
            'False phidp jumps in insect regions. Still uses old',
            'Giangrande code.'),
        'developers': 'Robert Jackson, ANL. Zachary Sherman, ANL.',
        'translator': 'Scott Collis, ANL.',
        'mentors': ('Nitin Bharadwaj, PNNL. Bradley Isom, PNNL.',
                    'Joseph Hardin, PNNL. Iosif Lindenmaier, PNNL.')},

    # X-SAPR I4 Sector metadata.
    'xsapr_i4_sec': {
        'site_id': 'sgp',
        'facility_id': 'I4' + ': ' + 'Billings, OK',
        'data_level': 'c1',
        'comment': (
            'This is highly experimental and initial data. There are many',
            'known and unknown issues. Please do not use before',
            'contacting the Translator responsible scollis@anl.gov'),
        'attributions': (
            'This data is collected by the ARM Climate Research facility.',
            'Radar system is operated by the radar engineering team',
            'radar@arm.gov and the data is processed by the precipitation',
            'radar products team. LP code courtesy of Scott Giangrande BNL.'),
        'version': '2.0 lite',
        'vap_name': 'cmac',
        'known_issues': (
            'False phidp jumps in insect regions. Still uses old',
            'Giangrande code.'),
        'developers': 'Robert Jackson, ANL. Zachary Sherman, ANL.',
        'translator': 'Scott Collis, ANL.',
        'mentors': ('Nitin Bharadwaj, PNNL. Bradley Isom, PNNL.',
                    'Joseph Hardin, PNNL. Iosif Lindenmaier, PNNL.')},

    # CACTI C-SAPR 2 metadata.
    'cacti_csapr2_ppi': {
        'site_id': 'cor',  # 'ARM Mobile Facility Argentina'
        'facility_id': 'c1',
        'comment': (
            'This is highly experimental and initial data. There are many',
            'known and unknown issues. Please do not use before',
            'contacting the Translator responsible scollis@anl.gov'),
        'attributions': (
            'This data is collected by the ARM Climate Research facility.',
            'Radar system is operated by the radar engineering team',
            'radar@arm.gov and the data is processed by the precipitation',
            'radar products team. LP code courtesy of Scott Giangrande BNL.'),
        'version': '2.0 lite',
        'vap_name': 'cmac',
        'known_issues': (
            'False phidp jumps in insect regions. Still uses old',
            'Giangrande code.',
            'Issues with some snow below melting layer.'),
        'developers': 'Robert Jackson, ANL. Zachary Sherman, ANL.',
        'translator': 'Scott Collis, ANL.',
        'mentors': ('Nitin Bharadwaj, PNNL. Bradley Isom, PNNL.',
                    'Joseph Hardin, PNNL. Iosif Lindenmaier, PNNL.')},
}



##############################################################################
# Default field names
#
# The DEFAULT_FIELD_NAMES dictionary contains field names for each radar and
# sonde field names that will be used with that radar.
##############################################################################

_DEFAULT_FIELD_NAMES = {
    # X-SAPR I6 PPI field names.
    'xsapr_i6_ppi': {
        # Radar field names
        'input_zdr': 'differential_reflectivity',
        'reflectivity': 'reflectivity',
        'velocity': 'velocity',
        'normalized_coherent_power': 'normalized_coherent_power',
        'cross_correlation_ratio': 'cross_correlation_ratio',
        'differential_reflectivity': 'differential_reflectivity',
        # Sonde field names
        'altitude': 'alt',
        'temperature': 'tdry',
        'u_wind': 'u_wind',
        'v_wind': 'v_wind',
        # Input field names to attenuation code
        'zdr_field': 'corrected_differential_reflectivity',
        'pia_field': 'path_integrated_attenuation',
        'phidp_field': 'filtered_corrected_differential_phase',
        'refl_field': 'corrected_reflectivity'},
 
    # X-SAPR I5 PPI field names.
    'xsapr_i5_ppi': {
        # Radar field names
        'input_zdr': 'differential_reflectivity',
        'reflectivity': 'reflectivity',
        'velocity': 'velocity',
        'normalized_coherent_power': 'normalized_coherent_power',
        'cross_correlation_ratio': 'cross_correlation_ratio',
        'differential_reflectivity': 'differential_reflectivity',
        # Sonde field names
        'altitude': 'alt',
        'temperature': 'tdry',
        'u_wind': 'u_wind',
        'v_wind': 'v_wind',
        # Input field names to attenuation code
        'zdr_field': 'corrected_differential_reflectivity',
        'pia_field': 'path_integrated_attenuation',
        'phidp_field': 'filtered_corrected_differential_phase',
        'refl_field': 'corrected_reflectivity'},

    'xsapr_i5_cfr_ppi': {
        # Radar field names
        'input_zdr': 'differential_reflectivity',
        'reflectivity': 'reflectivity',
        'velocity': 'mean_doppler_velocity',
        'normalized_coherent_power': 'normalized_coherent_power',
        'cross_correlation_ratio': 'cross_correlation_ratio_hv',
        # Sonde field names
        'altitude': 'alt',
        'temperature': 'tdry',
        'u_wind': 'u_wind',
        'v_wind': 'v_wind',
        # Input field names to attenuation code
        'zdr_field': 'corrected_differential_reflectivity',
        'pia_field': 'path_integrated_attenuation',
        'phidp_field': 'filtered_corrected_differential_phase',
        'refl_field': 'corrected_reflectivity'},

    # X-SAPR I4 PPI field names.
    'xsapr_i4_ppi': {
        # Radar field names
        'input_zdr': 'differential_reflectivity',
        'reflectivity': 'reflectivity',
        'velocity': 'velocity',
        'normalized_coherent_power': 'normalized_coherent_power',
        'cross_correlation_ratio': 'cross_correlation_ratio',
        'differential_reflectivity': 'differential_reflectivity',
        # Sonde field names
        'altitude': 'alt',
        'temperature': 'tdry',
        'u_wind': 'u_wind',
        'v_wind': 'v_wind',
        # Input field names to attenuation code
        'zdr_field': 'corrected_differential_reflectivity',
        'pia_field': 'path_integrated_attenuation',
        'phidp_field': 'filtered_corrected_differential_phase',
        'refl_field': 'corrected_reflectivity'},

    # X-SAPR I6 Sector field names.
    'xsapr_i6_sec': {
        # Radar field names
        'input_zdr': 'differential_reflectivity',
        'reflectivity': 'reflectivity',
        'velocity': 'velocity',
        'normalized_coherent_power': 'normalized_coherent_power',
        'cross_correlation_ratio': 'cross_correlation_ratio',
        'differential_reflectivity': 'differential_reflectivity',
        # Sonde field names
        'altitude': 'alt',
        'temperature': 'tdry',
        'u_wind': 'u_wind',
        'v_wind': 'v_wind',
        # Input field names to attenuation code
        'zdr_field': 'corrected_differential_reflectivity',
        'pia_field': 'path_integrated_attenuation',
        'phidp_field': 'filtered_corrected_differential_phase',
        'refl_field': 'corrected_reflectivity'},

    # X-SAPR I5 Sector field names.
    'xsapr_i5_sec': {
        # Radar field names
        'input_zdr': 'differential_reflectivity',
        'reflectivity': 'reflectivity',
        'velocity': 'velocity',
        'normalized_coherent_power': 'normalized_coherent_power',
        'cross_correlation_ratio': 'cross_correlation_ratio',
        'differential_reflectivity': 'differential_reflectivity',
        # Sonde field names
        'altitude': 'alt',
        'temperature': 'tdry',
        'u_wind': 'u_wind',
        'v_wind': 'v_wind',
        # Input field names to attenuation code
        'zdr_field': 'corrected_differential_reflectivity',
        'pia_field': 'path_integrated_attenuation',
        'phidp_field': 'filtered_corrected_differential_phase',
        'refl_field': 'corrected_reflectivity'},

    # X-SAPR I4 Sector field names.
    'xsapr_i4_sec': {
        # Radar field names
        'input_zdr': 'differential_reflectivity',
        'reflectivity': 'reflectivity',
        'velocity': 'velocity',
        'normalized_coherent_power': 'normalized_coherent_power',
        'cross_correlation_ratio': 'cross_correlation_ratio',
        'differential_reflectivity': 'differential_reflectivity',
        # Sonde field names
        'altitude': 'alt',
        'temperature': 'tdry',
        'u_wind': 'u_wind',
        'v_wind': 'v_wind',
        # Input field names to attenuation code
        'zdr_field': 'corrected_differential_reflectivity',
        'pia_field': 'path_integrated_attenuation',
        'phidp_field': 'filtered_corrected_differential_phase',
        'refl_field': 'corrected_reflectivity'},

    # CACTI C-SAPR 2 field names.
    'cacti_csapr2_ppi': {
        # Radar field names
        'input_zdr': 'differential_reflectivity',
        'reflectivity': 'uncorrected_reflectivity_h',  # need to change to input_reflectivity
        'velocity': 'mean_doppler_velocity',
        'normalized_coherent_power': 'normalized_coherent_power',
        'cross_correlation_ratio': 'copol_correlation_coeff',
        'input_phidp_field': 'uncorrected_differential_phase',
        'input_clutter_corrected_reflectivity': 'reflectivity',
        'clutter': 'ground_clutter',
        'differential_reflectivity': 'differential_reflectivity',
        # Sonde field names
        'altitude': 'alt',
        'temperature': 'tdry',
        'u_wind': 'u_wind',
        'v_wind': 'v_wind',
        # Input field names to attenuation code
        'zdr_field': 'corrected_differential_reflectivity',
        'pia_field': 'path_integrated_attenuation',
        'phidp_field': 'filtered_corrected_differential_phase',  # output phidp, need to change
        'refl_field': 'corrected_reflectivity'}  # output Z field
}

##############################################################################
# Membership functions
#
# This goes into the following section cmac_config
##############################################################################

# csapr2_cordoba
cacti_csapr2_ppi_mbfs={'multi_trip': {'velocity_texture': [[7.5, 7.8, 130.0, 130.0], 4.0],
                                 'copol_correlation_coeff': [[0.5, 0.7, 1, 1], 0.0],
                                 'normalized_coherent_power': [[0, 0, 0.5, 0.6], 1.0],
                                 'height': [[0, 0, 5000, 8000], 0.0],
                                 'sounding_temperature': [[-100, -100, 100, 100], 0.0],
                                 'signal_to_noise_ratio': [[5.0, 8.0, 1000, 1000], 1.0]},
                  'rain': {'velocity_texture': [[0, 0, 2.0, 2.1], 1.0],
                           'copol_correlation_coeff': [[0.97, 0.98, 1, 1], 1.0],
                           'normalized_coherent_power': [[0.4, 0.5, 1, 1], 1.0],
                           'height': [[0, 0, 5000, 6000], 0.0],
                           'sounding_temperature': [[2.0, 5.0, 100, 100], 2.0],
                           'signal_to_noise_ratio': [[20, 22, 1000, 1000], 1.0]},
                  'snow': {'velocity_texture': [[0, 0, 2.0, 2.1], 1.0],
                           'copol_correlation_coeff': [[0.65, 0.9, 1, 1], 1.0],
                           'normalized_coherent_power': [[0.4, 0.5, 1, 1], 1.0],
                           'height': [[0, 0, 25000, 25000], 0.0],
                           'sounding_temperature': [[-100, -100, 0.5, 4.0], 2.0],
                           'signal_to_noise_ratio': [[20, 22, 1000, 1000], 1.0]},
                  'no_scatter': {'velocity_texture': [[0, 0, 330.0, 330.0], 2.0],
                                 'copol_correlation_coeff': [[0, 0, 0.1, 0.2], 0.0],
                                 'normalized_coherent_power': [[0, 0, 0.1, 0.2], 0.0],
                                 'height': [[0, 0, 25000, 25000], 0.0],
                                 'sounding_temperature': [[-100, -100, 100, 100], 0.0],
                                 'signal_to_noise_ratio': [[-100, -100, 20, 22], 4.0]},
                'melting': {'velocity_texture': [[0, 0, 2.0, 2.1], 0.0],
                            'copol_correlation_coeff': [[0.6, 0.65, 0.9, 0.96], 2.0],
                            'normalized_coherent_power': [[0.4, 0.5, 1, 1], 0],
                            'height': [[0, 0, 25000, 25000], 0.0],
                            'sounding_temperature': [[0, 0.1, 2, 4], 4.0],
                            'signal_to_noise_ratio': [[20, 22, 1000, 1000], 0.0]}}

cacti_csapr2_ppi_hard_const = [['melting', 'sounding_temperature', (10, 100)],
                              ['multi_trip', 'height', (10000, 1000000)],
                              ['melting', 'sounding_temperature', (-10000, -2)],
                              ['rain', 'sounding_temperature', (-1000, -5)],
                              ['melting', 'velocity_texture', (3, 300)]]


##############################################################################
# Default CMAC 2.0 values
#
# The DEFAULT_CMAC_VALUES dictionary contains dictionaries for radars that
# contains parameter values used in the CMAC 2.0 processing. Values in these
# radar dictionaries are used for a variety of functions, such as hydrometeor
# classification, phase processing, specific attenuation and more. These
# values are all used within cmac_radar.py.
##############################################################################

_DEFAULT_CMAC_VALUES = {
    # X-SAPR I6 PPI CMAC 2.0 processing values.
    'xsapr_i6_ppi': {
        'save_name': 'sgpxsaprcmacsurI6.c1',
        'sonde_name': 'sgpsondewnpnC1.b1',
        'x_compass': 'XNW',
        'site_alt': 341,
        'ref_offset': 0.0,
        'self_const': 60000.00,
        'attenuation_a_coef': 0.17,
        'c_coef': 0.05,
        'd_coef': 1,
        'beta_coef': 1,
        'zdr_offset': 3.05,
        'rain_rate_a_coef': 51.3,
        'rain_rate_b_coef': 0.81},

    # X-SAPR I5 PPI CMAC 2.0 processing values.
    'xsapr_i5_ppi': {
        'save_name': 'sgpxsaprcmacsurI5.c1',
        'sonde_name': 'sgpsondewnpnC1.b1',
        'x_compass': 'XSW',
        'site_alt': 328,
        'ref_offset': 0.0,
        'self_const': 60000.00,
        'attenuation_a_coef': 0.17,
        'c_coef': 0.05,
        'd_coef': 1,
        'beta_coef': 1,
        'zdr_offset': 3.05,
        'rain_rate_a_coef': 51.3,
        'rain_rate_b_coef': 0.81},

    # X-SAPR I5 PPI CMAC 2.0 processing values.
    'xsapr_i5_cfr_ppi': {
        'save_name': 'sgpxsaprcmacsurI5.c1',
        'sonde_name': 'sgpsondewnpnC1.b1',
        'x_compass': 'XSW',
        'site_alt': 328,
        'ref_offset': 0.0,
        'self_const': 60000.00,
        'attenuation_a_coef': 0.17,
        'rain_rate_a_coef': 51.3,
        'rain_rate_b_coef': 0.81},

    # X-SAPR I4 PPI CMAC 2.0 processing values.
    'xsapr_i4_ppi': {
        'save_name': 'sgpxsaprcmacsurI4.c1',
        'sonde_name': 'sgpsondewnpnC1.b1',
        'x_compass': 'XSE',
        'site_alt': 330,
        'ref_offset': 0.0,
        'self_const': 60000.00,
        'attenuation_a_coef': 0.17,
        'c_coef': 0.05,
        'd_coef': 1,
        'beta_coef': 1,
        'zdr_offset': 3.05,
        'rain_rate_a_coef': 51.3,
        'rain_rate_b_coef': 0.81},

    # X-SAPR I6 Sector CMAC 2.0 processing values.
    'xsapr_i6_sec': {
        'save_name': 'sgpxsaprcmacsecI6.c1',
        'sonde_name': 'sgpsondewnpnC1.b1',
        'x_compass': 'XNW',
        'site_alt': 341,
        'ref_offset': 0.0,
        'self_const': 60000.00,
        'attenuation_a_coef': 0.17,
        'c_coef': 0.05,
        'd_coef': 1,
        'beta_coef': 1,
        'zdr_offset': 3.05,
        'rain_rate_a_coef': 51.3,
        'rain_rate_b_coef': 0.81},

    # X-SAPR I5 Sector CMAC 2.0 processing values.
    'xsapr_i5_sec': {
        'save_name': 'sgpxsaprcmacsecI5.c1',
        'sonde_name': 'sgpsondewnpnC1.b1',
        'x_compass': 'XSW',
        'site_alt': 328,
        'ref_offset': 0.0,
        'self_const': 60000.00,
        'attenuation_a_coef': 0.17,
        'c_coef': 0.05,
        'd_coef': 1,
        'beta_coef': 1,
        'zdr_offset': 3.05,
        'rain_rate_a_coef': 51.3,
        'rain_rate_b_coef': 0.81},

    # X-SAPR I4 Sector CMAC 2.0 processing values.
    'xsapr_i4_sec': {
        'save_name': 'sgpxsaprcmacsecI4.c1',
        'sonde_name': 'sgpsondewnpnC1.b1',
        'x_compass': 'XSE',
        'site_alt': 330,
        'ref_offset': 0.0,
        'self_const': 60000.00,
        'attenuation_a_coef': 0.17,
        'c_coef': 0.05,
        'd_coef': 1,
        'beta_coef': 1,
        'zdr_offset': 3.05,
        'rain_rate_a_coef': 51.3,
        'rain_rate_b_coef': 0.81},

    # CACTI C-SAPR 2 CMAC 2.0 processing values.
    'cacti_csapr2_ppi': {
        'save_name': 'cacticsapr2cmacppi.c1',
        'sonde_name': 'corsondewnpnM1.b1',
        'site_alt': 1141,
        'ref_offset': 0.0,
        'self_const': 60000.00,
        'attenuation_a_coef': 0.08,
        'c_coef': 0.3,
        'd_coef': 1.804,
        'beta_coef': 0.64884,  # ZDR corrections
        'flip_phidp': True,
        'phidp_flipped': ['uncorrected_differential_phase','differential_phase'],
        'zdr_offset': -3.8,
        'offset_zdrs': ['differential_reflectivity_lag_1', 'differential_reflectivity'],
        'mbfs': cacti_csapr2_ppi_mbfs,
        'hard_const': cacti_csapr2_ppi_hard_const,
        'gen_clutter_from_refl': True,
        'gen_clutter_from_refl_diff': -12.0,
        'gen_clutter_from_refl_alt': 2000.0,
        'clutter_mask_z_for_texture': True,
        'rain_rate_a_coef': 51.3,
        'rain_rate_b_coef': 0.81}  # We expect clutter corrected fields now
}


##############################################################################
# Default plot values
#
# The DEFAULT_PLOT_VALUES dictionary contains dictionaries for radars that
# contains parameter values used in the CMAC 2.0 quicklooks. Values in these
# radar dictionaries are used for defining specifications for plotting
# specific radars. Specifications such as, max latitude and longitude, sweep
# and coordinates for dual doppler lobes. These values are all used within
# cmac_quicklooks.py.
##############################################################################

_DEFAULT_PLOT_VALUES = {
    # X-SAPR I6 PPI plot values.
    'xsapr_i6_ppi': {
        'save_name': 'sgpxsaprcmacsurI6.c1',
        'facility': 'I6',
        'sweep': 3,
        'max_lat': 37.3,
        'min_lat': 36.25,
        'max_lon': -96.9,
        'min_lon': -98.2,
        'site_i6_dms_lat': (36, 46, 2.28),
        'site_i6_dms_lon': (-97, 32, 53.16),
        'site_i5_dms_lat': (36, 29, 29.4),
        'site_i5_dms_lon': (-97, 35, 37.68),
        'site_i4_dms_lat': (36, 34, 44.4),
        'site_i4_dms_lon': (-97, 21, 49.32)},

    # X-SAPR I5 PPI plot values.
    'xsapr_i5_ppi': {
        'save_name': 'sgpxsaprcmacsurI5.c1',
        'facility': 'I5',
        'sweep': 3,
        'max_lat': 37.0,
        'min_lat': 36.0,
        'max_lon': -97.0,
        'min_lon': -98.3,
        'site_i6_dms_lat': (36, 46, 2.28),
        'site_i6_dms_lon': (-97, 32, 53.16),
        'site_i5_dms_lat': (36, 29, 29.4),
        'site_i5_dms_lon': (-97, 35, 37.68),
        'site_i4_dms_lat': (36, 34, 44.4),
        'site_i4_dms_lon': (-97, 21, 49.32)},
    
    # X-SAPR I5 PPI plot values.
    'xsapr_i5_cfr_ppi': {
        'save_name': 'sgpxsaprcmacsurI5.c1',
        'facility': 'I5',
        'sweep': 3,
        'max_lat': 37.0,
        'min_lat': 36.0,
        'max_lon': -97.0,
        'min_lon': -98.3,
        'site_i6_dms_lat': (36, 46, 2.28),
        'site_i6_dms_lon': (-97, 32, 53.16),
        'site_i5_dms_lat': (36, 29, 29.4),
        'site_i5_dms_lon': (-97, 35, 37.68),
        'site_i4_dms_lat': (36, 34, 44.4),
        'site_i4_dms_lon': (-97, 21, 49.32)},

    # X-SAPR I4 PPI plot values.
    'xsapr_i4_ppi': {
        'save_name': 'sgpxsaprcmacsurI4.c1',
        'facility': 'I4',
        'sweep': 3,
        'max_lat': 37.1,
        'min_lat': 36.1,
        'max_lon': -96.7,
        'min_lon': -98.0,
        'site_i6_dms_lat': (36, 46, 2.28),
        'site_i6_dms_lon': (-97, 32, 53.16),
        'site_i5_dms_lat': (36, 29, 29.4),
        'site_i5_dms_lon': (-97, 35, 37.68),
        'site_i4_dms_lat': (36, 34, 44.4),
        'site_i4_dms_lon': (-97, 21, 49.32)},

    # X-SAPR I6 Sector plot values.
    'xsapr_i6_sec': {
        'save_name': 'sgpxsaprcmacsecI6.c1',
        'facility': 'I6',
        'sweep': 1,
        'max_lat': 36.85,
        'min_lat': 35.8,
        'max_lon': -96.5,
        'min_lon': -98.15,
        'site_i6_dms_lat': (36, 46, 2.28),
        'site_i6_dms_lon': (-97, 32, 53.16),
        'site_i5_dms_lat': (36, 29, 29.4),
        'site_i5_dms_lon': (-97, 35, 37.68),
        'site_i4_dms_lat': (36, 34, 44.4),
        'site_i4_dms_lon': (-97, 21, 49.32)},

    # X-SAPR I5 Sector plot values.
    'xsapr_i5_sec': {
        'save_name': 'sgpxsaprcmacsecI5.c1',
        'facility': 'I5',
        'sweep': 1,
        'max_lat': 37.4,
        'min_lat': 36.49,
        'max_lon': -96.45,
        'min_lon': -97.8,
        'site_i6_dms_lat': (36, 46, 2.28),
        'site_i6_dms_lon': (-97, 32, 53.16),
        'site_i5_dms_lat': (36, 29, 29.4),
        'site_i5_dms_lon': (-97, 35, 37.68),
        'site_i4_dms_lat': (36, 34, 44.4),
        'site_i4_dms_lon': (-97, 21, 49.32)},

    # X-SAPR I4 Sector plot values.
    'xsapr_i4_sec': {
        'save_name': 'sgpxsaprcmacsecI4.c1',
        'facility': 'I4',
        'sweep': 1,
        'max_lat': 37.4,
        'min_lat': 36.05,
        'max_lon': -97.3,
        'min_lon': -98.6,
        'site_i6_dms_lat': (36, 46, 2.28),
        'site_i6_dms_lon': (-97, 32, 53.16),
        'site_i5_dms_lat': (36, 29, 29.4),
        'site_i5_dms_lon': (-97, 35, 37.68),
        'site_i4_dms_lat': (36, 34, 44.4),
        'site_i4_dms_lon': (-97, 21, 49.32)},

    # CACTI C-SAPR 2 plot values.
    'cacti_csapr2_ppi': {
        'save_name': 'cacticsaprcmacppi.c1',
        'sweep': 3}
}
