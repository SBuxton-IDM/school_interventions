import covasim.base as cvb
import covasim.utils as cvu
import numpy as np
import sciris as sc

class FullTimeContactManager():
    ''' Contact manager for regular 5-day-per-week school '''

    def __init__(self, layer):
        self.base_layer = layer
        self.group = 'closed'

        self.schedule = {
            'Monday':    'all',
            'Tuesday':   'all',
            'Wednesday': 'all',
            'Thursday':  'all',
            'Friday':    'all',
            'Saturday':  'weekend',
            'Sunday':    'weekend',
        }

    def begin_day(self, date):
        # Update group
        dayname = sc.readdate(date).strftime('%A')
        group = self.schedule[dayname]

        # Could modify layer based on group
        if group == 'all':
            # Start with the original layer, will remove uids at home later
            self.layer = sc.dcp(self.base_layer) # needed?
        else:
            self.layer = cvb.Layer() # Empty

    def remove_individuals(self, uids):
        ''' Remove one or more individual from the contact network '''
        #print(f'Removing {uids}')
        rows = np.concatenate((
            np.isin(self.layer['p1'], uids).nonzero()[0],
            np.isin(self.layer['p2'], uids).nonzero()[0]))
        pop = self.layer.pop_inds(rows)


    def find_contacts(self, uids):
        # Assumption: base_layer is close enough, not adjusting for absenteeism
        return self.base_layer.find_contacts(uids)

    def get_layer(self):
        return self.layer


class HybridContactManager():
    ''' Contact manager for hybrid school '''

    def __init__(self, sim, uids, layer):
        self.sim = sim
        self.uids = uids
        self.base_layer = layer
        self.A_base_layer, self.B_base_layer = self.split_layer()

        self.group = 'closed'

        self.schedule = {
            'Monday':    'A',
            'Tuesday':   'A',
            'Wednesday': 'distance',
            'Thursday':  'B',
            'Friday':    'B',
            'Saturday':  'weekend',
            'Sunday':    'weekend',
        }

    def split_layer(self):
        students = [uid for uid in self.uids if self.sim.people.student_flag[uid]]
        self.staff = [uid for uid in self.uids if self.sim.people.staff_flag[uid]]
        self.teachers = [uid for uid in self.uids if self.sim.people.teacher_flag[uid]]

        self.A_students = cvu.binomial_filter(0.5, np.array(students)).tolist()
        self.B_students = [uid for uid in students if uid not in self.A_students]

        self.A_group = self.A_students + self.teachers + self.staff
        self.B_group = self.B_students + self.teachers + self.staff

        A_layer = sc.dcp(self.base_layer)
        rows = np.concatenate((
                np.isin(A_layer['p1'], self.B_students).nonzero()[0],
                np.isin(A_layer['p2'], self.B_students).nonzero()[0]))

        B_layer = sc.dcp(self.base_layer)
        rows = np.concatenate((
                np.isin(B_layer['p1'], self.A_students).nonzero()[0],
                np.isin(B_layer['p2'], self.A_students).nonzero()[0]))
        pop = B_layer.pop_inds(rows)
        return A_layer, B_layer

    def begin_day(self, date):
        # Update group
        dayname = sc.readdate(date).strftime('%A')
        group = self.schedule[dayname]

        # Could modify layer based on group
        if group == 'A':
            self.layer = sc.dcp(self.A_base_layer) # needed?
        elif group == 'B':
            self.layer = sc.dcp(self.B_base_layer) # needed?
        else:
            self.layer = cvb.Layer() # Empty

    def remove_individuals(self, uids):
        ''' Remove one or more individual from the contact network '''

        rows = np.concatenate((
            np.isin(self.layer['p1'], uids).nonzero()[0],
            np.isin(self.layer['p2'], uids).nonzero()[0]))
        pop = self.layer.pop_inds(rows)

    def find_contacts(self, uids):
        contacts = np.concatenate((
            self.A_base_layer.find_contacts(uids),
            self.B_base_layer.find_contacts(uids) ))
        return contacts

    def get_layer(self):
        return self.layer


class SchoolStats():
    def __init__(self, school):
        self.school = school

        self.students_at_school_while_infectious = set()
        self.teacherstaff_at_school_while_infectious = set()

        self.n_students_at_school_while_infectious = [0] * len(self.school.sim.tvec)
        self.n_teacherstaff_at_school_while_infectious = [0] * len(self.school.sim.tvec)

    def update(self):
        stu_at_sch_uids = [uid for uid in self.school.uids_arriving_at_school if self.school.sim.people.student_flag[uid]]
        students_at_school_while_infectious_today = cvu.itrue(self.school.sim.people.infectious[stu_at_sch_uids], np.array(stu_at_sch_uids))
        self.students_at_school_while_infectious |= set(students_at_school_while_infectious_today)
        self.n_students_at_school_while_infectious[self.school.sim.t] = len(self.students_at_school_while_infectious)

        teacherstaff_at_sch_uids = [uid for uid in self.school.uids_arriving_at_school if self.school.sim.people.teacher_flag[uid] or self.school.sim.people.staff_flag[uid]]
        teacherstaff_at_school_while_infectious_today = cvu.itrue(self.school.sim.people.infectious[stu_at_sch_uids], np.array(stu_at_sch_uids))
        self.teacherstaff_at_school_while_infectious |= set(teacherstaff_at_school_while_infectious_today)
        self.n_teacherstaff_at_school_while_infectious[self.school.sim.t] = len(self.teacherstaff_at_school_while_infectious)

    def get(self):
        return {
            'n_students_at_school_while_infectious': self.n_students_at_school_while_infectious,
            'n_teacherstaff_at_school_while_infectious': self.n_teacherstaff_at_school_while_infectious,
        }


