
import copy as _copy
import math as _math
import numpy as _np
import mathphys as _mp
import pyaccel.lattice as _lattice
import pyaccel.tracking as _tracking
from pyaccel.utils import interactive as _interactive


class OpticsException(Exception):
    pass


class Twiss:
    def __init__(self):
        self.spos = None
        self.corx, self.copx  = 0, 0
        self.cory, self.copy  = 0, 0
        self.code, self.codl  = 0, 0
        self.etax, self.etaxl = 0, 0
        self.etay, self.etayl = 0, 0
        self.mux, self.betax, self.alphax = 0, None, None
        self.muy, self.betay, self.alphay = 0, None, None

    def __str__(self):
        r = ''
        r += 'spos      : ' + '{0:+10.3e}'.format(self.spos) + '\n'
        r += 'corx,copx : ' + '{0:+10.3e}, {1:+10.3e}'.format(self.corx, self.copx) + '\n'
        r += 'cory,copy : ' + '{0:+10.3e}, {1:+10.3e}'.format(self.cory, self.copy) + '\n'
        r += 'code,codl : ' + '{0:+10.3e}, {1:+10.3e}'.format(self.code, self.codl) + '\n'
        r += 'mux       : ' + '{0:+10.3e}'.format(self.mux) + '\n'
        r += 'betax     : ' + '{0:+10.3e}'.format(self.betax) + '\n'
        r += 'alphax    : ' + '{0:+10.3e}'.format(self.alphax) + '\n'
        r += 'etax      : ' + '{0:+10.3e}'.format(self.etax) + '\n'
        r += 'etaxl     : ' + '{0:+10.3e}'.format(self.etaxl) + '\n'
        r += 'muy       : ' + '{0:+10.3e}'.format(self.muy) + '\n'
        r += 'betay     : ' + '{0:+10.3e}'.format(self.betay) + '\n'
        r += 'alphay    : ' + '{0:+10.3e}'.format(self.alphay) + '\n'
        r += 'etay      : ' + '{0:+10.3e}'.format(self.etay) + '\n'
        r += 'etayl     : ' + '{0:+10.3e}'.format(self.etayl) + '\n'
        return r


@_interactive
def gettwiss(twiss_list, attribute_list):
    """Build a matrix with Twiss data from a list of Twiss objects.

    Accepts a list of Twiss objects and returns a matrix with Twiss data, one line for
    each Twiss parameter defined in 'attributes_list'.

    Keyword arguments:
    twiss_list -- List with Twiss objects
    attributes_list -- List of strings with Twiss attributes to be stored in twiss matrix

    Returns:
    m -- Matrix with Twiss data. Can also be thought of a single column of
         Twiss parameter vectors:
            betax, betay = gettwiss(twiss, ('betax','betay'))
    """
    values = _np.zeros((len(attribute_list),len(twiss_list)))
    for i in range(len(twiss_list)):
        for j in range(len(attribute_list)):
            values[j,i] = getattr(twiss_list[i], attribute_list[j])
    return values


