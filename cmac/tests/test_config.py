""" Unit Tests for CMAC 2.0's config.py module. """

from cmac import (get_cmac_values, get_field_names,
                  get_plot_values, get_metadata)


def test_get_cmac_values():
    cmac_config = get_cmac_values('xsapr_i5_ppi')
    assert type(cmac_config) == dict

    assert cmac_config['save_name'] == 'sgpxsaprcmacsurI5.c1'
    assert cmac_config['site_alt'] == 328
    assert cmac_config['ref_offset'] == 0.0
    assert cmac_config['self_const'] == 60000.00
    assert cmac_config['attenuation_a_coef'] == 0.17

def test_get_field_names():
    field_config = get_field_names('xsapr_i5_ppi')
    assert type(field_config) == dict

    assert field_config['reflectivity'] == 'reflectivity'
    assert field_config['temperature'] == 'tdry'


def test_get_metadata():
    meta_config = get_metadata('xsapr_i5_ppi')
    assert type(meta_config) == dict

    assert meta_config['site_id'] == 'sgp'
    assert meta_config['facility_id'] == 'I5: Garber, OK'
    assert meta_config['version'] == '2.0 lite'
    

def test_get_plot_values():
    plot_config = get_plot_values('xsapr_i5_ppi')
    assert type(plot_config) == dict

    assert plot_config['sweep'] == 3
    assert plot_config['max_lat'] == 37.0
    assert plot_config['min_lon'] == -98.3
    assert plot_config['site_i5_dms_lat'] == (36, 29, 29.4)
    assert plot_config['site_i5_dms_lon'] == (-97, 35, 37.68)
