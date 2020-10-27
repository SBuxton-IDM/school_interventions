'''
Not a formal test -- test that symptom screening is doing what it is supposed to.
'''

import os
import numpy as np
import sciris as sc
import covasim as cv
import covasim_schools as cvsch
import create_sim as cs
from testing_scenarios import generate_scenarios


#%% Define the school seeding 'intervention'
class seed_schools(cv.Intervention):
    ''' Seed one infection in each school '''

    def __init__(self, n_infections=2, s_types=None, delay=0, verbose=1, **kwargs):
        super().__init__(**kwargs) # Initialize the Intervention object
        self._store_args() # Store the input arguments so that intervention can be recreated
        self.n_infections = n_infections
        self.s_types = s_types if s_types else ['es', 'ms', 'hs']
        self.delay = delay
        self.verbose = verbose
        self.school_ids = self._res([])
        self.seed_inds = self._res([])
        self.r0s = self._res(0.0)
        self.numerators = self._res(0)
        self.denominators = self._res(0)
        return


    def _res(self, emptyobj):
        ''' Return a standard results dict -- like a defaultdict kind of '''
        return sc.objdict({k:sc.dcp(emptyobj) for k in self.s_types})


    def initialize(self, sim):
        ''' Find the schools and seed infections '''
        for st in self.s_types:
            self.school_ids[st] = sim.people.school_types[st]
            for sid in self.school_ids[st]:
                s_uids = np.array(sim.people.schools[sid])
                choices = cv.choose(len(s_uids), self.n_infections)
                self.seed_inds[st] += s_uids[choices].tolist()
        return


    def _lseed(self, st):
        return f'seed_infection_{st}'


    def apply(self, sim):
        if sim.t == self.delay: # Only infect on the first day (or after a delay)
            for st,inds in self.seed_inds.items():
                if len(inds):
                    sim.people.infect(inds=np.array(inds), layer=self._lseed(st))
                if self.verbose:
                    print(f'Infected {len(inds)} people in school type {st} on day {sim.t}')

        if sim.t == sim.npts-1:
            self.tt = sim.make_transtree()
            self.tt.make_detailed(sim.people)
            for st in self.s_types:
                denominator = len(self.seed_inds[st])
                numerator = 0
                for ind in self.seed_inds[st]:
                    numerator +=  len(self.tt.targets[ind])
                self.numerators[st] = numerator
                self.denominators[st] = denominator
                if denominator:
                    self.r0s[st] = numerator/denominator
            sim.school_r0s = self.r0s

        return




#%% Configuration
sc.heading('Configuring...')
T = sc.tic()

do_plot     = True # Whether to plot results
n_seeds = 6 # Number of seeds to run each simulation with
rand_seed = 1 # Overwrite the default random seed
bypass_popfile = 'trans_r0_medium.ppl'
pop_size = int(100e3)

entry =   {
    "index": 376.0,
    "mismatch": 0.03221581045452142,
    "pars": {
      "pop_infected": 0,
      "change_beta": 0.5313884845187986,
      "symp_prob": 0.08250498122080606
    }
  }
params = sc.dcp(entry['pars'])
if rand_seed is None:
    params['rand_seed'] = int(entry['index'])
else:
    params['rand_seed'] = rand_seed

# Ensure the population file exists
if not os.path.exists(bypass_popfile):
    print(f'Population file {bypass_popfile} not found, recreating...')
    cvsch.make_population(pop_size=pop_size, rand_seed=params['rand_seed'], max_pop_seeds=5, popfile=bypass_popfile, do_save=True)

scen = generate_scenarios()['as_normal']

# Create the sim
people = sc.loadobj(bypass_popfile)
base_sim = cs.create_sim(params, pop_size=pop_size, load_pop=False, people=people, verbose=0.1)


#%% Run the sims
sims = []
for seed in range(n_seeds):
    sim = sc.dcp(base_sim)
    sim.set_seed(seed=sim['rand_seed'] + seed)
    sim.label = f'Sim {seed}'
    sim['interventions'] += [cvsch.schools_manager(scen), seed_schools()]
    sims.append(sim)
msim = cv.MultiSim(sims)
msim.run(keep_people=True)


#%% Results
res = {k:np.zeros(n_seeds) for k in ['es', 'ms', 'hs']}
for s,sim in enumerate(msim.sims):
    for k in res.keys():
        res[k][s] = sim.school_r0s[k]

for k in res.keys():
    mean = res[k].mean()
    std  = res[k].std()
    print(f'R0 for "{k}": {mean:0.2f} ± {std:0.2f}')

print('Done.')
sc.toc(T)