@_interactive
def calctwiss(
        accelerator=None,
        indices=None,
        closed_orbit=None,
        twiss_in=None):
    """Return Twiss parameters of uncoupled dynamics."""

    ''' process arguments '''
    if indices is None:
        indices = range(len(accelerator))

    try:
        indices[0]
    except:
        indices = [indices]

    if closed_orbit is None:
        closed_orbit = _tracking.findorbit6(accelerator=accelerator, indices='open', fixed_point_guess=None)

    m66, transfer_matrices, *_ = _tracking.findm66(accelerator = accelerator, closed_orbit = closed_orbit)

    ''' calcs twiss at first element '''
    mx, my = m66[0:2,0:2], m66[2:4,2:4] # decoupled transfer matrices
    sin_nux = _math.copysign(1,mx[0,1]) * _math.sqrt(-mx[0,1] * mx[1,0] - ((mx[0,0] - mx[1,1])**2)/4);
    sin_nuy = _math.copysign(1,my[0,1]) * _math.sqrt(-my[0,1] * my[1,0] - ((my[0,0] - my[1,1])**2)/4);

    fp = closed_orbit[:,0]
    t = Twiss()
    t.spos = 0
    t.corx, t.copx = fp[0], fp[1]
    t.cory, t.copy = fp[2], fp[3]
    t.code, t.codl = fp[4], fp[5]
    t.alphax = (mx[0,0] - mx[1,1]) / 2 / sin_nux
    t.betax  = mx[0,1] / sin_nux
    t.alphay = (my[0,0] - my[1,1]) / 2 / sin_nuy
    t.betay  = my[0,1] / sin_nuy
    ''' dispersion function based on eta = (1 - M)^(-1) D'''
    Dx = _np.array([[m66[0,4]],[m66[1,4]]])
    Dy = _np.array([[m66[2,4]],[m66[3,4]]])
    t.etax = _np.linalg.solve(_np.eye(2,2) - mx, Dx)
    t.etay = _np.linalg.solve(_np.eye(2,2) - my, Dy)

    if 0 in indices:
        tw = [t]
    else:
        tw = []

    ''' propagates twiss through line '''
    m_previous = _np.eye(6,6)
    for i in range(1, len(accelerator)):
        m = transfer_matrices[i-1]
        mx, my = m[0:2,0:2], m[2:4,2:4] # decoupled transfer matrices
        Dx = _np.array([[m[0,4]],[m[1,4]]])
        Dy = _np.array([[m[2,4]],[m[3,4]]])
        n = Twiss()
        n.spos   = t.spos + accelerator[i-1].length
        n.betax  =  ((mx[0,0] * t.betax - mx[0,1] * t.alphax)**2 + mx[0,1]**2) / t.betax
        n.alphax = -((mx[0,0] * t.betax - mx[0,1] * t.alphax) * (mx[1,0] * t.betax - mx[1,1] * t.alphax) + mx[0,1] * mx[1,1]) / t.betax
        n.betay  =  ((my[0,0] * t.betay - my[0,1] * t.alphay)**2 + my[0,1]**2) / t.betay
        n.alphay = -((my[0,0] * t.betay - my[0,1] * t.alphay) * (my[1,0] * t.betay - my[1,1] * t.alphay) + my[0,1] * my[1,1]) / t.betay
        ''' calcs phase advance based on R(mu) = U(2) M(2|1) U^-1(1) '''
        n.mux    = t.mux + _math.asin(mx[0,1]/_math.sqrt(n.betax * t.betax))
        n.muy    = t.muy + _math.asin(my[0,1]/_math.sqrt(n.betay * t.betay))
        ''' dispersion function '''
        n.etax = Dx + _np.dot(mx, t.etax)
        n.etay = Dy + _np.dot(my, t.etay)

        if i in indices:
            tw.append(n)
        t = _copy.deepcopy(n)

    ''' converts eta format '''
    for t in tw:
        t.etaxl, t.etayl = (t.etax[1,0], t.etay[1,0])
        t.etax,  t.etay  = (t.etax[0,0], t.etay[0,0])

    return tw, m66, transfer_matrices, closed_orbit


@_interactive
def getrffrequency(accelerator):
    """Return the frequency of the first RF cavity in the lattice"""
    for e in accelerator:
        if e.frequency != 0:
            return e.frequency
    else:
        raise OpticsException('no cavity element in the lattice')


@_interactive
def getrevolutionperiod(accelerator):
    return accelerator.length/accelerator.velocity


@_interactive
def getrevolutionfrequency(accelerator):
    return 1.0 / getrevolutionperiod(accelerator)


@_interactive
def getfractunes(accelerator, closed_orbit = None):
    m66 = _tracking.findm66(accelerator, indices = 'm66')
    trace_x = m66[0,0] + m66[1,1]
    trace_y = m66[2,2] + m66[3,3]
    trace_s = m66[4,4] + m66[5,5]
    tune_x = _math.acos(trace_x/2.0)/2.0/_math.pi
    tune_y = _math.acos(trace_y/2.0)/2.0/_math.pi
    tune_s = _math.acos(trace_s/2.0)/2.0/_math.pi
    return tune_x, tune_y, tune_s

@_interactive
def gettunes(accelerator):
    raise OpticsException('not implemented')


@_interactive
def getchromaticities(lattice):
    raise OpticsException('not implemented')


@_interactive
def getmcf(lattice):
    raise OpticsException('not implemented')


@_interactive
def getradiationintegrals(accelerator):
    raise OpticsException('not implemented')
