
import math as _math
from collections.abc import Iterable
from copy import deepcopy as _dcopy
import numpy as _numpy
import mathphys as _mp
import trackcpp as _trackcpp
import pyaccel as _pyaccel
from pyaccel.utils import interactive as _interactive


class LatticeError(Exception):
    pass


@_interactive
def flatten(elist):
    """Take a list-of-list-of-... elements and flattens it:
            a simple list of elements"""
    flat_elist = []
    for element in elist:
        if isinstance(element, Iterable) and not isinstance(element, str):
            flat_elist.extend(flatten(element))
        else:
            flat_elist.append(element)
    return flat_elist


@_interactive
def build(elist):
    """Build lattice from a list of elements and lines"""
    lattice = _trackcpp.CppElementVector()
    elist = flatten(elist)
    for e in elist:
        lattice.append(e._e)
    return lattice


@_interactive
def shift(lattice, start):
    """Shift periodically the lattice so that it starts at element whose index
    is 'start'.

    Keyword arguments:
    lattice -- a list of objects
    start -- index of first element in new list

    Returns an Accelerator.
    """
    new_lattice = lattice[start:]
    for i in range(start):
        new_lattice.append(lattice[i])
    return new_lattice


@_interactive
def length(lattice):
    return sum(map(lambda x: x.length, lattice))


@_interactive
def find_spos(lattice, indices='open'):
    """Return longitudinal position at the entrance of lattice elements.

    Keyword arguments:
    lattice -- accelerator model.
    indices -- may be a string 'closed' or 'open' to return or not the position
        at the end of the last element, or a list or tuple to select some
        indices or even an integer (default: 'open')
    """
    leng = [0] + [e.length for e in lattice]
    pos = _numpy.cumsum(leng)

    if isinstance(indices, str):
        if indices.lower() == 'open':
            return pos[:-1]
        elif indices.lower() == 'closed':
            return pos
        else:
            raise TypeError('indices string not supported')
    elif isinstance(indices, (int, _numpy.ndarray, list)):
        return pos[indices]
    elif isinstance(indices, tuple):
        return pos[list(indices)]
    else:
        raise TypeError('indices type not supported')


@_interactive
def find_indices(lattice, attribute_name, value, comparison=None):
    """Return a list with indices (i) of elements that match a given criteria.

    Keyword arguments:
    lattice: accelerator model.
    attribute_name: string identifying the attribute to match
    value: any data type or collection data type
    comparison: function which takes two arguments, the value of the attribute
        and value, performs a comparison between then and returns a boolean
        (default: __eq__)

    Returns list of indices where the comparison returns True.

    EXAMPLES:
      >> mia_idx = find_indices(lattice,'fam_name',value='mia')
      >> idx = find_indices(lattice,'polynom_b',value=[0.0,1.5,0.0])
      >> fun = lambda x,y: x[2] != y
      >> sext_idx = find_indices(lattice,'polynom_b',value=0.0,comparison=fun)
      >> fun2=lambda x,y: x.startswith(y)
      >> mi_idx = find_indices(lattice,'fam_name',value='mi',comparison=fun2)
    """

    if comparison is None:
        comparison = _is_equal
    indices = []
    for i, ele in enumerate(lattice):
        attrib = getattr(ele, attribute_name)
        if comparison(attrib, value):
            indices.append(i)
    return indices


@_interactive
def get_attribute(lattice, attribute_name, indices=None, m=None, n=None):
    """Return a list with requested lattice data"""
    if indices is None:
        indices = range(len(lattice))

    indices, values, isflat = _process_args_errors(indices, 0.0)

    if (m is not None) and (n is not None):
        for i, segs in enumerate(indices):
            for j, seg in enumerate(segs):
                tdata = getattr(lattice[seg], attribute_name)
                values[i][j] = tdata[m][n]
    elif (m is not None) and (n is None):
        for i, segs in enumerate(indices):
            for j, seg in enumerate(segs):
                tdata = getattr(lattice[seg], attribute_name)
                values[i][j] = tdata[m]
    else:
        for i, segs in enumerate(indices):
            for j, seg in enumerate(segs):
                tdata = getattr(lattice[seg], attribute_name)
                values[i][j] = tdata

    return _process_output(values, isflat)


@_interactive
def set_attribute(lattice, attribute_name, indices, values, m=None, n=None):
    """Set elements data."""

    indices, values, _ = _process_args_errors(indices, values)

    if (m is not None) and (n is not None):
        for segs, vals in zip(indices, values):
            for seg, val in zip(segs, vals):
                tdata = getattr(lattice[seg], attribute_name)
                tdata[m][n] = val
    elif (m is not None) and (n is None):
        for segs, vals in zip(indices, values):
            for seg, val in zip(segs, val):
                tdata = getattr(lattice[seg], attribute_name)
                tdata[m] = val
    else:
        for segs, vals in zip(indices, values):
            for seg, val in zip(segs, vals):
                setattr(lattice[seg], attribute_name, val)


