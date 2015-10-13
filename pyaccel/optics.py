
import sys as _sys
import math as _math
import numpy as _np
import mathphys as _mp
import pyaccel.lattice as _lattice
import pyaccel.tracking as _tracking
import trackcpp as _trackcpp
from pyaccel.utils import interactive as _interactive

class OpticsException(Exception):
    pass

class Twiss:

    def __init__(self, **kwargs):
        if 'twiss' in kwargs:
            if isinstance(kwargs['twiss'],_trackcpp.Twiss):
                copy = kwargs.get('copy',False)
                if copy:
                    self._t = _trackcpp.Twiss(kwargs['twiss'])
                else:
                    self._t = kwargs['twiss']
            elif isinstance(kwargs['twiss'],Twiss):
                copy = kwargs.get('copy',True)
                if copy:
                    self._t = _trackcpp.Twiss(kwargs['twiss']._t)
                else:
                    self._t = kwargs['twiss']._t
            else:
                raise TypeError('twiss must be a trackcpp.Twiss or a Twiss object.')
        else:
            self._t = _trackcpp.Twiss()

    def __eq__(self,other):
        if not isinstance(other,Twiss): return NotImplemented
        for attr in self._t.__swig_getmethods__:
            self_attr = getattr(self,attr)
            if isinstance(self_attr,_np.ndarray):
                if (self_attr != getattr(other,attr)).any():
                    return False
            else:
                if self_attr != getattr(other,attr):
                    return False
        return True

    @property
    def rx(self):
        return self._t.co.rx

    @rx.setter
    def rx(self, value):
        self._t.co.rx = value

    @property
    def ry(self):
        return self._t.co.ry

    @ry.setter
    def ry(self, value):
        self._t.co.ry = value

    @property
    def px(self):
        return self._t.co.px

    @px.setter
    def px(self, value):
        self._t.co.px = value

    @property
    def py(self):
        return self._t.co.py

    @py.setter
    def py(self, value):
        self._t.co.py = value

    @property
    def de(self):
        return self._t.co.de

    @de.setter
    def de(self, value):
        self._t.co.de = value

    @property
    def dl(self):
        return self._t.co.dl

    @dl.setter
    def dl(self, value):
        self._t.co.dl = value

    @property
    def co(self):
        return _np.array([self.rx, self.px, self.ry, self.py, self.de, self.dl])

    @co.setter
    def co(self, value):
        self.rx, self.px = value[0], value[1]
        self.ry, self.py = value[2], value[3]
        self.de, self.dl = value[4], value[5]

    @property
    def betax(self):
        return self._t.betax

    @betax.setter
    def betax(self, value):
        self._t.betax = value

    @property
    def betay(self):
        return self._t.betay

    @betay.setter
    def betay(self, value):
        self._t.betay = value

    @property
    def alphax(self):
        return self._t.alphax

    @alphax.setter
    def alphax(self, value):
        self._t.alphax = value

    @property
    def alphay(self):
        return self._t.alphay

    @alphay.setter
    def alphay(self, value):
        self._t.alphay = value

    @property
    def mux(self):
        return self._t.mux

    @mux.setter
    def mux(self, value):
        self._t.mux = value

    @property
    def muy(self):
        return self._t.muy

    @muy.setter
    def muy(self, value):
        self._t.muy = value

    @property
    def etax(self):
        return self._t.etax[0]

    @etax.setter
    def etax(self, value):
        self._t.etax[0] = value

    @property
    def etay(self):
        return self._t.etay[0]

    @etay.setter
    def etay(self, value):
        self._t.etay[0] = value

    @property
    def etapx(self):
        return self._t.etax[1]

    @etapx.setter
    def etapx(self, value):
        self._t.etax[1] = value

    @property
    def etapy(self):
        return self._t.etay[1]

    @etapy.setter
    def etapy(self, value):
        self._t.etay[1] = value

    def __str__(self):
        r = ''
        r += 'rx, ry        : ' + '{0:+10.3e}, {1:+10.3e}'.format(self.rx, self.ry) + '\n'
        r += 'px, py        : ' + '{0:+10.3e}, {1:+10.3e}'.format(self.px, self.py) + '\n'
        r += 'de, dl        : ' + '{0:+10.3e}, {1:+10.3e}'.format(self.de, self.dl) + '\n'
        r += 'mux, muy      : ' + '{0:+10.3e}, {1:+10.3e}'.format(self.mux, self.muy) + '\n'
        r += 'betax, betay  : ' + '{0:+10.3e}, {1:+10.3e}'.format(self.betax, self.betay) + '\n'
        r += 'alphax, alphay: ' + '{0:+10.3e}, {1:+10.3e}'.format(self.alphax, self.alphay) + '\n'
        r += 'etax, etapx   : ' + '{0:+10.3e}, {1:+10.3e}'.format(self.etax, self.etapx) + '\n'
        r += 'etay, etapy   : ' + '{0:+10.3e}, {1:+10.3e}'.format(self.etay, self.etapy) + '\n'
        return r

    def make_dict(self):
        co    =  self.co
        beta  = [self.betax, self.betay]
        alpha = [self.alphax, self.alphay]
        etax  = [self.etax, self.etapx]
        etay  = [self.etay, self.etapy]
        mu    = [self.mux, self.muy]
        _dict = {'co': co, 'beta': beta, 'alpha': alpha, 'etax': etax, 'etay': etay, 'mu': mu}
        return _dict

    @staticmethod
    def make_new(*args, **kwargs):
        """Build a Twiss object.
        """
        if args:
            if isinstance(args[0], dict):
                kwargs = args[0]
        n = Twiss()
        n.co = kwargs['co'] if 'co' in kwargs else (0.0,)*6
        n.mux,    n.muy    = kwargs['mu']    if 'mu'    in kwargs else (0.0, 0.0)
        n.betax,  n.betay  = kwargs['beta']  if 'beta'  in kwargs else (0.0, 0.0)
        n.alphax, n.alphay = kwargs['alpha'] if 'alpha' in kwargs else (0.0, 0.0)
        n.etax,   n.etapx  = kwargs['etax']  if 'etax'  in kwargs else (0.0, 0.0)
        n.etay,   n.etapy  = kwargs['etay']  if 'etay'  in kwargs else (0.0, 0.0)
        return n

