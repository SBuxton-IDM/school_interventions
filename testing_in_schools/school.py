# Main class to implement school-based interventions

import covasim.base as cvb
import covasim.utils as cvu
import numpy as np
import sciris as sc

class FullTimeContactManager():
    ''' Contact manager for regular 5-day-per-week school '''

    def __init__(self, sim, uids, layer):
        self.uids = uids
        self.base_layer = layer
        self.school_day = False

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
        ''' Called at the beginning of each day to configure the school layer '''

        dayname = sc.readdate(date).strftime('%A')
        group = self.schedule[dayname]
        self.school_day = group == 'all'

        # Could modify layer based on group
        if group == 'all':
            # Start with the original layer, will remove uids at home later
            self.layer = sc.dcp(self.base_layer) # needed?
            uids = self.uids
        else:
            self.layer = cvb.Layer() # Empty
            uids = []

        return uids # Everyone is scheduled for school today, unless it's a weekend

    def remove_individuals(self, uids):
        ''' Remove one or more individual from the contact network '''

        rows = np.concatenate((
            np.isin(self.layer['p1'], uids).nonzero()[0],
            np.isin(self.layer['p2'], uids).nonzero()[0]))
        pop = self.layer.pop_inds(rows)


    def find_contacts(self, uids):
        ''' Finds contacts of individuals listed in uids, including those who are absent from school '''

        return self.base_layer.find_contacts(uids)

    def get_layer(self):
        ''' Return the layer '''

        return self.layer


class HybridContactManager():
    ''' Contact manager for hybrid school '''

    def __init__(self, sim, uids, layer):
        self.sim = sim
        self.uids = uids
        self.base_layer = layer
        self.A_base_layer, self.B_base_layer = self.split_layer()
        self.school_day = False

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
        ''' Split the layer into A- and B-sublayers '''
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
        ''' Called at the beginning of each day to configure the school layer '''
        dayname = sc.readdate(date).strftime('%A')
        group = self.schedule[dayname]
        self.school_day = group in ['A', 'B']

        # Could modify layer based on group
        if group == 'A':
            self.layer = sc.dcp(self.A_base_layer) # needed?
            uids = self.A_group
        elif group == 'B':
            self.layer = sc.dcp(self.B_base_layer) # needed?
            uids = self.B_group
        else:
            uids = []
            self.layer = cvb.Layer() # Empty

        return uids # Hybrid scheduling

    def remove_individuals(self, uids):
        ''' Remove one or more individual from the contact network '''

        rows = np.concatenate((
            np.isin(self.layer['p1'], uids).nonzero()[0],
            np.isin(self.layer['p2'], uids).nonzero()[0]))
        pop = self.layer.pop_inds(rows)

    def find_contacts(self, uids):
        ''' Finds contacts of individuals listed in uids, including those who are absent from school.
            Look in A_base_layer as well as B_base_layer for uids and return contacts.
            Join together contacts of A-students in A-layer with B-students in B-layer
        '''

        contacts = np.concatenate((
            self.A_base_layer.find_contacts(uids),
            self.B_base_layer.find_contacts(uids) ))
        return contacts

    def get_layer(self):
        ''' Return the layer '''

        return self.layer

class RemoteContactManager():
    ''' Contact manager for remote school '''

    def __init__(self, sim, uids, layer):
        self.uids = uids
        self.base_layer = cvb.Layer() # Empty base layer (ignore the passed-in layer)
        self.school_day = False

    def begin_day(self, date):
        ''' Called at the beginning of each day to configure the school layer '''

        self.layer = cvb.Layer() # Empty
        uids = []

        return uids

    def remove_individuals(self, uids):
        ''' No individuals to remove, so just return '''
        return

    def find_contacts(self, uids):
        ''' No contacts because remote, return empty list '''
        return np.empty(0)

    def get_layer(self):
        ''' Return the (empty) layer '''
        return self.layer