@_interactive
def find_dict(lattice, attribute_name):
    """Return a dict which correlates values of 'attribute_name' and a list of
    indices corresponding to matching elements
    """
    latt_dict = {}
    for i, ele in enumerate(lattice):
        if hasattr(ele, attribute_name):
            att_value = getattr(ele, attribute_name)
            if att_value in latt_dict:
                latt_dict[att_value].append(i)
            else:
                latt_dict[att_value] = [i]
    return latt_dict


@_interactive
def set_knob(lattice, fam_name, attribute_name, value):

    if isinstance(fam_name, str):
        idx = find_indices(lattice, 'fam_name', fam_name)
    else:
        idx = []
        for famname in fam_name:
            idx.append(find_indices(lattice, 'fam_name', famname))
    for i in idx:
        setattr(lattice[i], attribute_name, value)


@_interactive
def add_knob(lattice, fam_name, attribute_name, value):

    if isinstance(fam_name, str):
        idx = find_indices(lattice, 'fam_name', fam_name)
    else:
        idx = []
        for famname in fam_name:
            idx.append(find_indices(lattice, 'fam_name', famname))
    for i in idx:
        original_value = getattr(lattice[i], attribute_name)
        new_value = original_value + value
        setattr(lattice[i], attribute_name, new_value)


@_interactive
def read_flat_file(filename):
    e = _mp.constants.electron_rest_energy*_mp.units.joule_2_eV
    a = _pyaccel.accelerator.Accelerator(energy=e)  # energy cannot be zero
    fname = _trackcpp.String(filename)
    r = _trackcpp.read_flat_file_wrapper(fname, a._accelerator, True)
    if r > 0:
        raise LatticeError(_trackcpp.string_error_messages[r])

    return a


@_interactive
def write_flat_file(accelerator, filename):
    fname = _trackcpp.String(filename)
    r = _trackcpp.write_flat_file_wrapper(
        fname, accelerator._accelerator, True)
    if r > 0:
        raise LatticeError(_trackcpp.string_error_messages[r])


@_interactive
def write_flat_file_to_string(accelerator):
    s = _trackcpp.String()
    r = _trackcpp.write_flat_file_wrapper(s, accelerator._accelerator, False)
    if r > 0:
        raise LatticeError(_trackcpp.string_error_messages[r])

    return s.data


@_interactive
def refine_lattice(accelerator, max_length=None, indices=None, fam_names=None,
                   pass_methods=None):

    if max_length is None:
        max_length = 0.05

    acc = accelerator

    # Build list with indices of elements to be affected
    if indices is None:
        indices = []
        # Add specified fam_names
        if fam_names is not None:
            for fam_name in fam_names:
                indices.extend(find_indices(acc, 'fam_name', fam_name))
        # Add specified pass_methods
        if pass_methods is not None:
            for pass_method in pass_methods:
                indices.extend(find_indices(acc, 'pass_method', pass_method))
        if fam_names is None and pass_methods is None:
            indices = list(range(len(acc)))

    new_acc = _pyaccel.accelerator.Accelerator(
        energy=acc.energy,
        harmonic_number=acc.harmonic_number,
        cavity_on=acc.cavity_on,
        radiation_on=acc.radiation_on,
        vchamber_on=acc.vchamber_on)

    indices = set(indices)
    for i, ele in enumerate(acc):
        if i not in indices or ele.length <= max_length:
            e = _pyaccel.elements.Element(ele)
            new_acc.append(e)
            continue

        nr_segs = 1+int(ele.length/max_length)
        if any((ele.angle_in, ele.angle_out, ele.fint_in, ele.fint_out)):
            # for dipoles (special case due to fringe fields)
            nr_segs = max(3, nr_segs)

            e = _pyaccel.elements.Element(ele)
            e.angle_in = 0.0
            e.angle_out = 0.0
            e.fint_in = 0.0
            e.fint_out = 0.0

            e_in = _pyaccel.elements.Element(ele)
            e_in.angle_out = 0.0
            e_in.fint_out = 0.0

            e_out = _pyaccel.elements.Element(ele)
            e_out.angle_in = 0.0
            e_out.fint_in = 0.0

            e_in.length, e.length, e_out.length = 3*(ele.length/nr_segs,)
            e_in.angle, e.angle, e_out.angle = 3*(ele.angle/nr_segs,)

            new_acc.append(e_in)
            for _ in range(nr_segs-2):
                new_acc.append(
                    _pyaccel.elements.Element(e))
            new_acc.append(e_out)
        elif ele.kicktable is not None:
            raise Exception('no refinement implemented for IDs yet')
        else:
            for _ in range(nr_segs):
                e = _pyaccel.elements.Element(ele)
                e.length = ele.length / nr_segs
                e.angle = ele.angle / nr_segs
                new_acc.append(e)
    return new_acc


