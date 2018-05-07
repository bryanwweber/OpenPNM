import scipy as sp
import numpy as np
import scipy.sparse as sprs
import scipy.sparse.csgraph as csg
import matplotlib.pyplot as plt
from collections import namedtuple
from openpnm.algorithms import GenericPercolation
from openpnm.topotools import site_percolation, bond_percolation
from openpnm.topotools import remove_isolated_clusters, ispercolating
from openpnm.core import logging
logger = logging.getLogger(__name__)

default_settings = {'access_limited': True,
                    'mode': 'bond',
                    'pore_entry_pressure': 'pore.capillary_pressure',
                    'throat_entry_pressure': 'throat.capillary_pressure',
                    'pore_volume': '',
                    'throat_volume': ''}


class OrdinaryPercolation(GenericPercolation):

    def __init__(self, settings={}, **kwargs):
        r"""
        """
        super().__init__(**kwargs)
        self.settings.update(default_settings)
        # Apply user settings, if any
        self.settings.update(settings)
        # Use the reset method to initialize all arrays
        self.reset()

    def setup(self,
              phase=None,
              access_limited=None,
              mode='',
              throat_entry_pressure='',
              pore_entry_pressure='',
              pore_volume='',
              throat_volume=''):
        r"""
        Used to specify necessary arguments to the simulation.  This method is
        useful for resetting the algorithm or applying more explicit control.

        Parameters
        ----------
        phase : OpenPNM Phase object
            The Phase object containing the physical properties of the invading
            fluid.

        access_limited : boolean
            If ``True`` the invading phase can only enter the network from the
            invasion sites specified with ``set_inlets``.  Otherwise, invading
            clusters can appear anywhere in the network.  This second case is
            the normal *ordinary percolation* in the traditional sense.

        mode : string
            Specifies the type of percolation process to simulate.  Options
            are:

            **'bond'** - The percolation process is controlled by bond entry
            thresholds.

            **'site'** - The percolation process is controlled by site entry
            thresholds.

        pore_entry_pressure : string
            The dictionary key on the Phase object where the pore entry
            pressure values are stored.  The default is
            'pore.capillary_pressure'.  This is only accessed if the ``mode``
            is set to site percolation.

        throat_entry_pressure : string
            The dictionary key on the Phase object where the throat entry
            pressure values are stored.  The default is
            'throat.capillary_pressure'.  This is only accessed if the ``mode``
            is set to bond percolation.

        'pore_volume' : string
            The dictionary key containing the pore volume information.

        'throat_volume' : string
            The dictionary key containing the pore volume information.

        """
        if phase:
            self.settings['phase'] = phase.name
        if throat_entry_pressure:
            self.settings['throat_entry_pressure'] = throat_entry_pressure
            phase = self.project.find_phase(self)
            self['throat.entry_pressure'] = phase[throat_entry_pressure]
        if pore_entry_pressure:
            self.settings['pore_entry_pressure'] = pore_entry_pressure
            phase = self.project.find_phase(self)
            self['pore.entry_pressure'] = phase[pore_entry_pressure]
        if mode:
            self.settings['mode'] = mode
        if access_limited is not None:
            self.settings['access_limited'] = access_limited

    def reset(self):
        r"""
        Resets the various data arrays on the object back to their original
        state. This is useful for repeating a simulation at different inlet
        conditions, or invasion points for instance.
        """
        self['pore.invasion_pressure'] = np.inf
        self['throat.invasion_pressure'] = np.inf
        self['pore.invasion_sequence'] = -1
        self['throat.invasion_sequence'] = -1
        self['pore.inlets'] = False
        self['pore.outlets'] = False
        self['pore.residual'] = False
        self['throat.residual'] = False

    def run(self, points=25, start=None, stop=None):
        r"""
        Runs the percolation algorithm to determine which pores and throats
        will be invaded at each given

        Parameters
        ----------
        points: int or array_like
            An array containing the pressure points to apply.  If a scalar is
            given then an array will be generated with the given number of
            points spaced between the lowest and highest values of throat
            entry pressures using logarithmic spacing.  To specify low and
            high pressure points use the ``start`` and ``stop`` arguments.

        start : int
            The optional starting point to use when generating pressure points.

        stop : int
            The optional stopping point to use when generating pressure points.

        """
        phase = self.project.find_phase(self)
        # Parse inputs and generate list of invasion points if necessary
        if self.settings['mode'] == 'bond':
            self['throat.entry_pressure'] = \
                phase[self.settings['throat_entry_pressure']]
            if type(points) is int:
                if start is None:
                    start = sp.amin(self['throat.entry_pressure'])*0.95
                if stop is None:
                    stop = sp.amax(self['throat.entry_pressure'])*1.05
                points = sp.logspace(start=sp.log10(max(1, start)),
                                     stop=sp.log10(stop),
                                     num=points)
        elif self.settings['mode'] == 'site':
            self['pore.entry_pressure'] = \
                phase[self.settings['pore_entry_pressure']]
            if type(points) is int:
                if start is None:
                    start = sp.amin(self['pore.entry_pressure'])*0.95
                if stop is None:
                    stop = sp.amax(self['pore.entry_pressure'])*1.05
                points = sp.logspace(start=sp.log10(max(1, start)),
                                     stop=sp.log10(stop),
                                     num=points)
        else:
            raise Exception('Percolation type has not been set')
        # Ensure pore inlets have been set IF access limitations is True
        if self.settings['access_limited']:
            if sp.sum(self['pore.inlets']) == 0:
                raise Exception('Inlet pores must be specified first')
            else:
                Pin = self['pore.inlets']

        # Generate curve from points
        conns = self.project.network['throat.conns']
        for inv_val in points:
            if self.settings['mode'] == 'bond':
                t_invaded = self['throat.entry_pressure'] <= inv_val
                labels = bond_percolation(conns, t_invaded)
            elif self.settings['mode'] == 'site':
                p_invaded = self['pore.entry_pressure'] <= inv_val
                labels = site_percolation(conns, p_invaded)

            # Optionally remove clusters not connected to the inlets
            if self.settings['access_limited']:
                labels = remove_isolated_clusters(labels=labels,
                                                       inlets=Pin)

            # Store current applied pressure in newly invaded pores
            pinds = (self['pore.invasion_pressure'] == sp.inf) * \
                    (labels.sites >= 0)
            self['pore.invasion_pressure'][pinds] = inv_val
            # Store current applied pressure in newly invaded throats
            tinds = (self['throat.invasion_pressure'] == sp.inf) * \
                    (labels.bonds >= 0)
            self['throat.invasion_pressure'][tinds] = inv_val

        # Convert invasion pressures in sequence values
        Pinv = self['pore.invasion_pressure']
        Tinv = self['throat.invasion_pressure']
        Pseq = sp.searchsorted(sp.unique(Pinv), Pinv)
        Tseq = sp.searchsorted(sp.unique(Tinv), Tinv)
        self['pore.invasion_sequence'] = Pseq
        self['throat.invasion_sequence'] = Tseq

    def get_percolation_threshold(self):
        r"""
        """
        if sp.sum(self['pore.inlets']) == 0:
            raise Exception('Inlet pores must be specified first')
        if sp.sum(self['pore.outlets']) == 0:
            raise Exception('Outlet pores must be specified first')
        else:
            Pout = self['pore.outlets']
        # Do a simple check of pressures on the outlet pores first...
        if self.settings['access_limited']:
            thresh = sp.amin(self['pore.invasion_pressure'][Pout])
        else:
            raise Exception('This is currently only implemented for access ' +
                            'limited simulations')
        return thresh

    def is_percolating(self, applied_pressure):
        r"""
        Returns a True or False value to indicate if a percolating cluster
        spans between the inlet and outlet pores that were specified.

        Parameters
        ----------
        applied_pressure : scalar, float
            The pressure at which percolation should be checked

        Returns
        -------
        A simple boolean True or False if percolation has occured or not.

        """
        if sp.sum(self['pore.inlets']) == 0:
            raise Exception('Inlet pores must be specified first')
        else:
            Pin = self['pore.inlets']
        if sp.sum(self['pore.outlets']) == 0:
            raise Exception('Outlet pores must be specified first')
        else:
            Pout = self['pore.outlets']
        # Do a simple check of pressures on the outlet pores first...
        if sp.amin(self['pore.invasion_pressure'][Pout]) > applied_pressure:
            val = False
        else:  # ... and do a rigorous check only if necessary
            mask = self['throat.invasion_pressure'] < applied_pressure
            am = self.project.network.create_adjacency_matrix(weights=mask,
                                                              fmt='coo')
            val = self._is_percolating(am=am, mode=self.settings['mode'],
                                       inlets=Pin, outlets=Pout)
        return val

    def results(self, Pc):
        r"""
        This method determines which pores and throats are filled with invading
        phase at the specified capillary pressure, and creates several arrays
        indicating the occupancy status of each pore and throat for the given
        pressure.

        Parameters
        ----------
        Pc : scalar
            The capillary pressure for which an invading phase configuration
            is desired.

        Returns
        -------
        A dictionary containing an assortment of data about distribution
        of the invading phase at the specified capillary pressure.  The data
        include:

        **'pore.occupancy'** : A value between 0 and 1 indicating the
        fractional volume of each pore that is invaded.  If no late pore
        filling model was applied, then this will only be integer values
        (either filled or not).

        **'throat.occupancy'** : The same as 'pore.occupancy' but for throats.

        This dictionary can be passed directly to the ``update`` method of
        the *Phase* object. These values can then be accessed by models
        or algorithms.

        """
        Psatn = self['pore.invasion_pressure'] <= Pc
        Tsatn = self['throat.invasion_pressure'] <= Pc
        inv_phase = {}
        inv_phase['pore.occupancy'] = sp.array(Psatn, dtype=float)
        inv_phase['throat.occupancy'] = sp.array(Tsatn, dtype=float)
        return inv_phase

    def get_percolation_data(self):
        r"""
        Obtain the numerical values of the calculated percolation curve

        Returns
        -------
        A named-tuple containing arrays of applied capillary pressures and
        invading phase saturation.

        """
        net = self.project.network
        # Infer list of applied capillary pressures
        points = np.unique(self['throat.invasion_pressure'])
        # Add a low pressure point to the list to improve graph
        points = np.concatenate(([0], points))
        if points[-1] == np.inf:  # Remove infinity from PcPoints if present
            points = points[:-1]
        # Get pore and throat volumes
        if self.settings['pore_volume']:
            Pvol = net[self.settings['pore_volume']]
        else:
            Pvol = sp.ones(shape=(self.Np, ), dtype=int)
        if self.settings['throat_volume']:
            Tvol = net[self.settings['throat_volume']]
        else:
            Tvol = sp.zeros(shape=(self.Nt, ), dtype=int)
        Total_vol = np.sum(Pvol) + np.sum(Tvol)
        # Find cumulative filled volume at each applied capillary pressure
        Vnwp_t = []
        Vnwp_p = []
        Vnwp_all = []
        for p in points:
            # Calculate filled pore volumes
            p_inv = self['pore.invasion_pressure'] <= p
            Vp = np.sum(Pvol[p_inv])
            # Calculate filled throat volumes
            t_inv = self['throat.invasion_pressure'] <= p
            Vt = np.sum(Tvol[t_inv])
            Vnwp_p.append(Vp)
            Vnwp_t.append(Vt)
            Vnwp_all.append(Vp + Vt)
        # Convert volumes to saturations by normalizing with total pore volume
        Snwp_all = [V/Total_vol for V in Vnwp_all]
        pc_curve = namedtuple('pc_curve', ('Pcap', 'Snwp'))
        data = pc_curve(points, Snwp_all)
        return data

    def plot_percolation_curve(self):
        r"""
        Plot the percolation curve as the invader volume or number fraction vs
        the applied capillary pressure.

        """
        # Begin creating nicely formatted plot
        data = self.get_percolation_data()
        xdata = data.Pcap
        ydata = data.Snwp
        fig = plt.figure()
        plt.semilogx(xdata, ydata, 'ko-')
        plt.ylabel('Invading Phase Saturation')
        plt.xlabel('Capillary Pressure')
        plt.grid(True)
        if np.amax(xdata) <= 1:
            plt.xlim(xmin=0, xmax=1)
        if np.amax(ydata) <= 1:
            plt.ylim(ymin=0, ymax=1)
        return fig
