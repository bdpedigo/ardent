import numpy as np

from ardent.utilities import _validate_ndarray

def _verify_data_is_ndarray(data):
    if not isinstance(data, np.ndarray):
        raise TypeError(f"data must be of type np.ndarray.\ntype(data): {type(data)}.")


def cast_to_typed_array(data, dtype=float):
    """Returns a copy of data cast as a np.ndarray of type dtype."""

    data = _validate_ndarray(data, dtype=dtype)


def normalize_by_MAD(data):
    """Returns a copy of <data> divided by its mean absolute deviation."""
    
    _verify_data_is_ndarray(data)

    mean_absolute_deviation = np.mean(np.abs(data - np.median(data)))

    normalized_data = data / mean_absolute_deviation

    return normalized_data


def center_to_mean(data):
    """Returns a copy of <data> subtracted by its mean."""

    _verify_data_is_ndarray(data)

    centered_data = data - np.mean(data)

    return centered_data


def pad(data, pad_width=5, mode='constant', constant_values=0):
    """Returns a padded copy of <data>."""

    _verify_data_is_ndarray(data)

    pad_kwargs = {'array':data, 'pad_width':pad_width, 'mode':mode}
    if mode == 'constant': pad_kwargs.update(constant_values=constant_values)

    padded_data = np.pad(**pad_kwargs)

    return padded_data