@_interactive
def get_error_misalignment_x(lattice, indices):
    """Get horizontal misalignment errors from lattice elements.

    INPUTS:
      lattice : accelerator model
      indices : (list, tuple, numpy.ndarray) of the indices of elements to
        appy the errros. If the elements are segmented in the model
        and the same error is to be applied to each segment, then it must be
        a (nested list,nested tuple, 2D numpy.ndarray), where each of its
        (elements, elements, first dimension) is a (list/tuple, tuple/list, 1D
        numpy.ndarray) of indices of the segments. Elements may have different
        number of segments.

    Outputs:
       list of floats, in case len(indices)>1, or float of errors. Unit: [m]
    """

    # processes arguments
    indices, _, isflat = _process_args_errors(indices, 0.0)

    # loops over elements and gets error from T_IN
    values = []
    for segs in indices:
        # it is possible to also have yaw errors,so:
        misx = -(lattice[segs[0]].t_in[0] - lattice[segs[-1]].t_out[0])/2
        values.append(len(segs)*[misx])

    return _process_output(values, isflat)


@_interactive
def set_error_misalignment_x(lattice, indices, values):
    """Set (discard previous) horizontal misalignments errors to lattice elements.

    INPUTS:
      lattice : accelerator model
      indices : (list, tuple, numpy.ndarray) of the indices of elements to
        appy the errros. If the elements are segmented in the model
        and the same error is to be applied to each segment, then it must be
        a (nested list,nested tuple, 2D numpy.ndarray), where each of its
        (elements, elements, first dimension) is a (list/tuple, tuple/list, 1D
        numpy.ndarray) of indices of the segments. Elements may have different
        number of segments.
      values : may be a float or a (list, tuple, 1D numpy.ndarray) of floats
        with the same length as indices. Unit [meters]
    """

    ''' processes arguments '''
    indices, values, _ = _process_args_errors(indices, values)

    # loops over elements and sets its T1 and T2 fields
    for segs, vals in zip(indices, values):
        # it is possible to also have yaw errors, so:
        yaw = (lattice[segs[0]].t_in[0] + lattice[segs[-1]].t_out[0])/2
        for idx, val in zip(segs, vals):
            lattice[idx].t_in[0] = yaw - val
            lattice[idx].t_out[0] = yaw + val


@_interactive
def add_error_misalignment_x(lattice, indices, values):
    """Add (sum to previous) horizontal misalignment errors to lattice.

    INPUTS:
      lattice : accelerator model
      indices : (list, tuple, numpy.ndarray) of the indices of elements to
        appy the errros. If the elements are segmented in the model
        and the same error is to be applied to each segment, then it must be
        a (nested list,nested tuple, 2D numpy.ndarray), where each of its
        (elements, elements, first dimension) is a (list/tuple, tuple/list, 1D
        numpy.ndarray) of indices of the segments. Elements may have different
        number of segments.
      values : may be a float or a (list, tuple, 1D numpy.ndarray) of floats
        with the same length as indices. Unit: [meters]
    """

    # processes arguments
    indices, values, _ = _process_args_errors(indices, values)

    # loops over elements and sets its T1 and T2 fields
    for segs, vals in zip(indices, values):
        for idx, val in zip(segs, vals):
            lattice[idx].t_in[0] += -val
            lattice[idx].t_out[0] += val


@_interactive
def get_error_misalignment_y(lattice, indices):
    """Get vertical misalignment errors from lattice elements.

    INPUTS:
      lattice : accelerator model
      indices : (list, tuple, numpy.ndarray) of the indices of elements to
        appy the errros. If the elements are segmented in the model
        and the same error is to be applied to each segment, then it must be
        a (nested list,nested tuple, 2D numpy.ndarray), where each of its
        (elements, elements, first dimension) is a (list/tuple, tuple/list, 1D
        numpy.ndarray) of indices of the segments. Elements may have different
        number of segments.

    Outputs:
       list, in case len(indices)>1, or float of errors. Unit: [meters]
    """

    # processes arguments
    indices, _, isflat = _process_args_errors(indices, 0.0)

    # loops over elements and gets error from T_IN
    values = []
    for segs in indices:
        # it is possible to also have pitch errors,so:
        misy = -(lattice[segs[0]].t_in[2] - lattice[segs[-1]].t_out[2])/2
        values.append(len(segs)*[misy])
    return _process_output(values, isflat)