class School():

    def __init__(self, sim, school_id, school_type, uids, layer,
                start_day, screen_prob, test_prob, trace_prob, is_hybrid, npi, ili_prob, verbose=False, **kwargs):

        self.sim = sim
        self.sid = school_id
        self.stype = school_type
        self.uids = uids
        self.is_hybrid = is_hybrid
        self.start_day = start_day
        self.screen_prob = screen_prob
        self.test_prob = test_prob
        self.trace_prob = trace_prob
        self.is_hybrid = is_hybrid
        self.npi = npi
        self.ili_prob = ili_prob
        self.verbose = verbose

        self.stats = SchoolStats(self)

        self.is_open = False # Schools start closed

        self.uids_at_home = {} # Dict from uid to release date

        if self.is_hybrid:
            self.ct_mgr = HybridContactManager(sim, uids, layer)
        else:
            self.ct_mgr = FullTimeContactManager(layer)

    def screen(self):
        ''' Screen those at school '''

        # Inclusion criteria: diagnosed or symptomatic but not recovered and not dead
        inds_to_screen = cvu.binomial_filter(self.screen_prob, np.array(self.uids_arriving_at_school))
        if len(inds_to_screen) == 0:
            return []

        dx_or_sx = np.logical_or(
            self.sim.people.diagnosed[inds_to_screen],
            self.sim.people.symptomatic[inds_to_screen])

        rec_or_dead = np.logical_or(
            self.sim.people.recovered[inds_to_screen],
            self.sim.people.dead[inds_to_screen])

        screen_pos = np.logical_and(dx_or_sx, ~rec_or_dead)
        screen_pos_uids = cvu.itrue(screen_pos, np.array(inds_to_screen))

        # Add in screen positives from ILI amongst those who were screened negative
        if self.ili_prob is not None and self.ili_prob > 0:
            screen_neg_uids = np.array(inds_to_screen)[~screen_pos]
            n_ili = np.random.binomial(len(screen_neg_uids), self.ili_prob) # Poisson
            if n_ili > 0:
                ili_pos_uids = np.random.choice(screen_neg_uids, n_ili, replace=False)
                screen_pos_uids = np.concatenate((screen_pos_uids, ili_pos_uids))

        return screen_pos_uids

    def update(self):
        ''' Process the day, return the school layer '''

        # First check if school is open
        if not self.is_open:
            if self.sim.t == self.sim.day(self.start_day):
                if self.verbose: print(f'School {self.sid} is opening today')
                self.is_open = True
            else:
                return cvb.Layer() # Might be faster to cache

        date = self.sim.date(self.sim.t)
        self.ct_mgr.begin_day(date) # Do this at the beginning of the update

        # Look for newly diagnosed people
        newly_dx_inds = cvu.itrue(self.sim.people.date_diagnosed[self.uids] == self.sim.t, np.array(self.uids)) # Diagnosed this time step, time to trace

        # Isolate the positives
        if len(newly_dx_inds) > 0:
            for uid in newly_dx_inds:
                self.uids_at_home[uid] = self.sim.t + self.sim.pars['quar_period'] # Can come back after quarantine period

            # Identify school contacts to quarantine
            uids_to_trace = cvu.binomial_filter(self.trace_prob, newly_dx_inds)
            uids_to_quar = self.ct_mgr.find_contacts(uids_to_trace)

            # Quarantine school contacts
            for uid in uids_to_quar:
                self.uids_at_home[uid] = self.sim.t + self.sim.pars['quar_period'] # Can come back after quarantine period

        # If any individuals are done with quarantine, return them to school
        self.uids_at_home = {uid:date for uid,date in self.uids_at_home.items() if date > self.sim.t}

        if self.ct_mgr.group in ['weekend', 'distance']:
            # No school today, nothing more to do - return an empty layer
            return cvb.Layer()

        # Determine who will arrive at school
        self.uids_arriving_at_school = [u for u in self.uids if u not in self.uids_at_home.keys()]

        # Perform symptom screening
        # TODO: screen_prob
        screen_pos_ids = self.screen()

        if len(screen_pos_ids) > 0:
            # Send the screen positives home
            for uid in screen_pos_ids:
                self.uids_at_home[uid] = self.sim.t + 2 # Can come back in a few days, TODO: make a parameter

            # Perform follow-up testing on some
            uids_to_test = cvu.binomial_filter(self.test_prob, screen_pos_ids)
            self.sim.people.test(uids_to_test, test_delay=1) # one day test delay, TODO: Make a parameter!

        # Remove individuals at home from the network
        self.ct_mgr.remove_individuals(list(self.uids_at_home.keys()))

        self.stats.update()

        # Return what is left of the layer
        return self.ct_mgr.get_layer()

    def get_stats(self):
        return self.stats.get()