class SchoolStats():
    ''' Reporter for tracking statistics associated with a school '''

    def __init__(self, school):
        self.school = school

        zero_vec = [0] * self.school.sim.npts

        ppl = self.school.sim.people
        pop_scale = self.school.sim.pars['pop_scale']
        student_uids = [uid for uid in self.school.uids if ppl.student_flag[uid]]
        teacher_uids = [uid for uid in self.school.uids if ppl.teacher_flag[uid]]
        staff_uids = [uid for uid in self.school.uids if ppl.staff_flag[uid]]
        self.num = {
            'students':   len(student_uids) * pop_scale,
            'teachers':   len(teacher_uids) * pop_scale,
            'staff':      len(staff_uids) * pop_scale,
        }

        self.num_school_days = 0

        self.infectious = {
            'students': sc.dcp(zero_vec),
            'teachers': sc.dcp(zero_vec),
            'staff':    sc.dcp(zero_vec),
        }

        self.infectious_arrive_at_school = {
            'students': sc.dcp(zero_vec),
            'teachers': sc.dcp(zero_vec),
            'staff':    sc.dcp(zero_vec),
        }

        self.infectious_stay_at_school = {
            'students': sc.dcp(zero_vec),
            'teachers': sc.dcp(zero_vec),
            'staff':    sc.dcp(zero_vec),
        }

        self.newly_exposed = {
            'students': sc.dcp(zero_vec),
            'teachers': sc.dcp(zero_vec),
            'staff':    sc.dcp(zero_vec),
        }

        self.scheduled = {
            'students': sc.dcp(zero_vec),
            'teachers': sc.dcp(zero_vec),
            'staff':    sc.dcp(zero_vec),
        }

        self.in_person = {
            'students': sc.dcp(zero_vec),
            'teachers': sc.dcp(zero_vec),
            'staff':    sc.dcp(zero_vec),
        }

    def update(self):
        ''' Called on each day to update school statistics '''

        t = self.school.sim.t
        ppl = self.school.sim.people
        rescale = self.school.sim.rescale_vec[t]

        if self.school.ct_mgr.school_day:
            self.num_school_days += 1

        student_uids = [uid for uid in self.school.uids if ppl.student_flag[uid]]
        teacher_uids = [uid for uid in self.school.uids if ppl.teacher_flag[uid]]
        staff_uids = [uid for uid in self.school.uids if ppl.staff_flag[uid]]

        for group, ids in zip(['students', 'teachers', 'staff'], [student_uids, teacher_uids, staff_uids]):
            self.infectious[group][t] = len(cvu.true(ppl.infectious[ids])) * rescale
            self.newly_exposed[group][t] = len(cvu.true(ppl.date_exposed[ids] == t-1)) * rescale
            self.scheduled[group][t] = len([u for u in self.school.scheduled_uids if u in ids]) * rescale # Scheduled
            self.in_person[group][t] = len([u for u in self.school.uids_passed_screening if u in ids]) * rescale # Post-screening

        # Tracing statistics to compare against previous work:
        if len(self.school.uids_arriving_at_school) > 0:
            school_infectious = cvu.itrue(ppl.infectious[np.array(self.school.uids_arriving_at_school)], np.array(self.school.uids_arriving_at_school))
        else:
            school_infectious = []

        # Options here: (TODO - avoid code replication)
        # 1. Use ids of students who arrived as school (pre-screening): self.school.uids_arriving_at_school (pre-screening)
        # 2. Use ids of students who passed screening: self.school.uids_passed_screening
        # First "infectious_arrive_at_school" assumes there is a transmission risk even pre-screening (e.g. bus)
        students_at_school_uids = [uid for uid in self.school.uids_arriving_at_school if ppl.student_flag[uid]]
        teachers_at_school_uids = [uid for uid in self.school.uids_arriving_at_school if ppl.teacher_flag[uid]]
        staff_at_school_uids = [uid for uid in self.school.uids_arriving_at_school if ppl.staff_flag[uid]]
        for group, ids in zip(['students', 'teachers', 'staff'], [students_at_school_uids, teachers_at_school_uids, staff_at_school_uids]):
            self.infectious_arrive_at_school[group][t] = sum(ppl.infectious[ids]) * rescale

        # Second "infectious_stay_at_school" effectively assumes "screen-positive" kids would be kept home from school in the first place
        students_at_school_uids = [uid for uid in self.school.uids_passed_screening if ppl.student_flag[uid]]
        teachers_at_school_uids = [uid for uid in self.school.uids_passed_screening if ppl.teacher_flag[uid]]
        staff_at_school_uids = [uid for uid in self.school.uids_passed_screening if ppl.staff_flag[uid]]
        for group, ids in zip(['students', 'teachers', 'staff'], [students_at_school_uids, teachers_at_school_uids, staff_at_school_uids]):
            self.infectious_stay_at_school[group][t] = sum(ppl.infectious[ids]) * rescale

    def finalize(self):
        ''' Called once on the final time step '''
        return


    def get(self):
        ''' Called once on the final time step to return a dictionary that will be preserved in sim.school_info by school id. '''

        return {
            'num': self.num,
            'infectious': self.infectious,
            'infectious_arrive_at_school': self.infectious_arrive_at_school,
            'infectious_stay_at_school': self.infectious_stay_at_school,
            'newly_exposed': self.newly_exposed,
            'scheduled': self.scheduled,
            'in_person': self.in_person,
            'num_school_days': self.num_school_days,
            'n_tested': self.school.testing.n_tested,
        }