@_interactive
def set_error_misalignment_y(lattice, indices, values):
    """Set (discard previous) vertical misalignments errors to lattice elements.

    INPUTS:
      lattice : accelerator model
      indices : (list, tuple, numpy.ndarray) of the indices of elements to
        appy the errros. If the elements are segmented in the model
        and the same error is to be applied to each segment, then it must be
        a (nested list,nested tuple, 2D numpy.ndarray), where each of its
        (elements, elements, first dimension) is a (list/tuple, tuple/list, 1D
        numpy.ndarray) of indices of the segments. Elements may have different
        number of segments.
      values : may be a float or a (list, tuple, 1D numpy.ndarray) of floats
        with the same length as indices. Unit [meters].
    """

    # processes arguments
    indices, values, _ = _process_args_errors(indices, values)

    # loops over elements and sets its T1 and T2 fields
    for segs, vals in zip(indices, values):
        # it is possible to also have yaw errors, so:
        pitch = (lattice[segs[0]].t_in[2] + lattice[segs[-1]].t_out[2])/2
        for idx, val in zip(segs, vals):
            lattice[idx].t_in[2] = pitch - val
            lattice[idx].t_out[2] = pitch + val


@_interactive
def add_error_misalignment_y(lattice, indices, values):
    """Add (sum to previous) vertical misalignment errors to lattice.

    INPUTS:
      lattice : accelerator model
      indices : (list, tuple, numpy.ndarray) of the indices of elements to
        appy the errros. If the elements are segmented in the model
        and the same error is to be applied to each segment, then it must be
        a (nested list,nested tuple, 2D numpy.ndarray), where each of its
        (elements, elements, first dimension) is a (list/tuple, tuple/list, 1D
        numpy.ndarray) of indices of the segments. Elements may have different
        number of segments.
      values : may be a float or a (list, tuple, 1D numpy.ndarray) of floats
        with the same length as indices. Unit: [meters]
    """

    # processes arguments
    indices, values, _ = _process_args_errors(indices, values)

    # loops over elements and sets its T1 and T2 fields
    for segs, vals in zip(indices, values):
        for idx, val in zip(segs, vals):
            lattice[idx].t_in[2] += -val
            lattice[idx].t_out[2] += val


@_interactive
def get_error_rotation_roll(lattice, indices):
    """Get roll rotation errors from lattice elements.

    INPUTS:
      lattice : accelerator model
      indices : (list, tuple, numpy.ndarray) of the indices of elements to
        appy the errros. If the elements are segmented in the model
        and the same error is to be applied to each segment, then it must be
        a (nested list,nested tuple, 2D numpy.ndarray), where each of its
        (elements, elements, first dimension) is a (list/tuple, tuple/list, 1D
        numpy.ndarray) of indices of the segments. Elements may have different
        number of segments.

    Outputs:
       list, in case len(indices)>1, or float of roll errors. Unit: [rad]
    """

    #  processes arguments
    indices, _, isflat = _process_args_errors(indices, 0.0)

    # loops over elements and gets error from R_IN
    values = []
    for segs in indices:
        angle = _math.asin(lattice[segs[0]].r_in[0, 2])
        values.append(len(segs) * [angle])
    return _process_output(values, isflat)


@_interactive
def set_error_rotation_roll(lattice, indices, values):
    """Set (discard previous) roll rotation errors to lattice elements.

    INPUTS:
      lattice : accelerator model
      indices : (list, tuple, numpy.ndarray) of the indices of elements to
        appy the errros. If the elements are segmented in the model
        and the same error is to be applied to each segment, then it must be
        a (nested list,nested tuple, 2D numpy.ndarray), where each of its
        (elements, elements, first dimension) is a (list/tuple, tuple/list, 1D
        numpy.ndarray) of indices of the segments. Elements may have different
        number of segments.
      values : may be a float or a (list, tuple, 1D numpy.ndarray) of floats
        with the same length as indices. Unit [rad].
    """

    # processes arguments
    indices, values, _ = _process_args_errors(indices, values)

    # loops over elements and sets its R1 and R2 fields
    for segs, val in zip(indices, values):
        cos, sin = _math.cos(val[0]), _math.sin(val[0])
        rot = _numpy.diag([cos, cos, cos, cos, 1.0, 1.0])
        rot[0, 2], rot[1, 3], rot[2, 0], rot[3, 1] = sin, sin, -sin, -sin
        for idx in segs:
            ele = lattice[idx]
            if ele.angle != 0 and ele.length != 0:
                rho = ele.length / ele.angle
                orig_s = ele.polynom_a[0] * rho
                # look at bndpolysymplectic4pass:
                orig_c = ele.polynom_b[0] * rho + 1.0
                # sin(teta)/rho:
                ele.polynom_a[0] = (orig_s*cos + orig_c*sin)/rho
                # (cos(teta)-1)/rho:
                ele.polynom_b[0] = (orig_c*cos - orig_s*sin - 1.0)/rho
            else:
                ele.r_in = rot
                ele.r_out = rot.T