@_interactive
def calc_twiss(accelerator=None, init_twiss=None, fixed_point=None, indices = 'open'):
    """Return Twiss parameters of uncoupled dynamics.

    Keyword arguments:
    accelerator -- Accelerator object
    init_twiss  -- Twiss parameters at the start of first element
    fixed_point -- 6D position at the start of first element
    indices     -- Open or closed

    Returns:
    tw -- list of Twiss objects
    m66
    transfer_matrices
    closed_orbit
    """
    if indices == 'open':
        closed_flag = False
    elif indices == 'closed':
        closed_flag = True
    else:
        raise OpticsException("invalid value for 'indices' in calc_twiss")

    _m66   = _trackcpp.Matrix()
    _twiss = _trackcpp.CppTwissVector()

    if init_twiss is not None:
        ''' as a transport line: uses init_twiss '''
        _init_twiss = init_twiss._t
        if fixed_point is None:
            _fixed_point = _init_twiss.co
        else:
            raise OpticsException('arguments init_twiss and fixed_orbit are mutually exclusive')
        r = _trackcpp.calc_twiss(accelerator._accelerator, _fixed_point, _m66, _twiss, _init_twiss, closed_flag)

    else:
        ''' as a periodic system: try to find periodic solution '''
        if accelerator.harmonic_number == 0:
            raise OpticsException('Either harmonic number was not set or calc_twiss was'
                'invoked for transport line without initial twiss')

        if fixed_point is None:
            _closed_orbit = _trackcpp.CppDoublePosVector()
            _fixed_point_guess = _trackcpp.CppDoublePos()

            if not accelerator.cavity_on and not accelerator.radiation_on:
                r = _trackcpp.track_findorbit4(accelerator._accelerator, _closed_orbit, _fixed_point_guess)
            elif not accelerator.cavity_on and accelerator.radiation_on:
                raise OpticsException('The radiation is on but the cavity is off')
            else:
                r = _trackcpp.track_findorbit6(accelerator._accelerator, _closed_orbit, _fixed_point_guess)

            if r > 0:
                raise _tracking.TrackingException(_trackcpp.string_error_messages[r])
            _fixed_point = _closed_orbit[0]

        else:
            _fixed_point = _tracking._Numpy2CppDoublePos(fixed_point)

        r = _trackcpp.calc_twiss(accelerator._accelerator, _fixed_point, _m66, _twiss)

    if r > 0:
        raise OpticsException(_trackcpp.string_error_messages[r])

    twiss = TwissList(_twiss)
    m66 = _tracking._CppMatrix2Numpy(_m66)

    return twiss, m66

@_interactive
def get_rf_frequency(accelerator):
    """Return the frequency of the first RF cavity in the lattice"""
    for e in accelerator:
        if e.frequency != 0.0:
            return e.frequency
    else:
        raise OpticsException('no cavity element in the lattice')


@_interactive
def get_rf_voltage(accelerator):
    """Return the voltage of the first RF cavity in the lattice"""
    voltages = []
    for e in accelerator:
        if e.voltage != 0.0:
            voltages.append(e.voltage)
    if voltages:
        if len(voltages) == 1:
            return voltages[0]
        else:
            return voltages
    else:
        raise OpticsException('no cavity element in the lattice')


@_interactive
def get_revolution_period(accelerator):
    return accelerator.length/accelerator.velocity


@_interactive
def get_revolution_frequency(accelerator):
    return 1.0/get_revolution_period(accelerator)


@_interactive
def get_traces(accelerator=None, m66=None, closed_orbit=None):
    """Return traces of 6D one-turn transfer matrix"""
    if m66 is None:
        m66 = _tracking.findm66(accelerator,
                                indices = 'm66', closed_orbit = closed_orbit)
    trace_x = m66[0,0] + m66[1,1]
    trace_y = m66[2,2] + m66[3,3]
    trace_z = m66[4,4] + m66[5,5]
    return trace_x, trace_y, trace_z, m66, closed_orbit


@_interactive
def get_frac_tunes(accelerator=None, m66=None, closed_orbit=None, coupled=False):
    """Return fractional tunes of the accelerator"""

    trace_x, trace_y, trace_z, m66, closed_orbit = get_traces(accelerator,
                                                   m66 = m66,
                                                   closed_orbit = closed_orbit)
    tune_x = _math.acos(trace_x/2.0)/2.0/_math.pi
    tune_y = _math.acos(trace_y/2.0)/2.0/_math.pi
    tune_z = _math.acos(trace_z/2.0)/2.0/_math.pi
    if coupled:
        tunes = _np.log(_np.linalg.eigvals(m66))/2.0/_math.pi/1j
        tune_x = tunes[_np.argmin(abs(_np.sin(tunes.real) - _math.sin(tune_x)))]
        tune_y = tunes[_np.argmin(abs(_np.sin(tunes.real) - _math.sin(tune_y)))]
        tune_z = tunes[_np.argmin(abs(_np.sin(tunes.real) - _math.sin(tune_z)))]

    return tune_x, tune_y, tune_z, trace_x, trace_y, trace_z, m66, closed_orbit


