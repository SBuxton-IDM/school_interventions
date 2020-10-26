'''
This is the main script used for commissioning the different testing scenarios
(defined in testing_scenarios.py) for the paper results. Run this script first
(preferably on an HPC!), then run the different plotting scripts.
'''

import os
import covasim as cv
import create_sim as cs
import sciris as sc
import synthpops as sp
import covasim_schools as cvsch
import testing_scenarios as t_s # From the local folder

cv.check_save_version('1.7.6', folder='gitinfo', comments={'SynthPops':sc.gitinfo(sp.__file__)})

par_inds = (0,30)
pop_size = 2.25e5 # 1e5 2.25e4 2.25e5
batch_size = 24

folder = 'v20201019'
stem = f'batch_final_1wAntigen_{par_inds[0]}-{par_inds[1]}'
calibfile = os.path.join(folder, 'pars_cases_begin=75_cases_end=75_re=1.0_prevalence=0.002_yield=0.024_tests=225_pop_size=225000.json')

scenarios = t_s.generate_scenarios()
#scenarios = {k:v for k,v in scenarios.items() if k in ['with_countermeasures']}

testing = t_s.generate_testing()
testing = {k:v for k,v in testing.items() if k in ['Antigen every 1w, PCR f/u']}

# Hand tuned and replicates instead of optuna pars - testing will perturb the rand seed before schools open anyway
pars_v1 = { # 100k pop
    'pop_infected': 160,
    'clip_edges': 0.65,
    'change_beta': 0.525,
}

pars_v2 = { # Updated v2 pars achieve lower prevalence (0.2% as opposed to closer to 0.5% with v1) (100kpop)
    'pop_infected': 90,
    'clip_edges': 0.65,
    'change_beta': 0.62,
}

# Now ignoring pars_v1 an pars_v2, using calibrated values instead:
par_list = sc.loadjson(calibfile)[par_inds[0]:par_inds[1]]

sims = []
msims = []
tot = len(scenarios) * len(testing) * len(par_list)
proc = 0
for skey, scen in scenarios.items():
    for tidx, (tkey, test) in enumerate(testing.items()):
        for eidx, entry in enumerate(par_list):
            par = sc.dcp(entry['pars'])
            par['rand_seed'] = int(entry['index'])

            sim = cs.create_sim(par, pop_size=pop_size, folder=folder)

            sim.label = f'{skey} + {tkey}'
            sim.key1 = skey
            sim.key2 = tkey
            sim.eidx = eidx
            sim.scen = scen
            sim.tscen = test
            sim.dynamic_par = par

            # Modify scen with test
            this_scen = sc.dcp(scen)
            for stype, spec in this_scen.items():
                if spec is not None:
                    spec['testing'] = sc.dcp(test) # dcp probably not needed because deep copied in new_schools

            sm = cvsch.schools_manager(scen)
            sim['interventions'] += [sm]
            sims.append(sim)
            proc += 1

            if len(sims) == batch_size or proc == tot or (tidx == len(testing)-1 and eidx == len(par_list)-1):
                print(f'Running sims {proc-len(sims)}-{proc-1} of {tot}')
                msim = cv.MultiSim(sims)
                msims.append(msim)
                msim.run(reseed=False, par_args={'ncpus': 32}, noise=0.0, keep_people=False)
                sims = []

    print(f'*** Saving after completing {skey}')
    sims_this_scenario = [s for msim in msims for s in msim.sims if s.key1 == skey]
    msim = cv.MultiSim(sims_this_scenario)
    cv.save(os.path.join(folder, 'msims', f'{stem}_{skey}.msim'), msim)

msim = cv.MultiSim.merge(msims)
cv.save(os.path.join(folder, 'msims', f'{stem}.msim'), msim)