@_interactive
def add_error_rotation_roll(lattice, indices, values):
    """Add (sum to previous) roll rotation errors to lattice.

    INPUTS:
      lattice : accelerator model
      indices : (list, tuple, numpy.ndarray) of the indices of elements to
        appy the errros. If the elements are segmented in the model
        and the same error is to be applied to each segment, then it must be
        a (nested list,nested tuple, 2D numpy.ndarray), where each of its
        (elements, elements, first dimension) is a (list/tuple, tuple/list, 1D
        numpy.ndarray) of indices of the segments. Elements may have different
        number of segments.
      values : may be a float or a (list, tuple, 1D numpy.ndarray) of floats
        with the same length as indices. Unit: [rad]
    """

    # processes arguments
    indices, values, _ = _process_args_errors(indices, values)

    # loops over elements and sets its R1 and R2 fields
    for segs, val in zip(indices, values):
        cos, sin = _math.cos(val[0]), _math.sin(val[0])
        rot = _numpy.diag([cos, cos, cos, cos, 1.0, 1.0])
        rot[0, 2], rot[1, 3], rot[2, 0], rot[3, 1] = sin, sin, -sin, -sin

        for idx in segs:
            ele = lattice[idx]
            if ele.angle != 0 and ele.length != 0:
                rho = ele.length / ele.angle
                orig_s = ele.polynom_a[0] * rho
                # look at bndpolysymplectic4pass:
                orig_c = ele.polynom_b[0] * rho + 1.0
                # sin(teta)/rho:
                ele.polynom_a[0] = (orig_s*cos + orig_c*sin) / rho
                # (cos(teta)-1)/rho:
                ele.polynom_b[0] = (orig_c*cos - orig_s*sin - 1.0) / rho
            else:
                ele.r_in = _numpy.dot(rot, ele.r_in)
                ele.r_out = _numpy.dot(ele.r_out, rot.T)


@_interactive
def get_error_rotation_pitch(lattice, indices):
    """Get pitch rotation errors of lattice elements

    INPUTS:
      lattice : accelerator model
      indices : (list, tuple, numpy.ndarray) of the indices of elements to
        appy the errros. If the elements are segmented in the model
        and the same error is to be applied to each segment, then it must be
        a (nested list,nested tuple, 2D numpy.ndarray), where each of its
        (elements, elements, first dimension) is a (list/tuple, tuple/list, 1D
        numpy.ndarray) of indices of the segments. Elements may have different
        number of segments.

    Outputs:
       list, in case len(indices)>1, or float of pitch errors. Unit: [rad]
    """

    # processes arguments
    indices, _, isflat = _process_args_errors(indices, 0.0)

    # loops over elements and gets error from T_IN
    values = []
    for segs in indices:
        ang = lattice[segs[0]].t_in[3]
        values.append(len(segs)*[-ang])

    return _process_output(values, isflat)


@_interactive
def set_error_rotation_pitch(lattice, indices, values):
    """Set (discard previous) pitch rotation errors to lattice.

    INPUTS:
      lattice : accelerator model
      indices : (list, tuple, numpy.ndarray) of the indices of elements to
        appy the errros. If the elements are segmented in the model
        and the same error is to be applied to each segment, then it must be
        a (nested list,nested tuple, 2D numpy.ndarray), where each of its
        (elements, elements, first dimension) is a (list/tuple, tuple/list, 1D
        numpy.ndarray) of indices of the segments. Elements may have different
        number of segments.
      values : may be a float or a (list, tuple, 1D numpy.ndarray) of floats
        with the same length as indices. Unit [rad]
    """

    # processes arguments
    indices, values, _ = _process_args_errors(indices, values)

    # set new values to first T1 and last T2
    for segs, ang in zip(indices, values):
        angy = -ang[0]
        L = sum([lattice[ii].length for ii in segs])
        # It is possible that there is a misalignment error, so:
        misy = (lattice[segs[0]].t_in[2] - lattice[segs[-1]].t_out[2])/2

        # correction of the path length
        old_angx = lattice[segs[0]].t_in[1]
        path = -(L/2)*(angy*angy + old_angx*old_angx)

        # Apply the errors only to the entrance of the first and exit of the
        # last segment:
        lattice[segs[0]].t_in[2] = -(L/2)*angy + misy
        lattice[segs[-1]].t_out[2] = -(L/2)*angy - misy
        lattice[segs[0]].t_in[3] = angy
        lattice[segs[-1]].t_out[3] = -angy
        lattice[segs[-1]].t_out[5] = path


