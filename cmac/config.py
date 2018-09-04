"""
Configuration file for the Corrected Moments Antenna Coordinates (CMAC2.0).

The values for a number of parameters that change depending on which radar is
being used.

Radar Parameters
----------

save_name : String
    The name extension to output the cmac radar object and quicklooks as.
site_alt : Float
    The altitude of the radar.
attenuation_a_coef : Float
    A coefficient in attenuation calculation.
field_shape : Tuple
    Shape of the radar data. This is needed due to the clutter calculation.

Plotting Parameters
-------------------

sweep : Integer
    Radar sweep to be plotted.
max_lat : Float
    Maximum latitude to plot.
min_lat : Float
    Minimum latitude to plot.
max_lon : Float
    Maximum longitude to plot.
min_lon : Float
    Minimum longitude to plot.

"""

config_xsapr_i6 = {
    'save_name': 'sgpxsaprcmacsurI6.c1',
    'facility': 'I6',
    'x_compass': 'XNW',
    'site_alt': 341,
    'ref_offset': 0.0,
    'self_const': 60000.00,
    'attenuation_a_coef': 0.17,
    'field_shape': (8280, 501),
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
    'site_i4_dms_lon': (-97, 21, 49.32),
    'sonde': {'temperature': 'tdry',
              'height': 'alt'},
    'metadata': {
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
                    'Joseph Hardin, PNNL. Iosif Lindenmaier, PNNL.')}}

config_xsapr_i5 = {
    'save_name': 'sgpxsaprcmacsurI5.c1',
    'facility': 'I5',
    'x_compass': 'XSW',
    'site_alt': 328,
    'ref_offset': 0.0,
    'self_const': 60000.00,
    'attenuation_a_coef': 0.17,
    'field_shape': (8680, 501),
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
    'site_i4_dms_lon': (-97, 21, 49.32),
    'sonde': {'temperature': 'tdry',
              'height': 'alt'},
    'metadata': {
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
                    'Joseph Hardin, PNNL. Iosif Lindenmaier, PNNL.')}}

config_xsapr_i4 = {
    'save_name': 'sgpxsaprcmacsurI4.c1',
    'facility': 'I4',
    'x_compass': 'XSE',
    'site_alt': 330,
    'ref_offset': 0.0,
    'self_const': 60000.00,
    'attenuation_a_coef': 0.17,
    'field_shape': (9200, 501),
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
    'site_i4_dms_lon': (-97, 21, 49.32),
    'sonde': {'temperature': 'tdry',
              'height': 'alt'},
    'metadata': {
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
                    'Joseph Hardin, PNNL. Iosif Lindenmaier, PNNL.')}}
