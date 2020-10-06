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
        schedule    (bool or dict)      : whether or not to schedule partially remote (if dict, by type, otherwise for all types)
        kwargs      (dict)              : passed to Intervention

    **Examples**
        TODO
    '''

    def __init__(self, start_day=None, ili_prev=None, test_freq=None, trace_frac=None, test_frac=None, schedule=None, **kwargs):
        super().__init__(**kwargs) # Initialize the Intervention object
        self._store_args() # Store the input arguments so that intervention can be recreated

        # Store arguments
        self.start_day  = start_day
        self.ili_prev   = ili_prev
        self.test_freq  = test_freq # int of frequency of diagnostic testing
        self.trace_frac = trace_frac # whether or not you trace contacts of all diagnosed patients
        self.test_frac  = test_frac # probability that anyone who screens positive is tested
        self.schedule   = schedule # dictionary

        self.schools = []

    def initialize(self, sim):
        # Create schools
        self.school_types = sim.people.school_types # Dict with keys of school types (e.g. 'es') and values of list of school ids (e.g. [1,5])

        sdf = sim.people.contacts['s'].to_df()

        for school_type, scids in self.school_types.items():
            for school_id in scids:
                uids = sim.people.schools[school_id] # Dict with keys of school_id and values of uids in that school
                print(school_type, school_id, uids)

                # Extract 's'-layer associated with this school
                s_subset = sdf.loc[ (sdf['p1'].isin(uids)) | (sdf['p2'].isin(uids))]
                this_school_layer = cvb.Layer().from_df(s_subset)
                sch = School(school_id, school_type, uids, this_school_layer, is_hybrid, sim)
                print(sch)
                self.schools.append(sch)


                #print(sim.people.contacts['s'].find_contacts(uids))
                #for cuid in sim.people.contacts['s'].find_contacts(uids):
                    #sim.people.contacts['s'].pop_inds
                exit()

        people = [item for sublist in sim.people.schools.values() for item in sublist]
        print(len(people))

        print(sim.people) # school_type_by_person:, school_types, schools, stuent_flag, staff_flag, teacher_flag

        self.initialized = True
        return


    def apply(self, sim):

        t = sim.t
        self.rescale = sim.rescale_vec[t] # Current rescaling factor for counts

        return