@_interactive
def get_chromaticities(accelerator):
    raise OpticsException('not implemented')


@_interactive
def get_mcf(accelerator, order=1, energy_offset=None):
    """Return momentum compaction factor of the accelerator"""
    if energy_offset is None:
        energy_offset = _np.linspace(-1e-3,1e-3,11)

    accel=accelerator[:]
    _tracking.set4dtracking(accel)
    ring_length = _lattice.length(accel)

    dl = _np.zeros(_np.size(energy_offset))
    for i in range(len(energy_offset)):
        fp = _tracking.findorbit4(accel,energy_offset[i])
        X0 = _np.concatenate([fp,[energy_offset[i],0]]).tolist()
        T = _tracking.ringpass(accel,X0)
        dl[i] = T[0][5]/ring_length

    polynom = _np.polyfit(energy_offset,dl,order)
    a = _np.fliplr([polynom])[0].tolist()
    a = a[1:]
    if len(a) == 1:
        a=a[0]
    return a

@_interactive
def get_radiation_integrals(accelerator,
                          twiss=None,
                          m66=None,
                          closed_orbit=None):
    """Calculate radiation integrals for periodic systems"""

    if twiss is None or m66 is None:
        fixed_point = closed_orbit if closed_orbit is None else closed_orbit[:,0]
        twiss, m66 = calc_twiss(accelerator, fixed_point=fixed_point)

    spos = _lattice.find_spos(accelerator)

    # # Old get twiss
    # etax,etapx,betax,alphax = twiss,('etax','etapx','betax','alphax'))

    etax, etapx, betax, alphax = twiss.etax, twiss.etapx, twiss.betax, twiss.alphax

    if len(spos) != len(accelerator) + 1:
        spos = _np.resize(spos,len(accelerator)+1); spos[-1] = spos[-2] + accelerator[-1].length
        etax = _np.resize(etax,len(accelerator)+1); etax[-1] = etax[0]
        etapx = _np.resize(etapx,len(accelerator)+1); etapx[-1] = etapx[0]
        betax = _np.resize(betax,len(accelerator)+1); betax[-1] = betax[0]
        alphax = _np.resize(alphax,len(accelerator)+1); alphax[-1] = alphax[0]
    gammax = (1+alphax**2)/betax
    n = len(accelerator)
    angle, angle_in, angle_out, K = _np.zeros((4,n))
    for i in range(n):
        angle[i] = accelerator._accelerator.lattice[i].angle
        angle_in[i] = accelerator._accelerator.lattice[i].angle_in
        angle_out[i] = accelerator._accelerator.lattice[i].angle_out
        K[i] = accelerator._accelerator.lattice[i].polynom_b[1]
    idx, *_ = _np.nonzero(angle)
    leng = spos[idx+1]-spos[idx]
    rho  = leng/angle[idx]
    angle_in = angle_in[idx]
    angle_out = angle_out[idx]
    K = K[idx]
    etax_in, etax_out = etax[idx], etax[idx+1]
    etapx_in, etapx_out = etapx[idx], etapx[idx+1]
    betax_in, betax_out = betax[idx], betax[idx+1]
    alphax_in, alphax_out = alphax[idx], alphax[idx+1]
    gammax_in, gammax_out = gammax[idx], gammax[idx+1]
    H_in = betax_in*etapx_in**2 + 2*alphax_in*etax_in*etapx_in+gammax_in*etax_in**2
    H_out = betax_out*etapx_out**2 + 2*alphax_out*etax_out*etapx_out+gammax_out*etax_out**2

    etax_avg = 0.5*(etax_in+etax_out)
    rho2, rho3 = rho**2, rho**3
    rho3abs = _np.abs(rho3)

    integrals = [0.0]*6
    integrals[0] = _np.dot(etax_avg/rho, leng)
    integrals[1] = _np.dot(1/rho2, leng)
    integrals[2] = _np.dot(1/rho3abs, leng)
    integrals[3] = sum((etax_in/rho2)*_np.tan(angle_in)) + \
                   sum((etax_out/rho2)*_np.tan(angle_out)) + \
                   _np.dot((etax_avg/rho3)*(1+2*rho2*K), leng)
    integrals[4] = _np.dot(0.5*(H_in+H_out)/rho3abs, leng)
    integrals[5] = _np.dot((K*etax_avg)**2, leng)

    return integrals, twiss, m66

@_interactive
def get_natural_energy_spread(accelerator):
    Cq = _mp.constants.Cq
    gamma = accelerator.gamma_factor
    integrals, *_ = get_radiation_integrals(accelerator)
    natural_energy_spread = _math.sqrt( Cq*(gamma**2)*integrals[2]/(2*integrals[1] + integrals[3]))
    return natural_energy_spread


@_interactive
def get_natural_emittance(accelerator):
    Cq = _mp.constants.Cq
    gamma = accelerator.gamma_factor
    integrals, *_ = get_radiation_integrals(accelerator)

    damping = _np.zeros(3)
    damping[0] = 1.0 - integrals[3]/integrals[1]
    damping[1] = 1.0
    damping[2] = 2.0 + integrals[3]/integrals[1]

    natural_emittance = Cq*(gamma**2)*integrals[4]/(damping[0]*integrals[1])
    return natural_emittance


