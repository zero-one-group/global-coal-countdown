from datetime import datetime
from typing import Any, List


def is_positive(value: int | float) -> int | float:
    if value < 0:
        raise ValueError("must be non-negative.")
    return value


def is_valid_year(value: int):
    if value < 2000 or value > 2050:
        raise ValueError("year must be between 2000 and 2050.")
    return value


def is_valid_long_lat(long_lat_list: List) -> List:
    if len(long_lat_list) != 2:
        raise ValueError("long-lat pair must have length of two.")
    longitude, latitude = long_lat_list
    if not (-180.0 <= longitude <= 180.0 and -90.0 <= latitude <= 90.0):
        raise ValueError(
            f"invalid long-lat pair {long_lat_list}. "
            "expected long-lat ranges [-180, 180] and [-90, 90] respectively."
        )
    return long_lat_list


def is_unique(values: Any, extract_fn):
    extracted = [extract_fn(value) for value in values]
    if len(set(extracted)) != len(extracted):
        raise ValueError(f"not unique elements: {values}")
    return values


def is_american_date(value: str):
    _ = datetime.strptime(value, "%B %d, %Y")
    return value


def is_greater_than_min_length(threshold, value):
    if len(value) < threshold:
        raise ValueError(f"minimum length required: {threshold}.")
    return value


def is_required_keys_exist(keys, value):
    missing_keys = {key for key in keys if key not in value}
    if missing_keys:
        raise ValueError(f"expected keys: {missing_keys}.")
    return value


def is_valid_article_id(value: str):
    if not isinstance(value, str):
        raise TypeError("string required")
    if "coalwire" not in value.lower() and "newsapi" not in value.lower():
        raise ValueError("ArticleID does not have the required format.")
    return value


def is_len(value: str, ln: int):
    if not len(value) == ln:
        raise ValueError(f"{value} length is not {ln}")
    return value


def is_valid_bounds(value: list[float]):
    if len(value) != 4:
        raise ValueError("bounds must have length of four.")
    else:
        left, top, right, bottom = value
        _ = is_valid_long_lat([left, top])
        _ = is_valid_long_lat([right, bottom])
        if not (left <= right and top <= bottom):
            raise ValueError("invalid bounding box.")
    return value


def is_sorted_by_capacity(value: list):
    sorted_val = sorted(value, key=lambda country: -country.capacity_mw)
    if value != sorted_val:
        raise ValueError(
            f"must be sorted by the capacity.\n"
            f"Output = {value}\nExpected Output = {sorted_val}"
        )
    return value


def is_percentage_string(value):
    if value == "N/A":
        return value
    _ = float(value.rstrip("%"))
    return value
