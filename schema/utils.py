from datetime import datetime

from cytoolz.functoolz import curry
from pydantic import validator


def non_negative(value):
    if value < 0:
        raise ValueError('must be non-negative.')
    return value


def percentage_string(value):
    if value == 'N/A':
        return value
    _ = float(value.rstrip('%'))
    return value


@curry
def length_constraint(target_length, value):
    if len(value) != target_length:
        raise ValueError(f'must be of length {target_length}.')
    return value


def sorted_by_capacity(value):
    if value != sorted(value, key=lambda country: -country.capacity_mw):
        raise ValueError('must be sorted by the capacity.')
    return value


def valid_year(value):
    if value < 2000 or value > 2050:
        raise ValueError('year must be between 2000 and 2050.')
    return value


def valid_long_lat(value):
    if len(value) != 2:
        raise ValueError('long-lat pair must have length of two.')
    longitude, latitude = value
    if not (-180.0 <= longitude <= 180.0 and -90.0 <= latitude <= 90.0):
        raise ValueError(
            f'invalid long-lat pair {value}. '
            'expected long-lat ranges [-180, 180] and [-90, 90] respectively.'
        )
    return value


def valid_bounds(value):
    if len(value) != 4:
        raise ValueError('bounds must have length of four.')
    else:
        left, top, right, bottom = value
        _ = valid_long_lat([left, top])
        _ = valid_long_lat([right, bottom])
        if not (left <= right and top <= bottom):
            raise ValueError('invalid bounding box.')
    return value


@curry
def min_length(threshold, value):
    if len(value) < threshold:
        raise ValueError(f'minimum length required: {threshold}.')
    return value


@curry
def require_dict_keys(keys, value):
    missing_keys = {key for key in keys if key not in value}
    if missing_keys:
        raise ValueError(f'expected keys: {missing_keys}.')
    return value


def validate(validate_fn, *fields):
    return validator(*fields, allow_reuse=True)(validate_fn)


def american_date(value):
    _ = datetime.strptime(value, '%B %d, %Y')
    return value
