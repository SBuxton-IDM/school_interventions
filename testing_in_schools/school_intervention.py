# This is the front end to the Schools class intervention.  Not much here, it's a sub-class of covasim's Intervention class.  The one piece of computation done here is to split the original school 's' network into individual schools.  (Each school was already a separate component, but the code figures out which component goes with which school and extracts the subgraph.)

from covasim.interventions import Intervention
import covasim.base as cvb
from school import School

class new_schools(Intervention):
    ''' Specifies reopening strategy.  '''

    def __init__(self, scenario, **kwargs):
        super().__init__(**kwargs) # Initialize the Intervention object
        self._store_args() # Store the input arguments so that intervention can be recreated

        # Store arguments
        self.scenario = scenario
        self.schools = []

    def initialize(self, sim):
        # Create schools, stealing 's' edges into the School class instances upon *initialize*
        self.school_types = sim.people.school_types # Dict with keys of school types (e.g. 'es') and values of list of school ids (e.g. [1,5])

        sdf = sim.people.contacts['s'].to_df()
        sim.school_stats = {}

        if sim['beta_layer']['s'] == 0:
            print('Warning: new_schools intervention is being configured with school beta_layer set to zero, no transmission will occur.')
        for school_type, scids in self.school_types.items():
            for school_id in scids:
                uids = sim.people.schools[school_id] # Dict with keys of school_id and values of uids in that school

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
                    sim['beta_layer'][sch.sid] = self.scenario[school_type]['beta_s']
                    sim['iso_factor'][sch.sid] = sim['iso_factor']['s']
                    sim['quar_factor'][sch.sid] = sim['quar_factor']['s']

        # Delete remaining entries in sim.people.contacts['s'], these were associated with schools that will not open, e.g. pk and uv
        sim.people.contacts['s'] = cvb.Layer()

        self.initialized = True

    def apply(self, sim):
        for school in self.schools:
            layer = school.update()
            sim.people.contacts[school.sid] = layer

        if sim.t == sim.npts-1:
            # Only needed on final time step:
            sim.school_stats[school.sid].update( school.get_stats() )
            self.schools = [] # Huge space savings if user saves this simulation due to python junk collection

