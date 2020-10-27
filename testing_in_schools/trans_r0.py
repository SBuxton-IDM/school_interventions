'''
Not a formal test -- test that symptom screening is doing what it is supposed to.
'''

import os
import sciris as sc
import covasim as cv
import covasim_schools as cvsch
import create_sim as cs
from testing_scenarios import generate_scenarios

#%% Configuration
sc.heading('Configuring...')
T = sc.tic()

debug       = True # Verobisty and other settings
do_run      = True # Whether to rerun instead of load saved run
keep_people = False # Whether to keep people when running
parallelize = True # If running, whether to parallelize
do_save     = True # If rerunning, whether to save sims
do_plot     = True # Whether to plot results

n_seeds = 1 # Number of seeds to run each simulation with
rand_seed = 2346 # Overwrite the default random seed
bypass_popfile = 'explore_symptoms_medium.ppl'
pop_size = int(100e3)

entry =   {
    "index": 376.0,
    "mismatch": 0.03221581045452142,
    "pars": {
      "pop_infected": 242.11186358945181,
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
    sim.label = {f'Sim {seed}'}
    sim['interventions'] += [cvsch.schools_manager(scen)]
    sims.append(sim)
msim = cv.MultiSim(sims)
msim.run(keep_people=True)



#%% Plotting
sc.heading('Plotting...')



print('Done.')
sc.toc(T)