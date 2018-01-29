"""
Configuration file for the Corrected Moments Antenna Coordinates (CMAC2.0).

The values for a number of parameters that change depending on which X-SAPR
is being used (I4, I5 and I6). Note: If a different type of radar is used,
values within the kdp, rainrate amd specific attenuation, for example, will
have to also be changed.

"""


config_xsapr_i6 = {
    'site': 'I6',
    'town': 'Deer Creek, OK',
    'x_compass': 'XNW',
    'site_alt': 341,
    'field_shape': (8280, 501),
    'max_lat': 37.3,
    'min_lat': 36.25,
    'max_lon': -96.9,
    'min_lon': -98.2,
    'site_i6_dms_lat': (36, 46, 2.28),
    'site_i6_dms_lon': (-97, 32, 53.16),
    'site_i5_dms_lat': (36, 29, 29.4),
    'site_i5_dms_lon': (-97, 35, 37.68),
    'site_i4_dms_lat': (36, 34, 44.4),
    'site_i4_dms_lon': (-97, 21, 49.32)}

config_xsapr_i5 = {
    'site': 'I5',
    'town': 'Garber, OK',
    'x_compass': 'XSW',
    'site_alt': 328,
    'field_shape': (8680, 501),
    'max_lat': 37.0,
    'min_lat': 36.0,
    'max_lon': -97.0,
    'min_lon': -98.3,
    'site_i6_dms_lat': (36, 46, 2.28),
    'site_i6_dms_lon': (-97, 32, 53.16),
    'site_i5_dms_lat': (36, 29, 29.4),
    'site_i5_dms_lon': (-97, 35, 37.68),
    'site_i4_dms_lat': (36, 34, 44.4),
    'site_i4_dms_lon': (-97, 21, 49.32)}

config_xsapr_i4 = {
    'site': 'I4',
    'town': 'Billings, OK',
    'x_compass': 'XSE',
    'site_alt': 330,
    'field_shape': (9200, 501),
    'max_lat': 37.1,
    'min_lat': 36.1,
    'max_lon': -96.7,
    'min_lon': -98.0,
    'site_i6_dms_lat': (36, 46, 2.28),
    'site_i6_dms_lon': (-97, 32, 53.16),
    'site_i5_dms_lat': (36, 29, 29.4),
    'site_i5_dms_lon': (-97, 35, 37.68),
    'site_i4_dms_lat': (36, 34, 44.4),
    'site_i4_dms_lon': (-97, 21, 49.32)}
