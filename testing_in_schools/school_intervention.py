from covasim.interventions import Intervention
import covasim.base as cvb
from school import School

class new_schools(Intervention):
    '''
    Specifies reopening strategy.

    Args:
        ili_prev    (float or dict)     : Prevalence of influenza-like-illness symptoms in the population
        num_pos     (int)               : number of covid positive cases per school that triggers school closure
        trace       (float)             : probability of tracing contacts of diagnosed covid+
        test        (float)             : probability of testing screen positive
        test_freq   (int)               : frequency of testing teachers (1 = daily, 2 = every other day, ...)
        is_hybrid   (bool or dict)      : whether or not to schedule partially remote (if dict, by type, otherwise for all types)
        kwargs      (dict)              : passed to Intervention

    **Examples**
        TODO
    '''

    def __init__(self, scenario, **kwargs):
        super().__init__(**kwargs) # Initialize the Intervention object
        self._store_args() # Store the input arguments so that intervention can be recreated

        # Store arguments
        '''
        self.start_day  = start_day
        self.ili_prev   = ili_prev
        self.test_freq  = test_freq # int of frequency of diagnostic testing
        self.trace_prob = trace_prob # whether or not you trace contacts of all diagnosed patients
        self.test_prob  = test_prob # probability that anyone who screens positive is tested
        self.is_hybrid   = is_hybrid # dictionary
        '''
        self.scenario = scenario
        self.schools = []

    def initialize(self, sim):
        # Create schools
        self.school_types = sim.people.school_types # Dict with keys of school types (e.g. 'es') and values of list of school ids (e.g. [1,5])

        sdf = sim.people.contacts['s'].to_df()
        sim.school_stats = {}

        for school_type, scids in self.school_types.items():
            for school_id in scids:
                uids = sim.people.schools[school_id] # Dict with keys of school_id and values of uids in that school
                students = [u for u in uids if sim.people.student_flag[u]]
                staff = [u for u in uids if sim.people.staff_flag[u]]
                teachers = [u for u in uids if sim.people.teacher_flag[u]]

                stats = {
                    'type':         school_type,
                    'scenario':     self.scenario[school_type],
                }
                sim.school_stats[school_id] = stats

                if self.scenario[school_type] is not None:
                    # Extract 's'-layer associated with this school
                    rows = (sdf['p1'].isin(uids)) | (sdf['p2'].isin(uids))
                    s_subset = sdf.loc[ rows ]
                    sdf = sdf.loc[ ~rows ] # Remove rows from the 's' contacts
                    this_school_layer = cvb.Layer().from_df(s_subset)

                    sch = School(sim, school_id, school_type, uids, this_school_layer, **self.scenario[school_type])
                    self.schools.append(sch)

                    # Configure the new layer
                    sim['beta_layer'][sch.sid] = self.scenario[school_type]['npi'] * sim['beta_layer']['s']
                    sim['iso_factor'][sch.sid] = sim['iso_factor']['s']
                    sim['quar_factor'][sch.sid] = sim['quar_factor']['s']

        # Delete remaining entries in sim.people.contacts['s'], these were associated with schools that will not open, e.g. pk and uv
        sim.people.contacts['s'] = cvb.Layer()

        self.initialized = True

    def apply(self, sim):
        for school in self.schools:
            layer = school.update()
            sim.people.contacts[school.sid] = layer
            sim.school_stats[school.sid].update( school.get_stats() )

