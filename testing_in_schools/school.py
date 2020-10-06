import covasim.base as cvb
import numpy as np
import sciris as sc

class FullTimeContactManager():
    ''' Contact manager for regular 5-day-per-week school '''

    def __init__(self, layer):
        self.all_layer = layer
        self.cur_layer = layer
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

    def remove_individual(self, uids):
        ''' Remove one or more individual from the contact network '''
        rows = np.concatenate((
            np.isin(self.cur_layer['p1'], uids).nonzero()[0],
            np.isin(self.cur_layer['p2'], uids).nonzero()[0]))
        pop = self.cur_layer.pop_inds(rows)
        print('Pop:', pop)
        exit()
        return

    def get_layer(self):
        return self.cur_layer

    def begin_day(self, date):
        # Update group
        dayname = sc.readdate(date).strftime('%A')
        group = self.schedule[dayname]

        # Could modify layer based on group
        if group == 'all':
            self.cur_layer = self.all_layer
        else:
            self.cur_layer = cvb.Layer() # Empty



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
                start_day, test_frac, trace_frac, test_freq, is_hybrid, npi, ili, verbose=False, **kwargs):

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
        self.ili = ili
        self.verbose = verbose

        self.is_open = False # Schools start closed


        self.uids_at_home = [] # ? list per day to be able to easily return to school? Timer?

        if self.is_hybrid:
            print('Not implemented')
            exit()
        else:
            self.ct_mgr = FullTimeContactManager(layer)

    def screen(self):
        # Screen those at school
        ids_at_school_today = self.uids
        return

    def test_undiagnosed(self, student_frac=0, staff_frac=0, teacher_frac=0):
        # Administer diagnostic tests in individuals not already diagnosed
        # Exclude those home sick?
        return

    def _contact_trace(self, inds):
        return

    def update(self):
        # Process the day, return in school layer

        print(self.sim.t)
        exit()

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


        # Let's pretend to put some uids at home
        self.uids_at_home = self.uids[:2]

        # If any individuals are done with quarantine, return them to school

        # Perform symptom screening
        screen_pos_ids = self.screen()

        # Send the screen positives home

        # Perform follow-up testing on some
        covid_pos_ids = self.test(screen_pos_ids)

        # Isolate the positive ids

        # Identify school contacts

        # Quarantine school contacts


        # Remove individuals at home from the network
        self.ct_mgr.remove_individual(self.uids_at_home)
        exit()




        # Return what is left of the layer
        return self.ct_mgr.get_layer()