@_interactive
def add_error_rotation_pitch(lattice, indices, values):
    """Add (sum to previous) pitch rotation errors to lattice.

    INPUTS:
      lattice : accelerator model
      indices : (list, tuple, numpy.ndarray) of the indices of elements to
        appy the errros. If the elements are segmented in the model
        and the same error is to be applied to each segment, then it must be
        a (nested list,nested tuple, 2D numpy.ndarray), where each of its
        (elements, elements, first dimension) is a (list/tuple, tuple/list, 1D
        numpy.ndarray) of indices of the segments. Elements may have different
        number of segments.
      values : may be a float or a (list, tuple, 1D numpy.ndarray) of floats
        with the same length as indices. Unit [rad]
    """

    # processes arguments
    indices, values, _ = _process_args_errors(indices, values)

    # set new values to first T1 and last T2. Uses small angle approximation
    for segs, ang in zip(indices, values):
        angy = -ang[0]
        L = sum([lattice[ii].length for ii in segs])

        # correction of the path length
        old_angy = lattice[segs[0]].t_in[3]
        path = -(L/2)*((angy+old_angy)*(angy+old_angy) - old_angy*old_angy)

        # Apply the errors only to the entrance of the first and exit of the
        # last segment:
        lattice[segs[0]].t_in += _numpy.array([0, 0, -(L/2)*angy, angy, 0, 0])
        lattice[segs[-1]].t_out += _numpy.array(
            [0, 0, -(L/2)*angy, -angy, 0, path])


@_interactive
def get_error_rotation_yaw(lattice, indices):
    """Get yaw rotation errors of lattice elements.

    INPUTS:
      lattice : accelerator model
      indices : (list, tuple, numpy.ndarray) of the indices of elements to
        appy the errros. If the elements are segmented in the model
        and the same error is to be applied to each segment, then it must be
        a (nested list,nested tuple, 2D numpy.ndarray), where each of its
        (elements, elements, first dimension) is a (list/tuple, tuple/list, 1D
        numpy.ndarray) of indices of the segments. Elements may have different
        number of segments.

    Outputs:
       list, in case len(indices)>1, or float of yaw errors. Unit: [rad]
    """

    # processes arguments
    indices, _, isflat = _process_args_errors(indices, 0.0)

    # loops over elements and gets error from T_IN
    values = []
    for segs in indices:
        ang = lattice[segs[0]].t_in[1]
        values.append(len(segs)*[-ang])
    return _process_output(values, isflat)


@_interactive
def set_error_rotation_yaw(lattice, indices, values):
    """Set (discard previous) yaw rotation errors to lattice.

    INPUTS:
      lattice : accelerator model
      indices : (list, tuple, numpy.ndarray) of the indices of elements to
        appy the errros. If the elements are segmented in the model
        and the same error is to be applied to each segment, then it must be
        a (nested list,nested tuple, 2D numpy.ndarray), where each of its
        (elements, elements, first dimension) is a (list/tuple, tuple/list, 1D
        numpy.ndarray) of indices of the segments. Elements may have different
        number of segments.
      values : may be a float or a (list, tuple, 1D numpy.ndarray) of floats
        with the same length as indices. Unit [rad]
    """
    # processes arguments
    indices, values, _ = _process_args_errors(indices, values)

    # set new values to first T1 and last T2
    for segs, ang in zip(indices, values):
        angx = -ang[0]
        L = sum([lattice[ii].length for ii in segs])
        # It is possible that there is a misalignment error, so:
        misx = (lattice[segs[0]].t_in[0] - lattice[segs[-1]].t_out[0])/2

        # correction of the path length
        old_angy = lattice[segs[0]].t_in[3]
        path = -(L/2)*(angx*angx + old_angy*old_angy)

        # Apply the errors only to the entrance of the first and exit of the
        # last segment:
        lattice[segs[0]].t_in[0] = -(L/2)*angx+misx
        lattice[segs[-1]].t_out[0] = -(L/2)*angx-misx
        lattice[segs[0]].t_in[1] = angx
        lattice[segs[-1]].t_out[1] = -angx
        lattice[segs[-1]].t_out[5] = path


