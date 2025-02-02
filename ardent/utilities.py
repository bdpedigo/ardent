import numpy as np

"""
Test _validate_scalar_to_multi
"""

def _validate_scalar_to_multi(value, size=3, dtype=float):
    """
    If value's length is 1, upcast it to match size. 
    Otherwise, if it does not match size, raise error.

    Return a numpy array.
    """

    # Cast size to int.
    try:
        size = int(size)
    except (TypeError, ValueError):
        raise TypeError(f"size must be interpretable as an integer.\n"
            f"type(size): {type(size)}.")
    
    if size < 0:
        raise ValueError(f"size must be non-negative.\n"
            f"size: {size}.")
    
    # Cast value to np.ndarray.
    try:
        value = np.array(value, dtype)
    except ValueError:
        raise ValueError(f"value and dtype are incompatible with one another.")

    # Validate value's dimensionality and length.
    if value.ndim == 0:
        value = np.array([value])
    if value.ndim == 1:
        if len(value) == 1:
            # Upcast scalar to match size.
            value = np.full(size, value, dtype=dtype)
        elif len(value) != size:
            # value's length is incompatible with size.
            raise ValueError(f"The length of value must either be 1 or it must match size."
                f"len(value): {len(value)}.")    
    else:
        # value.ndim > 1.
        raise ValueError(f"value must not have more than 1 dimension."
            f"value.ndim: {value.ndim}.")
    
    # TODO: verify that this is necessary and rewrite/remove accordingly.
    # Check for np.nan values.
    if np.any(np.isnan(value)):
        raise NotImplementedError("np.nan values encountered. What input led to this result?"
            "Write in an exception as appropriate.")
        raise ValueError(f"value contains inappropriate values for the chosen dtype "
            f"and thus contains np.nan values.")
            
    return value


def _validate_ndarray(array, minimum_ndim=0, required_ndim=None, dtype=None, 
forbid_object_dtype=True, broadcast_to_shape=None):
    """Cast (a copy of) array to a np.ndarray if possible and return it 
    unless it is noncompliant with minimum_ndim, required_ndim, and dtype.
    
    Note:
    
    If required_ndim is None, _validate_ndarray will accept any object.
    If it is possible to cast to dtype, otherwise an exception is raised.

    If np.array(array).ndim == 0 and required_ndim == 1, array will be upcast to ndim 1.
    
    If forbid_object_dtype == True and the dtype is object, an exception is raised 
    unless object is the dtype.
    
    If a shape is provided to broadcast_to_shape, unless noncompliance is found with 
    required_ndim, array is broadcasted to that shape."""

    # Verify arguments.

    # Verify minimum_ndim.
    if not isinstance(minimum_ndim, int):
        raise TypeError(f"minimum_ndim must be of type int."
            f"type(minimum_ndim): {type(minimum_ndim)}.")
    if minimum_ndim < 0:
        raise ValueError(f"minimum_ndim must be non-negative."
            f"minimum_ndim: {minimum_ndim}.")

    # Verify required_ndim.
    if required_ndim is not None:
        if not isinstance(required_ndim, int):
            raise TypeError(f"required_ndim must be either None or of type int."
                f"type(required_ndim): {type(required_ndim)}.")
        if required_ndim < 0:
            raise ValueError(f"required_ndim must be non-negative."
                f"required_ndim: {required_ndim}.")

    # Verify dtype.
    if dtype is not None:
        if not isinstance(dtype, type):
            raise TypeError(f"dtype must be either None or a valid type."
                f"type(dtype): {type(dtype)}.")

    # Validate array.

    # Cast array to np.ndarray.
    # Validate compliance with dtype.
    try:
        array = np.array(array, dtype) # Side effect: breaks alias.
    except TypeError:
        raise TypeError(f"array is of a type that is incompatible with dtype.\n"
            f"type(array): {type(array)}, dtype: {dtype}.")
    except ValueError:
        raise ValueError(f"array has a value that is incompatible with dtype.\n"
            f"array: {array}, \ntype(array): {type(array)}, dtype: {dtype}.")

    # Verify compliance with forbid_object_dtype.
    if forbid_object_dtype:
        if array.dtype == object and dtype != object:
            raise TypeError(f"Casting array to a np.ndarray produces an array of dtype object while forbid_object_dtype == True and dtype != object.")

    # Validate compliance with required_ndim.
    if required_ndim is not None and array.ndim != required_ndim:
        # Upcast from ndim 0 to ndim 1 if appropriate.
        if array.ndim == 0 and required_ndim == 1:
            array = np.array([array])
        else:
            raise ValueError(f"If required_ndim is not None, array.ndim must equal it unless array.ndim == 0 and required_ndin == 1.\n"
                f"array.ndim: {array.ndim}, required_ndim: {required_ndim}.")

    # Verify compliance with minimum_ndim.
    if array.ndim < minimum_ndim:
        raise ValueError(f"array.ndim must be at least equal to minimum_ndim."
            f"array.ndim: {array.ndim}, minimum_ndim: {minimum_ndim}.")
    
    # Broadcast array if appropriate.
    if broadcast_to_shape is not None:
        array = np.copy(np.broadcast_to(array=array, shape=broadcast_to_shape))

    return array