class SchoolTesting():
    '''
    Conduct testing in school students and staff.

    N.B. screening with follow-up testing is handled in the School class.
    '''

    def __init__(self, school, testing):
        ''' Initialize testing. '''

        self.school = school
        self.testing = [] if testing is None else sc.dcp(testing)

        for test in self.testing:
            if 'is_antigen' not in test:
                test['is_antigen'] = False
            test['type'] = 'Antigen' if test['is_antigen'] else 'PCR'

        self.n_tested = { 'PCR': 0, 'Antigen': 0 }

        for test in self.testing:
            # Determine from test start_day and repeat which sim times to test on
            start_t = self.school.sim.day(test['start_date'])
            if test['repeat'] == None:
                # Easy - one time test
                test['t_vec'] = [start_t]
            else:
                test['t_vec'] = list(range(start_t, self.school.sim.pars['n_days'], test['repeat']))

            # Determine uids to include
            uids = []
            ppl = self.school.sim.people
            if 'students' in test['groups']:
                uids += [uid for uid in self.school.uids if ppl.student_flag[uid]]
            if 'staff' in test['groups']:
                uids += [uid for uid in self.school.uids if ppl.staff_flag[uid]]
            if 'teachers' in test['groups']:
                uids += [uid for uid in self.school.uids if ppl.teacher_flag[uid]]
            test['uids'] = uids


    def antigen_test(self, inds, sym7d_sens=1.0, other_sens=1.0, specificity=1, loss_prob=0.0):
        '''
        Adapted from the test() method on sim.people to do antigen testing. Main change is that sensitivity is now broken into those symptomatic in the past week and others.

        Args:
            inds: indices of who to test
            sym7d_sens (float): probability of a true positive in a recently symptomatic individual (7d)
            other_sens (float): probability of a true positive in others
            loss_prob (float): probability of loss to follow-up
            delay (int): number of days before test results are ready
        '''

        ppl = self.school.sim.people
        t = self.school.sim.t

        inds = np.unique(inds)
        # Antigen tests don't count towards stats (yet)
        #ppl.tested[inds] = True
        #ppl.date_tested[inds] = t # Only keep the last time they tested
        #ppl.date_results[inds] = t + delay # Keep date when next results will be returned

        is_infectious = cvu.itruei(ppl.infectious, inds)
        symp = is_infectious[~np.isnan(ppl.date_symptomatic[is_infectious])]
        recently_symp_inds = symp[ t-ppl.date_symptomatic[symp] < 7 ]
        other_inds = np.setdiff1d(is_infectious, recently_symp_inds)

        is_inf_pos = np.concatenate((
            cvu.binomial_filter(sym7d_sens, recently_symp_inds), # Higher sensitivity for <7 days
            cvu.binomial_filter(other_sens, other_inds)          # Lower sensitivity of otheres
        ))

        not_diagnosed      = is_inf_pos[np.isnan(ppl.date_diagnosed[is_inf_pos])]
        not_lost           = cvu.n_binomial(1.0-loss_prob, len(not_diagnosed))
        true_positive_uids = not_diagnosed[not_lost]

        # Store the date the person will be diagnosed, as well as the date they took the test which will come back positive
        # Not for antigen tests?  date_diagnosed would interfere with later PCR.
        #ppl.date_diagnosed[true_positive_uids] = t + delay
        #ppl.date_pos_test[true_positive_uids] = t

        # False positivies
        if specificity < 1:
            non_infectious_uids = np.setdiff1d(inds, is_infectious)
            false_positive_uids = cvu.binomial_filter(1-specificity, non_infectious_uids)
        else:
            false_positive_uids = np.empty(0, dtype=np.int64)

        return np.concatenate((true_positive_uids, false_positive_uids))


    def update(self):
        '''
        Check for testing today and conduct tests if needed.
        True positives return via date_diagnosed, false positives are returned via this function.

        Fields include:
            * 'start_date': '2020-08-29',
            * 'repeat': None,
            * 'groups': ['students', 'teachers', 'staff'],
            * 'coverage': 0.9,
            * 'sensitivity': 1,
            * 'delay': 1,
            * TODO: 'specificity': 1,
        '''

        false_positive_uids = []
        ppl = self.school.sim.people
        t = self.school.sim.t
        ids_to_iso = {}
        for test in self.testing:
            if self.school.sim.t in test['t_vec']:
                undiagnosed_uids = cvu.ifalsei(ppl.diagnosed, np.array(test['uids']))
                uids_to_test = cvu.binomial_filter(test['coverage'], undiagnosed_uids)
                self.n_tested[test['type']] += len(uids_to_test)

                if self.school.verbose: print(self.school.sim.t, f'School {self.school.sid} of type {self.school.stype} is testing {len(uids_to_test)} today')

                if test['is_antigen']:
                    ag_pos_uids = self.antigen_test(uids_to_test, sym7d_sens=test['symp7d_sensitivity'], other_sens=test['other_sensitivity'], specificity=test['specificity'])

                    pcr_fu_uids = cvu.binomial_filter(test['PCR_followup_perc'], ag_pos_uids)
                    ppl.test(pcr_fu_uids, test_sensitivity=1.0, test_delay=test['PCR_followup_delay'])
                    #self.school.sim.results['new_tests'][t] += len(pcr_fu_uids)
                    self.n_tested['PCR'] += len(pcr_fu_uids) # Also add follow-up PCR tests

                    ids_to_iso = {uid:t+test['PCR_followup_delay'] for uid in pcr_fu_uids}
                    non_pcr_uids = np.setdiff1d(ag_pos_uids, pcr_fu_uids)
                    ids_to_iso.update({uid:t+self.school.sim.pars['quar_period'] for uid in non_pcr_uids})
                else:
                    ppl.test(uids_to_test, test_sensitivity=test['sensitivity'], test_delay=test['delay'])
                    #self.school.sim.results['new_tests'][t] += len(uids_to_test)
                    # N.B. No false positives for PCR

        return ids_to_iso