@_interactive
def add_error_rotation_yaw(lattice, indices, values):
    """Add (sum to previous) yaw rotation errors to lattice elements.

    INPUTS:
      lattice : accelerator model
      indices : (list, tuple, numpy.ndarray) of the indices of elements to
        appy the errros. If the elements are segmented in the model
        and the same error is to be applied to each segment, then it must be
        a (nested list,nested tuple, 2D numpy.ndarray), where each of its
        (elements, elements, first dimension) is a (list/tuple, tuple/list, 1D
        numpy.ndarray) of indices of the segments. Elements may have different
        number of segments.
      values : may be a float or a (list, tuple, 1D numpy.ndarray) of floats
        with the same length as indices. Unit: [rad]
    """

    # processes arguments
    indices, values, _ = _process_args_errors(indices, values)

    # set new values to first T1 and last T2. Uses small angle approximation
    for segs, ang in zip(indices, values):
        angx = -ang[0]
        L = sum([lattice[ii].length for ii in segs])

        # correction of the path length
        old_angx = lattice[segs[0]].t_in[1]
        path = -(L/2)*((angx+old_angx)*(angx+old_angx) - old_angx*old_angx)

        # Apply the errors only to the entrance of the first and exit of the
        # last segment:
        lattice[segs[0]].t_in += _numpy.array([-(L/2)*angx, angx, 0, 0, 0, 0])
        lattice[segs[-1]].t_out += _numpy.array(
            [-(L/2)*angx, -angx, 0, 0, 0, path])


@_interactive
def add_error_excitation_main(lattice, indices, values):
    """ Add excitation errors to magnets.

    INPUTS:
      lattice : accelerator model
      indices : (list, tuple, numpy.ndarray) of the indices of elements to
        appy the errros. If the elements are segmented in the model
        and the same error is to be applied to each segment, then it must be
        a (nested list,nested tuple, 2D numpy.ndarray), where each of its
        (elements, elements, first dimension) is a (list/tuple, tuple/list, 1D
        numpy.ndarray) of indices of the segments. Elements may have different
        number of segments.
      values : may be a float or a (list, tuple, 1D numpy.ndarray) of floats
        with the same length as indices. Unit: Relative value
    """
    # processes arguments
    indices, values, _ = _process_args_errors(indices, values)

    for segs, errors in zip(indices, values):
        for idx, error in zip(segs, errors):
            ele = lattice[idx]
            if ele.angle != 0:
                rho = ele.length / ele.angle
                # read dipole pass method!
                ele.polynom_b[0] += error/rho
                # ele.polynom_a[1:] *= 1 + error
                # ele.polynom_b[1:] *= 1 + error
            else:
                ele.hkick *= 1 + error
                ele.vkick *= 1 + error
                ele.polynom_a *= 1 + error
                ele.polynom_b *= 1 + error


@_interactive
def add_error_excitation_kdip(lattice, indices, values):
    """ Add excitation errors to the quadrupole component of dipoles.

    INPUTS:
      lattice : accelerator model
      indices : (list, tuple, numpy.ndarray) of the indices of elements to
        appy the errros. If the elements are segmented in the model
        and the same error is to be applied to each segment, then it must be
        a (nested list,nested tuple, 2D numpy.ndarray), where each of its
        (elements, elements, first dimension) is a (list/tuple, tuple/list, 1D
        numpy.ndarray) of indices of the segments. Elements may have different
        number of segments.
      values : may be a float or a (list, tuple, 1D numpy.ndarray) of floats
        with the same length as indices.
    """
    # processes arguments
    indices, values, _ = _process_args_errors(indices, values)

    for segs, errors in zip(indices, values):
        for idx, error in zip(segs, errors):
            ele = lattice[idx]
            if ele.angle == 0:
                raise TypeError(
                    'lattice[{0:d}] is not a Bending Magnet.'.format(idx))
            ele.polynom_b[1] *= 1 + error


