'''
Not a formal test, but a script for running all scenarios. Based on test_schools.py.
'''

import os
import pylab as pl
import sciris as sc
import seaborn as sns
import covasim_schools as cvsch
from testing_in_schools import create_sim as cs
from testing_in_schools.testing_scenarios import generate_scenarios, generate_testing

#%% Configuration
sc.heading('Configuring...')
T = sc.tic()

debug = True # Verobisty and other settings
bypass = True # Whether to use a small population size
do_run = True # Whether to rerun instead of load saved run
keep_people = False # Whether to keep people when running
parallelize = True # If running, whether to parallelize
do_save = True  # If rerunning, whehter to save sims
do_plot = True # Whether to plot results

rand_seed = None # Overwrite the default random seed
folder = '../testing_in_schools/v20201019'
bypass_popfile = 'explore_scenarios_small.ppl'
sims_file = 'explore_scenarios.sims'
pop_size = int(20e3) if bypass else int(2.25e5)
calibfile = os.path.join(folder, 'pars_cases_begin=75_cases_end=75_re=1.0_prevalence=0.002_yield=0.024_tests=225_pop_size=225000.json')

try:
    entry = sc.loadjson(calibfile)[1]
except Exception as E:
    entry =   {
        "index": 376.0,
        "mismatch": 0.03221581045452142,
        "pars": {
          "pop_infected": 242.11186358945181,
          "change_beta": 0.5313884845187986,
          "symp_prob": 0.08250498122080606
        }
      }
    print(f'Warning: could not load calibration file "{calibfile}" due to "{str(E)}", using hard-coded parameters')
params = sc.dcp(entry['pars'])
if rand_seed is None:
    params['rand_seed'] = int(entry['index'])
else:
    params['rand_seed'] = rand_seed

# Ensure the population file exists
if bypass and not os.path.exists(bypass_popfile):
    print(f'Population file {bypass_popfile} not found, recreating...')
    cvsch.make_population(pop_size=pop_size, rand_seed=params['rand_seed'], max_pop_seeds=5, popfile=bypass_popfile, do_save=True)

# Create the scenarios
scens = generate_scenarios()
testings = generate_testing()
n_scens = len(scens)
n_testings = len(testings)
all_scens = sc.odict()
all_keys = []
for skey,origscen in scens.items():
    for tkey,testing in testings.items():
        scen = sc.dcp(origscen)
        for stype, spec in scen.items():
            if spec is not None:
                spec['testing'] = testing
        scen['es']['verbose'] = scen['ms']['verbose'] = scen['hs']['verbose'] = debug
        all_scens[f'{skey} -- {tkey}'] = scen
        all_keys.append([skey, tkey])

# Create the sim
if bypass: # BYPASS option -- create small population on the fly
    people = sc.loadobj(bypass_popfile)
    base_sim = cs.create_sim(params, pop_size=pop_size, load_pop=False, people=people)
else: # Otherwise, load full population from disk
    base_sim = cs.create_sim(params, pop_size=pop_size, folder=folder, verbose=0.1)


#%% Run the sims
def run_sim(scen):
    ''' Run a single sim '''
    sim = sc.dcp(base_sim)
    sm = cvsch.schools_manager(scen)
    sim['interventions'] += [sm]
    sim.run(keep_people=keep_people)
    return sim

if do_run:
    if parallelize:
        sc.heading('Running in parallel...')
        raw_sims = sc.parallelize(run_sim, all_scens.values())
        sims = sc.odict({k:scen for k,scen in zip(all_scens.keys(), raw_sims)})
    else:
        sc.heading('Running in serial...')
        sims = sc.odict()
        for k,scen in all_scens:
            sims[k] = run_sim(scen)
    if do_save:
        sc.saveobj(sims_file, sims)

else:
    sc.heading('Loading from disk...')
    sims = sc.loadobj(sims_file)


#%% Analysis
sc.heading('Analyzing...')
res = sc.objdict()




#%% Plotting
sc.heading('Plotting...')

fig = pl.figure()

print('Done.')
sc.toc(T)