class School():
    ''' Represent a single school '''

    def __init__(self, sim, school_id, school_type, uids, layer,
                start_day, screen_prob, screen2pcr, test_prob, trace_prob, quar_prob, schedule, beta_s, ili_prob, testing, verbose=False, **kwargs):
        '''
        Initialize the School

        sim          (covasim Sim)  : Pointer to the simulation object
        school_id    (int)          : ID of this school
        school_type  (str)          : Type of this school in pk, es, ms, hs, uv
        uids         (array)        : Array of ids of individuals associated with this school
        layer        (Layer)        : The fragment of the original 's' network associated with this school
        start_day    (str)          : Opening day for school
        screen_prob  (float)        : Coverage of screening
        test_prob    (float)        : Probability of PCR testing on screen +
        screen2pcr   (int)          : Days between positive screening receiving PCR results, for those testing
        trace_prob   (float)        : Probability of tracing from PCR+
        quar_prob    (float)        : Probability school contacts quarantine on trace
        schedule     (str)          : Full, Hybrid, or Remote
        beta_s       (float)        : beta for this school
        ili_prob     (float)        : Daily probability of ILI
        testing      (struct)       : List of dictionaries of parameters for SchoolTesting
        '''

        self.sim = sim
        self.sid = school_id
        self.stype = school_type
        self.uids = uids
        self.start_day = start_day
        self.screen_prob = screen_prob
        self.screen2pcr = screen2pcr
        self.test_prob = test_prob
        self.trace_prob = trace_prob
        self.quar_prob = quar_prob
        self.schedule = schedule
        self.beta_s = beta_s # Not currently used here, but rather in the school_intervention
        self.ili_prob = ili_prob
        self.verbose = verbose

        self.is_open = False # Schools start closed

        self.uids_at_home = {} # Dict from uid to release date

        if self.schedule.lower() == 'hybrid':
            self.ct_mgr = HybridContactManager(sim, uids, layer)
        elif self.schedule.lower() == 'full':
            self.ct_mgr = FullTimeContactManager(sim, uids, layer)
        elif self.schedule.lower() == 'remote':
            self.ct_mgr = RemoteContactManager(sim, uids, layer)
        else:
            print(f'Warning: Unrecognized schedule ({self.schedule}) passed to School class.')

        self.stats = SchoolStats(self)
        self.testing = SchoolTesting(self, testing)

    def screen(self):
        ''' Screen those individuals who are arriving at school '''

        # Inclusion criteria: diagnosed or symptomatic but not recovered and not dead
        inds_to_screen = cvu.binomial_filter(self.screen_prob, np.array(self.uids_arriving_at_school))
        if len(inds_to_screen) == 0:
            return []

        symp = self.sim.people.symptomatic[inds_to_screen]

        rec_or_dead = np.logical_or(
            self.sim.people.recovered[inds_to_screen],
            self.sim.people.dead[inds_to_screen])

        screen_pos = np.logical_and(symp, ~rec_or_dead)
        screen_pos_uids = cvu.itrue(screen_pos, np.array(inds_to_screen))

        inf = [z for z in self.uids_arriving_at_school if self.sim.people.infectious[z]]
        inf_post_screen = [z for z in inf if z not in screen_pos_uids]

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

        # Even if a school is not yet open, consider testing in the population
        ids_to_iso = self.testing.update()
        self.uids_at_home.update(ids_to_iso)

        # Look for newly diagnosed people (by PCR)
        newly_dx_inds = cvu.itrue(self.sim.people.date_diagnosed[self.uids] == self.sim.t, np.array(self.uids)) # Diagnosed this time step, time to trace

        if self.verbose and len(newly_dx_inds)>0: print(self.sim.t, f'School {self.sid} has {len(newly_dx_inds)} newly diagnosed: {newly_dx_inds}', [self.sim.people.date_exposed[u] for u in newly_dx_inds], 'recovering', [self.sim.people.date_recovered[u] for u in newly_dx_inds])

        # Isolate newly diagnosed individuals - could happen before school starts
        for uid in newly_dx_inds:
            self.uids_at_home[uid] = self.sim.t + self.sim.pars['quar_period'] # Can come back after quarantine period

        # If any individuals are done with quarantine, return them to school
        self.uids_at_home = {uid:date for uid,date in self.uids_at_home.items() if date >= self.sim.t} # >= or =?

        # Check if school is open
        if not self.is_open:
            if self.sim.t == self.sim.day(self.start_day):
                if self.verbose:
                    print(self.sim.t, self.sid, f'School {self.sid} is opening today with {len(self.uids_at_home)} at home: {self.uids_at_home}')

                    infectious_uids = cvu.itrue(self.sim.people.infectious[self.uids], np.array(self.uids))
                    print(self.sim.t, self.sid, 'Infectious:', len(cvu.true(self.sim.people.infectious[self.uids])) * self.sim.rescale_vec[self.sim.t], len(infectious_uids) )
                    print(self.sim.t, self.sid, 'Iuids:', infectious_uids)
                    print(self.sim.t, self.sid, 'Itime:', [self.sim.people.date_exposed[u] for u in infectious_uids])
                self.is_open = True
            else:
                # CLOSED SCHOOLS DO NOT PASS THIS POINT!
                return cvb.Layer() # Might be faster to cache

        date = self.sim.date(self.sim.t)
        self.scheduled_uids = self.ct_mgr.begin_day(date) # Call at the beginning of the update

        # Quarantine contacts of newly diagnosed individuals - # TODO: Schedule in a delay
        if len(newly_dx_inds) > 0:
            # Identify school contacts to quarantine
            uids_to_trace = cvu.binomial_filter(self.trace_prob, newly_dx_inds)
            uids_reached_by_tracing = self.ct_mgr.find_contacts(uids_to_trace) # Assume all contacts of traced individuals will quarantine
            uids_to_quar = cvu.binomial_filter(self.quar_prob, uids_reached_by_tracing)

            # Quarantine school contacts
            for uid in uids_to_quar:
                self.uids_at_home[uid] = self.sim.t + self.sim.pars['quar_period'] # Can come back after quarantine period

            # N.B. Not intentionally testing those in quarantine other than what covasim already does

        # Determine who will arrive at school (used in screen() and stats.update())
        self.uids_arriving_at_school = [u for u in self.scheduled_uids if u not in self.uids_at_home.keys()]

        # Perform symptom screening
        screen_pos_ids = self.screen()

        if len(screen_pos_ids) > 0:
            # Perform follow-up testing on some
            uids_to_test = cvu.binomial_filter(self.test_prob, screen_pos_ids)
            self.sim.people.test(uids_to_test, test_delay=self.screen2pcr)
            #self.sim.results['new_tests'][t] += len(uids_to_test)
            self.testing.n_tested['PCR'] += len(uids_to_test) # Ugly, move all testing in to the SchoolTesting class!

            # Send the screen positives home - quar_period if no PCR and otherwise the time to the PCR
            for uid in uids_to_test:
                self.uids_at_home[uid] = self.sim.t + self.screen2pcr # Can come back after PCR results are in

            for uid in np.setdiff1d(screen_pos_ids, uids_to_test):
                self.uids_at_home[uid] = self.sim.t + self.sim.pars['quar_period'] # Can come back after quarantine period


        # Determine (for tracking, mostly) who has arrived at school and passed symptom screening
        self.uids_passed_screening = [u for u in self.scheduled_uids if u not in self.uids_at_home.keys()]

        # Remove individuals at home from the network
        self.ct_mgr.remove_individuals(list(self.uids_at_home.keys()))

        self.stats.update()
        if self.sim.t == self.sim.npts-1:
            self.stats.finalize()

        # Return what is left of the layer
        return self.ct_mgr.get_layer()

    def get_stats(self):
        ''' Return a dictionary of statistics '''

        return self.stats.get()