@_interactive
def get_natural_bunch_length(accelerator):
    c = _mp.constants.light_speed
    rad_cgamma = _mp.constants.rad_cgamma
    e0 = accelerator.energy
    gamma = accelerator.gamma_factor
    beta = accelerator.beta_factor
    harmon = accelerator.harmonic_number

    integrals, *_ = get_radiation_integrals(accelerator)
    rev_freq = get_revolution_frequency(accelerator)
    compaction_factor = get_mcf(accelerator)

    etac = gamma**(-2) - compaction_factor

    freq = get_rf_frequency(accelerator)
    v_cav = get_rf_voltage(accelerator)
    radiation = rad_cgamma*((e0/1e9)**4)*integrals[1]/(2*_math.pi)*1e9
    overvoltage = v_cav/radiation

    syncphase = _math.pi - _math.asin(1/overvoltage)
    synctune = _math.sqrt((etac * harmon * v_cav * _math.cos(syncphase))/(2*_math.pi*e0))
    natural_energy_spread = get_natural_energy_spread(accelerator)
    bunch_length = beta* c *abs(etac)* natural_energy_spread /( synctune * rev_freq *2*_math.pi)
    return bunch_length


@_interactive
def get_equilibrium_parameters(accelerator,
                             twiss=None,
                             m66=None,
                             closed_orbit=None):

    c = _mp.constants.light_speed
    Cq = _mp.constants.Cq
    Ca = _mp.constants.Ca
    rad_cgamma = _mp.constants.rad_cgamma

    e0 = accelerator.energy
    gamma = accelerator.gamma_factor
    beta = accelerator.beta_factor
    harmon = accelerator.harmonic_number
    circumference = accelerator.length
    rev_time = circumference / accelerator.velocity
    rev_freq = get_revolution_frequency(accelerator)

    compaction_factor = get_mcf(accelerator)
    etac = gamma**(-2) - compaction_factor

    integrals, *args = get_radiation_integrals(accelerator,twiss,m66,closed_orbit)

    damping = _np.zeros(3)
    damping[0] = 1.0 - integrals[3]/integrals[1]
    damping[1] = 1.0
    damping[2] = 2.0 + integrals[3]/integrals[1]

    radiation_damping = _np.zeros(3)
    radiation_damping[0] = 1.0/(Ca*((e0/1e9)**3)*integrals[1]*damping[0]/circumference)
    radiation_damping[1] = 1.0/(Ca*((e0/1e9)**3)*integrals[1]*damping[1]/circumference)
    radiation_damping[2] = 1.0/(Ca*((e0/1e9)**3)*integrals[1]*damping[2]/circumference)

    radiation = rad_cgamma*((e0/1e9)**4)*integrals[1]/(2*_math.pi)*1e9
    natural_energy_spread = _math.sqrt( Cq*(gamma**2)*integrals[2]/(2*integrals[1] + integrals[3]))
    natural_emittance = Cq*(gamma**2)*integrals[4]/(damping[0]*integrals[1])

    freq = get_rf_frequency(accelerator)
    v_cav = get_rf_voltage(accelerator)
    overvoltage = v_cav/radiation

    syncphase = _math.pi - _math.asin(1.0/overvoltage)
    synctune = _math.sqrt((etac * harmon * v_cav * _math.cos(syncphase))/(2*_math.pi*e0))
    rf_energy_acceptance = _math.sqrt(v_cav*_math.sin(syncphase)*2*(_math.sqrt((overvoltage**2)-1.0)
                        - _math.acos(1.0/overvoltage))/(_math.pi*harmon*abs(etac)*e0))
    bunch_length = beta* c *abs(etac)* natural_energy_spread /( synctune * rev_freq *2*_math.pi)

    summary=dict(compaction_factor = compaction_factor, radiation_integrals = integrals, damping_numbers = damping,
        damping_times = radiation_damping, natural_energy_spread = natural_energy_spread, etac = etac,
        natural_emittance = natural_emittance, overvoltage = overvoltage, syncphase = syncphase,
        synctune = synctune, rf_energy_acceptance = rf_energy_acceptance, bunch_length = bunch_length)

    return [summary, integrals] + args


@_interactive
def get_beam_size(accelerator, coupling=0.0, closed_orbit=None, indices='open'):
    """Return beamsizes (stddev) along ring"""

    # twiss parameters
    fixed_point = closed_orbit if closed_orbit is None else closed_orbit[:,0]
    twiss, *_ = calc_twiss(accelerator, fixed_point=fixed_point, indices=indices)

    # Old get twiss
    # betax, alphax, etax, etapx = get_twiss(twiss, ('betax','alphax','etax','etapx'))
    # betay, alphay, etay, etapy = get_twiss(twiss, ('betay','alphay','etay','etapy'))

    betax, alphax, etax, etapx = twiss.betax, twiss.alphax, twiss.etax, twiss.etapx
    betay, alphay, etay, etapy = twiss.betay, twiss.alphay, twiss.etay, twiss.etapy

    gammax = (1.0 + alphax**2)/betax
    gammay = (1.0 + alphay**2)/betay
    # emittances and energy spread
    summary, *_ = get_equilibrium_parameters(accelerator)
    e0 = summary['natural_emittance']
    sigmae = summary['natural_energy_spread']
    ey = e0 * coupling / (1.0 + coupling)
    ex = e0 * 1 / (1.0 + coupling)
    # beamsizes per se
    sigmax  = _np.sqrt(ex * betax + (sigmae * etax)**2)
    sigmay  = _np.sqrt(ey * betay + (sigmae * etay)**2)
    sigmaxl = _np.sqrt(ex * gammax + (sigmae * etapx)**2)
    sigmayl = _np.sqrt(ey * gammay + (sigmae * etapy)**2)
    return sigmax, sigmay, sigmaxl, sigmayl, ex, ey, summary, twiss