@_interactive
def add_error_multipoles(lattice, indices, r0, main_monom, Bn_norm=None,
                         An_norm=None):
    """ Add multipole errors to elements of lattice.

    INPUTS:
      lattice : accelerator model
      indices : (list, tuple, numpy.ndarray) of the indices of elements to
        appy the multipole errros. If the elements are segmented in the model
        and the same errors are to be applied to each segment, then it must be
        a (nested list,nested tuple, 2D numpy.ndarray), where each of its
        (elements, elements, first dimension) is a (list/tuple, tuple/list, 1D
        numpy.ndarray) of indices of the segments. Elements may have different
        number of segments.
      r0      : float whose meaning is the transverse horizontal position where
        the multipoles are normalized. Unit [meters];
      main_monom : may be an integer or (list, tuple, 1D numpy.ndarray) of
        integers whose meaning is the order of the main field strength
        compoment of each element. Positive values mean the main field
        component is normal and negative values mean they are skew. Examples:
          n= 1: dipole or horizontal corrector
          n=-1: vertical corrector
          n= 2: normal quadrupole
          n=-2: skew quadrupole  and so on
      Bn_norm : may be one normalized polynom to be applied to all elements or
        a list of normalized polynoms, one for each element. If the normalized
        polynoms for each element have the same sizes, it can also be a 2D
        numpy.ndarray where the first dimension has the same length as indices.
        By normalized polynom we mean a list, tuple or 1D numpy.ndarray whose
        (i+1)-th element is given by:
            Bn_norm[i] = DeltaB[i]/B  @ r0      with
            DeltaB[i] = PolB[i] * r0**i    and    B = Kn * r0**(n-1)
        where n is the absolute value of main_monom, Kn is the principal
        field strength component of the element and PolB is the quantity which
        will be applied to the element.
        The default value is None, which means the polynom_b of the elements
        will not be affected.
      An_norm : analogous of Bn_norm but for the polynom_a.

    """

    def add_polynom(elem, polynom, Pol_norm, n, KP):
        if Pol_norm is not None:
            if isinstance(Pol_norm, _numpy.ndarray):
                Pol = Pol_norm
            else:
                Pol = _numpy.array(Pol_norm)
            monoms = abs(n-1) - _numpy.arange(Pol.shape[0])
            r0_i = r0**monoms
            newPol = KP*r0_i*Pol
            oldPol = getattr(elem, polynom)
            lenNewPol = len(newPol)
            lenOldPol = len(oldPol)
            if lenNewPol > lenOldPol:
                pol = newPol
                pol[:lenOldPol] += oldPol
            else:
                pol = oldPol
                pol[:lenNewPol] += newPol
            setattr(elem, polynom, pol)

    indices, *_ = _process_args_errors(indices, 0.0)

    if len(main_monom) == 1:
        main_monom *= _numpy.ones(len(indices))
    if len(main_monom) != len(indices):
        raise IndexError(
            'Length of main_monoms differs from length of indices.')

    # Extend the fields, if necessary to the number of elements in indices
    types = (int, float, _numpy.int_, _numpy.float_)
    if Bn_norm is None or isinstance(Bn_norm[0], types):
        Bn_norm = len(indices) * [Bn_norm]
    if An_norm is None or isinstance(An_norm[0], types):
        An_norm = len(indices) * [An_norm]
    if len(Bn_norm) != len(indices) or len(An_norm) != len(indices):
        raise IndexError('Length of polynoms differs from length of indices.')

    for segs, n, ann, bnn in zip(indices, main_monom, An_norm, Bn_norm):
        for idx in segs:
            ele = lattice[idx]
            if abs(n) == 1 and ele.angle != 0:
                KP = ele.angle
                if ele.length > 0:
                    KP /= ele.length
            else:
                KP = ele.polynom_b[n-1] if n > 0 else ele.polynom_a[-n-1]
            add_polynom(ele, 'polynom_b', bnn, n, KP)
            add_polynom(ele, 'polynom_a', ann, n, KP)


def _process_args_errors(indices, values):
    types = (int, _numpy.int_)
    isflat = False
    if isinstance(indices, types):
        indices = [[indices]]
    elif len(indices) > 0 and isinstance(indices[0], types):
        indices = [[ind] for ind in indices]
        isflat = True

    types = (int, float, _numpy.int_, _numpy.float_)
    if isinstance(values, types):
        values = [len(ind) * [values] for ind in indices]
    if len(values) != len(indices):
        raise IndexError('length of values differs from length of indices.')

    newvalues = []
    for ind, vals in zip(indices, values):
        if isinstance(vals, types):
            vals = len(ind) * [vals]
        if len(vals) != len(ind):
            raise IndexError(
                'length of values differs from length of indices.')
        newvalues.append(vals)
    return indices, newvalues, isflat


def _process_output(values, isflat):
    if isflat:
        values = flatten(values)
    if len(values) == 1:
        values = values[0]
    return values


def _is_equal(a, b):
    # checks for strings
    if isinstance(a, str):
        if isinstance(b, str):
            return a == b
        else:
            return False
    else:
        if isinstance(b, str):
            return False
    try:
        a[0]
        # 'a' is an iterable
        try:
            b[0]
            # 'b' is an iterable
            if len(a) != len(b):
                # 'a' and 'b' are iterbales but with different lengths
                return False
            else:
                # 'a' and 'b' are iterables with the same length
                for a_, b_ in zip(a, b):
                    if not _is_equal(a_, b_):
                        return False
                # corresponding elements in a and b iterables are the same.
                return True
        except:
            # 'a' is iterable but 'b' is not
            return False
    except:
        # 'a' is not iterable
        try:
            b[0]
            # 'a' is not iterable but 'b' is.
            return False
        except:
            # neither 'a' nor 'b' are iterables
            return a == b
