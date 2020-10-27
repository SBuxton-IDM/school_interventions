'''
Not a formal test -- test that symptom screening is doing what it is supposed to.
'''

import os
import numpy as np
import pylab as pl
import sciris as sc
import seaborn as sns
import covasim as cv
import covasim_schools as cvsch
from testing_in_schools import create_sim as cs
from testing_in_schools.testing_scenarios import generate_scenarios, generate_testing

#%% Configuration
sc.heading('Configuring...')
T = sc.tic()

debug       = True # Verobisty and other settings
bypass      = True # Whether to use a small population size
do_run      = True # Whether to rerun instead of load saved run
keep_people = False # Whether to keep people when running
parallelize = True # If running, whether to parallelize
do_save     = True # If rerunning, whether to save sims
do_plot     = True # Whether to plot results

n_seeds = 4 # Number of seeds to run each simulation with
rand_seed = 2346 # Overwrite the default random seed
folder = '../testing_in_schools/v20201019'
bypass_popfile = 'explore_symptoms_small.ppl'
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
divider = ' -- '
def joinkeys(skey, tkey):
    ''' Turn scenario and testing keys into a single key '''
    return divider.join([skey, tkey])

def splitkey(key):
    ''' Oppostite of joinkeys() '''
    return key.split(divider)

origscen = generate_scenarios()['as_normal']
testings = {'none':
                None,
            'antigen': {
                'start_date': '2020-10-26',
                'repeat': 14,
                'groups': ['students', 'teachers', 'staff'], # No students
                'coverage': 1,
                'is_antigen': True,
                'symp7d_sensitivity': 0.971, # https://www.fda.gov/media/141570/download
                'other_sensitivity': 0.90, # Modeling assumption
                'specificity': 0.985, # https://www.fda.gov/media/141570/download
                'PCR_followup_perc': 1.0,
                'PCR_followup_delay': 3.0,
            }}
t_keys = list(testings.keys())
n_testings = len(testings)
all_scens = sc.odict()
for tkey,testing in testings.items():
    scen = sc.dcp(origscen)
    for stype, spec in scen.items():
        if spec is not None:
            spec['testing'] = testing
    scen['es']['verbose'] = scen['ms']['verbose'] = scen['hs']['verbose'] = debug
    all_scens[tkey] = scen

# Create the sim
if bypass: # BYPASS option -- create small population on the fly
    people = sc.loadobj(bypass_popfile)
    base_sim = cs.create_sim(params, pop_size=pop_size, load_pop=False, people=people, verbose=0.1)
else: # Otherwise, load full population from disk
    base_sim = cs.create_sim(params, pop_size=pop_size, folder=folder, verbose=0.1)


#%% Run the sims
msims = []
for key,scen in all_scens.items():
    sims = []
    for seed in range(n_seeds):
        sim = sc.dcp(base_sim)
        sim.set_seed(seed=sim['rand_seed'] + seed)
        sim.label = f'Testing = {key}, seed = {seed}'
        sim['interventions'] += [cvsch.schools_manager(scen)]
        sims.append(sim)
    msim = cv.MultiSim(sims)
    msim.run()
    msim.reduce()
    msims.append(msim)

msim_base = cv.MultiSim.merge(msims, base=True)
msim_all = cv.MultiSim.merge(msims, base=False)


#%% Plotting
if do_plot:
    msim_base.plot(to_plot='overview')
    msim_all.plot(to_plot='overview', color_by_sim=True, max_sims=2*n_seeds)


print('Done.')
sc.toc(T)