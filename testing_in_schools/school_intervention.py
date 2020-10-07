from covasim.interventions import Intervention
import covasim.base as cvb
from school import School

class Scenario():
    def __init__(self):
        self.key = 'as_normal'
        self.label = 'As Normal'

        test_prob = 1
        trace_prob = 1
        ili_prob = 0.002

        self.scenario = {
            'pk': None,
            'es': {
                'start_day':  '2020-09-01',
                'test_prob':  test_prob,
                'trace_prob': trace_prob,
                'test_freq':  0,
                'is_hybrid':  False,
                'npi':        0.75,
                'daily_ili_prob': ili_prob
            },
            'ms': {
                'start_day':  '2020-09-01',
                'test_prob':  test_prob,
                'trace_prob': trace_prob,
                'test_freq':  0,
                'is_hybrid':  False,
                'npi':        0.75,
                'daily_ili_prob': ili_prob,
            },
            'hs': {
                'start_day':  '2020-09-01',
                'test_prob':  test_prob,
                'trace_prob': trace_prob,
                'test_freq':  0,
                'is_hybrid':  False,
                'npi':        0.75,
                'daily_ili_prob': ili_prob,
            },
            'uv': None,
        }


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

    #def __init__(self, start_day=None, ili_prev=None, test_freq=None, trace_prob=None, test_prob=None, is_hybrid=None, **kwargs):
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

        for school_type, scids in self.school_types.items():
            for school_id in scids:
                if self.scenario[school_type] is not None:
                    print(f'Createating school {school_id} of type {school_type}')
                    # Extract 's'-layer associated with this school
                    uids = sim.people.schools[school_id] # Dict with keys of school_id and values of uids in that school
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
                else:
                    print(f'Skipping school {school_id} of type {school_type}')

        # Delete remaining entries in sim.people.contacts['s'], these were associated with schools that will not open, e.g. pk and uv
        print(f'Removing remaining {sdf.shape[0]} school contacts as they are in schools that will not open')
        sim.people.contacts['s'] = cvb.Layer()

        self.initialized = True
        return


    def apply(self, sim):

        #t = sim.t
        #self.rescale = sim.rescale_vec[t] # Current rescaling factor for counts

        for school in self.schools:
            layer = school.update()
            sim.people.contacts[school.sid] = layer

        return