@_interactive
def get_transverse_acceptance(accelerator, twiss=None, init_twiss=None, fixed_point=None, energy_offset=0.0):
    """Return linear transverse horizontal and vertical physical acceptances"""

    m66 = None
    if twiss is None:
        twiss, m66 = calc_twiss(accelerator, init_twiss=init_twiss, fixed_point=fixed_point, indices='open')
        n = len(accelerator)
    else:
        if len(twiss) == len(accelerator):
            n = len(accelerator)
        elif len(twiss) == len(accelerator)+1:
            n = len(accelerator)+1
        else:
            raise OpticsException('Mismatch between size of accelerator and size of twiss object')

    # # Old get twiss
    # closed_orbit = _np.zeros((6,n))
    # closed_orbit[0,:], closed_orbit[2,:] = get_twiss(twiss, ('rx','ry'))
    # betax, betay, etax, etay = get_twiss(twiss, ('betax', 'betay', 'etax', 'etay'))

    closed_orbit = twiss.co
    betax, betay, etax, etay = twiss.betax, twiss.betay, twiss.etax, twiss.etay

    # physical apertures
    lattice = accelerator._accelerator.lattice
    hmax, vmax = _np.array([(lattice[i].hmax,lattice[i].vmax) for i in range(len(accelerator))]).transpose()
    if len(hmax) != n:
        hmax = _np.append(hmax, hmax[-1])
        vmax = _np.append(vmax, vmax[-1])

    # calcs local linear acceptances
    co_x, co_y = closed_orbit[(0,2),:]

    # calcs acceptance with beta at entrance of elements
    betax_sqrt, betay_sqrt = _np.sqrt(betax), _np.sqrt(betay)
    local_accepx_pos = (hmax - (co_x + etax * energy_offset)) / betax_sqrt
    local_accepx_neg = (hmax + (co_x + etax * energy_offset)) / betax_sqrt
    local_accepy_pos = (vmax - (co_y + etay * energy_offset)) / betay_sqrt
    local_accepy_neg = (vmax + (co_y + etay * energy_offset)) / betay_sqrt
    local_accepx_pos[local_accepx_pos < 0] = 0
    local_accepx_neg[local_accepx_neg < 0] = 0
    local_accepx_pos[local_accepy_pos < 0] = 0
    local_accepx_neg[local_accepy_neg < 0] = 0
    accepx_in = [min(local_accepx_pos[i],local_accepx_neg[i])**2 for i in range(n)]
    accepy_in = [min(local_accepy_pos[i],local_accepy_neg[i])**2 for i in range(n)]

    # calcs acceptance with beta at exit of elements
    betax_sqrt, betay_sqrt = _np.roll(betax_sqrt,-1), _np.roll(betay_sqrt,-1)
    local_accepx_pos = (hmax - (co_x + etax * energy_offset)) / betax_sqrt
    local_accepx_neg = (hmax + (co_x + etax * energy_offset)) / betax_sqrt
    local_accepy_pos = (vmax - (co_y + etay * energy_offset)) / betay_sqrt
    local_accepy_neg = (vmax + (co_y + etay * energy_offset)) / betay_sqrt
    local_accepx_pos[local_accepx_pos < 0] = 0
    local_accepx_neg[local_accepx_neg < 0] = 0
    local_accepx_pos[local_accepy_pos < 0] = 0
    local_accepx_neg[local_accepy_neg < 0] = 0
    accepx_out = [min(local_accepx_pos[i],local_accepx_neg[i])**2 for i in range(n)]
    accepy_out = [min(local_accepy_pos[i],local_accepy_neg[i])**2 for i in range(n)]

    accepx = [min(accepx_in[i],accepx_out[i]) for i in range(n)]
    accepy = [min(accepy_in[i],accepy_out[i]) for i in range(n)]

    if m66 is None:
        return accepx, accepy, twiss
    else:
        return accepx, accepy, twiss, m66


