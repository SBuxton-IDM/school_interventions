import covasim.base as cvb
import numpy as np
import sciris as sc

class FullTimeContactManager():
    ''' Contact manager for regular 5-day-per-week school '''

    def __init__(self, layer):
        self.orig_layer = layer
        #self.layer = layer
        self.group = 'closed'

        self.removed_contacts = {} # Dictionary uid: contacts | group?

        self.schedule = {
            'Monday':    'all',
            'Tuesday':   'all',
            'Wednesday': 'all',
            'Thursday':  'all',
            'Friday':    'all',
            'Saturday':  'no_school',
            'Sunday':    'no_school',
        }

    def begin_day(self, date):
        # Update group
        dayname = sc.readdate(date).strftime('%A')
        group = self.schedule[dayname]

        # Could modify layer based on group
        if group == 'all':
            # Start with the original layer, will remove uids at home later
            self.layer = self.orig_layer
        else:
            self.layer = cvb.Layer() # Empty

    def remove_individuals(self, uids):
        ''' Remove one or more individual from the contact network '''

        print(f'Removing {uids}')
        rows = np.concatenate((
            np.isin(self.layer['p1'], uids).nonzero()[0],
            np.isin(self.layer['p2'], uids).nonzero()[0]))
        pop = self.layer.pop_inds(rows)


    def get_layer(self):
        return self.layer



'''
# For hybrid contact manager
self.schedule = {
    'Monday':    'A',
    'Tuesday':   'A',
    'Wednesday': 'distance',
    'Thursday':  'B',
    'Friday':    'B',
    'Saturday':  'no_school',
    'Sunday':    'no_school',
}
'''

class School():

    def __init__(self, sim, school_id, school_type, uids, layer,
                start_day, test_frac, trace_frac, test_freq, is_hybrid, npi, daily_ili_prob, verbose=False, **kwargs):

        self.sim = sim
        self.sid = school_id
        self.stype = school_type
        self.uids = uids
        self.is_hybrid = is_hybrid
        self.start_day = start_day
        self.test_frac = test_frac
        self.trace_frac = trace_frac
        self.test_freq = test_freq
        self.is_hybrid = is_hybrid
        self.npi = npi
        self.ili_prob = daily_ili_prob
        self.verbose = verbose

        self.is_open = False # Schools start closed


        self.uids_at_home = {} # Dict from uid to release date

        if self.is_hybrid:
            print('Not implemented')
            exit()
        else:
            self.ct_mgr = FullTimeContactManager(layer)

    def screen(self):
        # Screen those at school

        # Inclusion criteria: diagnosed or symptomatic but not recovered and not dead
        dx_or_sx = np.logical_or(
            self.sim.people.diagnosed[self.uids_at_school],
            self.sim.people.symptomatic[self.uids_at_school])

        rec_or_dead = np.logical_or(
            self.sim.people.recovered[self.uids_at_school],
            self.sim.people.dead[self.uids_at_school])

        screen_pos = np.logical_and(dx_or_sx, ~rec_or_dead)
        screen_pos_uids = np.array(self.uids_at_school)[screen_pos] # list(compress(self.uids_at_school, screen_pos))

        # Add in screen positives from ILI
        if self.ili_prob is not None and self.ili_prob > 0:
            screen_neg_uids = np.array(self.uids_at_school)[~screen_pos]
            n_ili = np.random.binomial(len(screen_neg_uids), self.ili_prob) # Poisson
            if n_ili > 0:
                ili_pos_uids = np.random.choice(screen_neg_uids, n_ili, replace=False)
                screen_pos_uids = np.concatenate((screen_pos_uids, ili_pos_uids))

        return screen_pos_uids

    def test_undiagnosed(self, student_frac=0, staff_frac=0, teacher_frac=0):
        # Administer diagnostic tests in individuals not already diagnosed
        # Exclude those home sick?
        return

    def _contact_trace(self, inds):
        return

    def update(self):
        # Process the day, return in school layer

        # First check if school is open
        if not self.is_open:
            if self.sim.t == self.sim.day(self.start_day):
                if self.verbose: print(f'School {self.sid} is opening today')
                self.is_open = True
            else:
                return cvb.Layer() # Might be faster to cache

        date = self.sim.date(self.sim.t)
        self.ct_mgr.begin_day(date) # Do this first

        if self.ct_mgr.group == 'no_school':
            return cvb.Layer() # No school today


        # TEMP: Let's pretend to put some uids at home
        self.uids_at_home[self.uids[0]] = self.sim.t
        self.uids_at_home[self.uids[1]] = self.sim.t + self.sim.pars['quar_period']

        # If any individuals are done with quarantine, return them to school
        self.uids_at_home = {uid:date for uid,date in self.uids_at_home.items() if date > self.sim.t}

        # Everyone else is at school
        self.uids_at_school = [u for u in self.uids if u not in self.uids_at_home.keys()]

        # Perform symptom screening
        screen_pos_ids = self.screen()

        # Send the screen positives home (for 3 days...?)
        for uid in screen_pos_ids:
            self.uids_at_home[uid] = self.sim.t + 3 # Can come back tomorrow if test


        # Perform follow-up testing on some
        #covid_pos_ids = self.test(screen_pos_ids)

        # Isolate the positive ids

        # Identify school contacts

        # Quarantine school contacts


        # Remove individuals at home from the network
        self.ct_mgr.remove_individuals(list(self.uids_at_home.keys()))


        # Return what is left of the layer
        return self.ct_mgr.get_layer()