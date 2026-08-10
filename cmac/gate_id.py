"""
Helpers for interpreting the category metadata attached to a ``gate_id``
(hydrometeor ID) radar field.

CMAC's own gate id fields document their categories with a ``notes``
attribute: a comma separated list of ``"index: label"`` pairs, e.g.
``"0: multi_trip, 1: rain, 2: snow"``. The index/label separator within
each pair may be either a colon or plain whitespace (``"0 multi_trip"``).
Fields that follow the CF conventions instead (or radar objects re-read
from a file that converted ``notes`` on save) may document the same
information with a ``flag_meanings`` attribute and a parallel
``flag_values`` attribute (the matching integer codes). ``flag_meanings``
is generally comma separated, though a plain whitespace separated string
is also accepted.
"""

import re

_PAIR_SEP_RE = re.compile(r'[:\s]+')


def _label_from_pair(pair_str):
    """Extract the category label from a single ``"index: label"`` pair,
    where the index/label separator is a colon, whitespace, or both."""
    parts = _PAIR_SEP_RE.split(pair_str.strip(), maxsplit=1)
    return parts[-1].strip()


def _split_flag_meanings(flag_meanings):
    """Split a ``flag_meanings`` attribute into its individual labels,
    whether it is comma separated or plain whitespace separated."""
    if ',' in flag_meanings:
        parts = flag_meanings.split(',')
    else:
        parts = flag_meanings.split()
    return [part.strip() for part in parts if part.strip()]


def get_gate_id_categories(gate_id_field):
    """
    Return a dict mapping each gate id category label to its integer code.

    Parameters
    ----------
    gate_id_field : dict
        A Py-ART field dictionary, e.g. ``radar.fields['gate_id']``.

    """
    if 'notes' in gate_id_field:
        cat_dict = {}
        for i, pair_str in enumerate(gate_id_field['notes'].split(',')):
            cat_dict[_label_from_pair(pair_str)] = i
        return cat_dict

    if 'flag_meanings' in gate_id_field and 'flag_values' in gate_id_field:
        labels = _split_flag_meanings(gate_id_field['flag_meanings'])
        values = gate_id_field['flag_values']
        return {label: int(value) for label, value in zip(labels, values)}

    raise KeyError(
        "The 'gate_id' field must have either a 'notes' attribute or "
        "'flag_values'/'flag_meanings' attributes describing its "
        "categories.")


def gate_id_has_category(gate_id_field, category):
    """
    Return True if ``category`` is one of the documented categories of a
    ``gate_id`` field, whether documented via ``notes`` or via
    ``flag_meanings``.
    """
    if 'notes' in gate_id_field:
        return category in gate_id_field['notes']
    if 'flag_meanings' in gate_id_field:
        return category in _split_flag_meanings(gate_id_field['flag_meanings'])
    return False
