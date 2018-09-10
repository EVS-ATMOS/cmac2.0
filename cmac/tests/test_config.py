""" Unit Tests for CMAC 2.0's config.py module. """

from cmac import (get_cmac_values, get_field_names,
                  get_metadata, get_plot_values)


def test_get_cmac_values:
    cmac_config = get_cmac_calues('xsapr_i5')
    assert type(cmac_config) == dict

    assert cmac_config['save_name'] == 'sgpxsaprcmacsurI5.c1'
    assert cmac_config['site_alt'] == 341
    assert cmac_config['ref_offset'] == 0.0
    assert cmac_config['self_const'] == 60000.00
    assert cmac_config['attenuation_a_coef'] == 0.017

def test_get_field_names:
    field_config = get_field_names('xsapr_i5')
    assert type(field_config) == dict

    assert field_config['reflectivity'] == 'reflectivity'
    assert field_config['temperature'] == 'tdry'


def test_get_metadata:
    meta_config = get_metadata('xsapr_i5')
    assert type(meta_config) == dict

def test_get_plot_values:
    plot_config = get_plot_values('xsapr_i5')
    assert type(plot_config) == dict
