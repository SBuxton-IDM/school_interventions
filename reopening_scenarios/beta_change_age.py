import numpy as np
import sciris as sc
from covasim import defaults as cvd

from covasim.interventions import process_days, find_day, Intervention


def find_cutoff(age_cutoffs, age):
    '''
    Find which age bin each person belongs to -- e.g. with standard
    age bins 0, 10, 20, etc., ages [5, 12, 4, 58] would be mapped to
    indices [0, 1, 0, 5]. Age bins are not guaranteed to be uniform
    width, which is why this can't be done as an array operation.
    '''
    return np.nonzero(age_cutoffs <= age)[0][-1]  # Index of the age bin to use


def process_changes(trans_ORs, changes, days):
    '''
    Ensure lists of changes are in consistent format.
    '''
    changes = sc.promotetoarray(changes)
    if len(days) != len(changes):
        if len(days) == 1 and len(changes) == len(trans_ORs):
            changes = [changes]
        else:
            errormsg = f'Number of days supplied ({len(days)}) does not match number of changes ({len(changes)})'
            raise ValueError(errormsg)
    for i in range(len(changes)):
        changes[i] = sc.promotetoarray(changes[i])
        if len(changes[i]) != len(trans_ORs):
            if len(changes[i]) == 1:
                changes[i] = sc.promotetoarray([changes[i][0] for j in range(len(trans_ORs))])
            else:
                errormsg = f'Number of changes supplied ({len(changes[i])}) does not match number of age bins ({len(trans_ORs)})'
                raise ValueError(errormsg)
    return changes


class change_beta_age(Intervention):
    '''
    The most basic intervention with a twist-- change beta by age by a certain amount.

    Args:
        days (int or array): the day or array of days to apply the interventions
        changes (float, array, or array of arrays): the changes in beta (1 = no change, 0 = no transmission)
        kwargs (dict): passed to Intervention()

    **Examples**::

        interv = cv.change_beta(25, 0.3) # On day 25, reduce all ages transmission by 70% to 0.3 of original
        interv = cv.change_beta([14, 28], [[.10, .20, .30, .50, .50, .30, .20, .10, .01, .001], 1]) # On day 14, reduce transmission in all age groups but the most in the young and very old and on day 28, return to original for all groups
    '''

    def __init__(self, days, changes, **kwargs):
        super().__init__(**kwargs)  # Initialize the Intervention object
        self._store_args()  # Store the input arguments so the intervention can be recreated
        self.days = sc.dcp(days)
        self.changes = sc.dcp(changes)
        self.orig_rel_trans = None
        return

    def initialize(self, sim):
        ''' Fix days and store odds ratios '''
        self.trans_ORs = sc.promotetoarray(sim.pars['prognoses']['trans_ORs'])  # Shorten the name
        self.inds = np.fromiter(
            (find_cutoff(sim.pars['prognoses']['age_cutoffs'], this_age) for this_age in sim.people.age),
            dtype=cvd.default_int, count=len(sim.people))  # Convert ages to indices
        self.idx = 0

        self.days = process_days(sim, self.days)
        self.changes = process_changes(self.trans_ORs, self.changes, self.days)
        self.orig_rel_trans = sc.dcp(sim.people.rel_trans)

        self.initialized = True
        return

    def apply(self, sim):
        # If this day is found in the list, apply the intervention
        for ind in find_day(self.days, sim.t):
            sim.people.rel_trans[:] = self.orig_rel_trans * self.changes[self.idx][self.inds]
            self.idx += 1

        return