class TwissList(object):

    def __init__(self, twiss_list=None):
        """Read-only list of matrices.

        Keyword argument:
        twiss_list -- trackcpp Twiss vector (default: None)
        """
        # TEST!
        if twiss_list is not None:
            if isinstance(twiss_list, _trackcpp.CppTwissVector):
                self._tl = twiss_list
            else:
                raise TrackingException('invalid Twiss vector')
        else:
            self._tl = _trackcpp.CppTwissVector()
        self._ptl = [self._tl[i] for i in range(len(self._tl))]

    def __len__(self):
        return len(self._tl)

    def __getitem__(self, index):
        if isinstance(index,(int, _np.int_)):
            return Twiss(twiss=self._tl[index])
        elif isinstance(index, (list,tuple,_np.ndarray)) and all(isinstance(x, (int, _np.int_)) for x in index):
            tl = _trackcpp.CppTwissVector()
            for i in index:
                tl.append(self._tl[i])
            return TwissList(twiss_list = tl)
        elif isinstance(index, slice):
            return TwissList(twiss_list = self._tl[index])
        else:
            raise TypeError('invalid index')

    def append(self, value):
        if isinstance(value, _trackcpp.Twiss):
            self._tl.append(value)
            self._ptl.append(value)
        elif isinstance(value, Twiss):
            self._tl.append(value._t)
            self._ptl.append(value._t)
        elif self._is_list_of_lists(value):
            t = _trackcpp.Twiss()
            for line in value:
                t.append(line)
            self._tl.append(t)
            self._ptl.append(t)
        else:
            raise TrackingException('can only append twiss-like objects')

    def _is_list_of_lists(self, value):
        valid_types = (list, tuple)
        if not isinstance(value, valid_types):
            return False
        for line in value:
            if not isinstance(line, valid_types):
                return False
        return True

    @property
    def betax(self):
        betax = _np.array([float(self._ptl[i].betax) for i in range(len(self._ptl))])
        return betax if len(betax) > 1 else betax[0]

    @property
    def betay(self):
        betay = _np.array([float(self._ptl[i].betay) for i in range(len(self._ptl))])
        return betay if len(betay) > 1 else betay[0]

    @property
    def alphax(self):
        alphax = _np.array([float(self._ptl[i].alphax) for i in range(len(self._ptl))])
        return alphax if len(alphax) > 1 else alphax[0]

    @property
    def alphay(self):
        alphay = _np.array([float(self._ptl[i].alphay) for i in range(len(self._ptl))])
        return alphay if len(alphay) > 1 else alphay[0]

    @property
    def mux(self):
        mux = _np.array([float(self._ptl[i].mux) for i in range(len(self._ptl))])
        return mux if len(mux) > 1 else mux[0]

    @property
    def muy(self):
        muy = _np.array([float(self._ptl[i].muy) for i in range(len(self._ptl))])
        return muy if len(muy) > 1 else muy[0]

    @property
    def etax(self):
        etax = _np.array([float(self._ptl[i].etax[0]) for i in range(len(self._ptl))])
        return etax if len(etax) > 1 else etax[0]

    @property
    def etay(self):
        etay = _np.array([float(self._ptl[i].etay[0]) for i in range(len(self._ptl))])
        return etay if len(etay) > 1 else etay[0]

    @property
    def etapx(self):
        etapx = _np.array([float(self._ptl[i].etax[1]) for i in range(len(self._ptl))])
        return etapx if len(etapx) > 1 else etapx[0]

    @property
    def etapy(self):
        etapy = _np.array([float(self._ptl[i].etay[1]) for i in range(len(self._ptl))])
        return etapy if len(etapy) > 1 else etapy[0]

    @property
    def co(self):
        co = [self._ptl[i].co for i in range(len(self._ptl))]
        co = [[co[i].rx, co[i].px, co[i].ry, co[i].py, co[i].de, co[i].dl] for i in range(len(co))]
        co = _np.transpose(_np.array(co))
        return co if len(co[0,:]) > 1 else co[:,0]


class old_Twiss:
    def __init__(self):
        self.spos = 0
        self.rx, self.px  = 0, 0
        self.ry, self.py  = 0, 0
        self.de, self.dl  = 0, 0
        self.etax, self.etapx = 0, 0
        self.etay, self.etapy = 0, 0
        self.mux, self.betax, self.alphax = 0, None, None
        self.muy, self.betay, self.alphay = 0, None, None

    def __str__(self):
        r = ''
        r += 'spos          : ' + '{0:+10.3e}'.format(self.spos) + '\n'
        r += 'rx, ry        : ' + '{0:+10.3e}, {1:+10.3e}'.format(self.rx, self.ry) + '\n'
        r += 'px, py        : ' + '{0:+10.3e}, {1:+10.3e}'.format(self.px, self.py) + '\n'
        r += 'de, dl        : ' + '{0:+10.3e}, {1:+10.3e}'.format(self.de, self.dl) + '\n'
        r += 'mux, muy      : ' + '{0:+10.3e}, {1:+10.3e}'.format(self.mux, self.muy) + '\n'
        r += 'betax, betay  : ' + '{0:+10.3e}, {1:+10.3e}'.format(self.betax, self.betay) + '\n'
        r += 'alphax, alphay: ' + '{0:+10.3e}, {1:+10.3e}'.format(self.alphax, self.alphay) + '\n'
        r += 'etax, etay    : ' + '{0:+10.3e}, {1:+10.3e}'.format(self.etax, self.etay) + '\n'
        r += 'etapx, etapy  : ' + '{0:+10.3e}, {1:+10.3e}'.format(self.etapx, self.etapy) + '\n'
        return r

    def make_copy(self):
        n = Twiss()
        n.spos = self.spos
        n.rx, n.px = self.rx, self.px
        n.ry, n.py = self.ry, self.py
        n.de, n.dl = self.de, self.dl
        n.etax, n.etapx = self.etax, self.etapx
        n.etay, n.etapy = self.etay, self.etapy
        n.mux, n.betax, n.alphax = self.mux, self.betax, self.alphax
        n.muy, n.betay, n.alphay = self.muy, self.betay, self.alphay
        return n

    def make_dict(self):
        fixed_point = self.fixed_point
        beta  = [self.betax, self.betay]
        alpha = [self.alphax, self.alphay]
        eta   = [self.etax, self.etay]
        etap  = [self.etapx, self.etapy]
        mu    = [self.mux, self.muy]
        _dict = {'spos': spos, 'fixed_point': fixed_point, 'beta': beta,
                 'alpha': alpha, 'eta': eta, 'etap': etap, 'mu': mu}
        return _dict

    @staticmethod
    def make_new(*args, **kwargs):
        """Build a Twiss object.

        Keyword arguments:
        spos -- Initial s position
        fixed_point -- Initial 6D particle position
        mu    -- List of Twiss attributes [mux, muy]
        alpha -- List of Twiss attributes [alphax, alphay]
        beta  -- List of Twiss attributes [betax, betay]
        eta   -- List of Twiss attributes [etax, etay]
        etap  -- List of Twiss attributes [etapx, etapy]

        """
        if args:
            if isinstance(args[0], dict):
                kwargs = args[0]
        n = Twiss()
        n.spos = kwargs['spos'] if 'spos' in kwargs else 0.0
        n.fixed_point = kwargs['fixed_point'] if 'fixed_point' in kwargs else (0.0,)*6
        n.mux, n.muy = kwargs['mu'] if 'mu' in kwargs else (0.0, 0.0)
        n.betax, n.betay = kwargs['beta'] if 'beta' in kwargs else (None, None)
        n.alphax, n.alphay = kwargs['alpha'] if 'alpha' in kwargs else (0.0, 0.0)
        n.etax, n.etay = kwargs['eta'] if 'eta' in kwargs else (0.0, 0.0)
        n.etapx, n.etapy = kwargs['etap'] if 'etap' in kwargs else (0.0, 0.0)
        return n

    @property
    def fixed_point(self):
        rx, px = self.rx, self.px
        ry, py = self.ry, self.py
        de, dl = self.de, self.dl
        fixed_point = [rx, px, ry, py, de, dl]
        return fixed_point

    @fixed_point.setter
    def fixed_point(self, value):
        self.rx, self.px  = value[0], value[1]
        self.ry, self.py  = value[2], value[3]
        self.de, self.dl  = value[4], value[5]

@_interactive
def get_twiss(twiss_list, attribute_list):
    """Build a matrix with Twiss data from a list of Twiss objects.

    Accepts a list of Twiss objects and returns a matrix with Twiss data, one line for
    each Twiss parameter defined in 'attributes_list'.

    Keyword arguments:
    twiss_list -- List with Twiss objects
    attributes_list -- List of strings with Twiss attributes to be stored in twiss matrix

    Returns:
    m -- Matrix with Twiss data. Can also be thought of a single column of
         Twiss parameter vectors:
            betax, betay = get_twiss(twiss, ('betax','betay'))
    """
    if isinstance(attribute_list, str):
        attribute_list = (attribute_list,)
    values = _np.zeros((len(attribute_list),len(twiss_list)))
    for i in range(len(twiss_list)):
        for j in range(len(attribute_list)):
            values[j,i] = getattr(twiss_list[i], attribute_list[j])
    if values.shape[0] == 1:
        return values[0,:]
    else:
        return values

@_interactive
def old_calc_twiss(accelerator=None, init_twiss=None, fixed_point=None, indices = 'open'):
    """Return Twiss parameters of uncoupled dynamics.

    Keyword arguments:
    accelerator -- Accelerator object
    init_twiss  -- Twiss parameters at the start of first element
    fixed_point -- 6D position at the start of first element
    indices     -- Open or closed

    Returns:
    tw -- list of Twiss objects
    m66
    transfer_matrices
    closed_orbit
    """

    if indices == 'open':
        length = len(accelerator)
    elif indices == 'closed':
        length = len(accelerator)+1
    else:
        raise OpticsException("invalid value for 'indices' in calc_twiss")

    if init_twiss is not None:
        ''' as a transport line: uses init_twiss '''
        if fixed_point is None:
            fixed_point = init_twiss.fixed_point
        else:
            raise OpticsException('arguments init_twiss and fixed_orbit are mutually exclusive')

        closed_orbit, *_ = _tracking.linepass(accelerator, particles=list(fixed_point), indices='open')
        m66, cumul_trans_matrices = _tracking.findm66(accelerator, closed_orbit=closed_orbit)

        if indices == 'closed':
            orb, *_ = _tracking.linepass(accelerator[-1:], particles=closed_orbit[:,-1])
            closed_orbit = _np.append(closed_orbit,orb.transpose(),axis=1)

        mx, my = m66[0:2, 0:2], m66[2:4, 2:4]
        t = init_twiss
        t.etax = _np.array([[t.etax], [t.etapx]])
        t.etay = _np.array([[t.etay], [t.etapy]])
    else:
        ''' as a periodic system: try to find periodic solution '''

        if accelerator.harmonic_number == 0:
            raise OpticsException('Either harmonic number was not set or calc_twiss was'
                'invoked for transport line without initial twiss')

        if fixed_point is None:
            if not accelerator.cavity_on and not accelerator.radiation_on:
                closed_orbit = _np.zeros((6,length))
                closed_orbit[:4,:] = _tracking.findorbit4(accelerator, indices=indices)
            elif not accelerator.cavity_on and accelerator.radiation_on:
                raise OpticsException('The radiation is on but the cavity is off')
            else:

                closed_orbit = _tracking.findorbit6(accelerator, indices=indices)
        else:
            closed_orbit, *_ = _tracking.linepass(accelerator, particles=list(fixed_point), indices=indices)

        ''' calcs twiss at first element '''
        orbit = closed_orbit[:,:-1] if indices == 'closed' else closed_orbit
        m66, cumul_trans_matrices, *_ = _tracking.findm66(accelerator, closed_orbit=orbit)
        mx, my = m66[0:2,0:2], m66[2:4,2:4] # decoupled transfer matrices
        trace_x, trace_y, *_ = get_traces(accelerator, m66 = m66, closed_orbit=closed_orbit)
        if not (-2.0 < trace_x < 2.0):
            raise OpticsException('horizontal dynamics is unstable')
        if not (-2.0 < trace_y < 2.0):
            raise OpticsException('vertical dynamics is unstable')
        sin_nux = _math.copysign(1,mx[0,1]) * _math.sqrt(-mx[0,1] * mx[1,0] - ((mx[0,0] - mx[1,1])**2)/4);
        sin_nuy = _math.copysign(1,my[0,1]) * _math.sqrt(-my[0,1] * my[1,0] - ((my[0,0] - my[1,1])**2)/4);
        fp = closed_orbit[:,0]
        t = Twiss()
        t.spos = 0
        t.rx, t.px = fixed_point[0], fixed_point[1]
        t.ry, t.py = fixed_point[2], fixed_point[3]
        t.de, t.dl = fixed_point[4], fixed_point[5]
        t.alphax = (mx[0,0] - mx[1,1]) / 2 / sin_nux
        t.betax  = mx[0,1] / sin_nux
        t.alphay = (my[0,0] - my[1,1]) / 2 / sin_nuy
        t.betay  = my[0,1] / sin_nuy
        ''' dispersion function based on eta = (1 - M)^(-1) D '''
        Dx = _np.array([[m66[0,4]],[m66[1,4]]])
        Dy = _np.array([[m66[2,4]],[m66[3,4]]])
        t.etax = _np.linalg.solve(_np.eye(2,2) - mx, Dx)
        t.etay = _np.linalg.solve(_np.eye(2,2) - my, Dy)

    ''' get transfer matrices from cumulative transfer matrices '''
    transfer_matrices = []
    m66_prev = _np.eye(6,6)
    cumul_trans_matrices.append(m66)
    for m66_this in cumul_trans_matrices[1:]: # Matrices at start of elements
        inv_m66_prev = _np.linalg.inv(m66_prev)
        tm = _np.dot(m66_this, inv_m66_prev)
        #tm = _np.linalg.solve(m66_prev.T, m66_this.T).T  # Fernando, you may uncomment this line when running YOUR code! aushuashuahs
        m66_prev = m66_this
        transfer_matrices.append(tm)

    ''' propagates twiss through line '''
    tw = [t]
    m_previous = _np.eye(6,6)
    for i in range(1, length):
        m = transfer_matrices[i-1]
        mx, my = m[0:2,0:2], m[2:4,2:4] # decoupled transfer matrices
        Dx = _np.array([[m[0,4]],[m[1,4]]])
        Dy = _np.array([[m[2,4]],[m[3,4]]])
        n = Twiss()
        n.spos   = t.spos + accelerator[i-1].length
        fp = closed_orbit[:,i]
        n.rx, n.px = fixed_point[0], fixed_point[1]
        n.ry, n.py = fixed_point[2], fixed_point[3]
        n.de, n.dl = fixed_point[4], fixed_point[5]
        n.betax  =  ((mx[0,0] * t.betax - mx[0,1] * t.alphax)**2 + mx[0,1]**2) / t.betax
        n.alphax = -((mx[0,0] * t.betax - mx[0,1] * t.alphax) * (mx[1,0] * t.betax - mx[1,1] * t.alphax) + mx[0,1] * mx[1,1]) / t.betax
        n.betay  =  ((my[0,0] * t.betay - my[0,1] * t.alphay)**2 + my[0,1]**2) / t.betay
        n.alphay = -((my[0,0] * t.betay - my[0,1] * t.alphay) * (my[1,0] * t.betay - my[1,1] * t.alphay) + my[0,1] * my[1,1]) / t.betay

        ''' calcs phase advance based on R(mu) = U(2) M(2|1) U^-1(1) '''
        sint = mx[0,1]/_math.sqrt(n.betax * t.betax)
        cost = (mx[0,0] * t.betax - mx[0,1] * t.alphax)/_math.sqrt(n.betax * t.betax)
        dmux = _math.atan2(sint, cost)
        n.mux = t.mux + dmux
        sint = my[0,1]/_math.sqrt(n.betay * t.betay)
        cost = (my[0,0] * t.betay - my[0,1] * t.alphay)/_math.sqrt(n.betay * t.betay)
        dmuy = _math.atan2(sint, cost)
        n.muy = t.muy + dmuy

        ''' when phase advance in an element is over PI atan2 returns a
            negative value that has to be corrected by adding 2*PI'''
        if dmux < 0 and dmux < -10*_sys.float_info.epsilon:
            n.mux += 2*_math.pi
        if dmuy < 0 and dmuy < -10*_sys.float_info.epsilon:
            n.muy += 2*_math.pi

        ''' dispersion function'''
        n.etax = Dx + _np.dot(mx, t.etax)
        n.etay = Dy + _np.dot(my, t.etay)

        tw.append(n)

        t = n.make_copy()

    ''' converts eta format '''
    for t in tw:
        t.etapx, t.etapy = (t.etax[1,0], t.etay[1,0])
        t.etax,  t.etay  = (t.etax[0,0], t.etay[0,0])

    return tw, m66, transfer_matrices, closed_orbit
