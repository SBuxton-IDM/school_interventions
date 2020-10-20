import os
import numpy as np
import covasim as cv
import create_sim as cs
import sciris as sc
import matplotlib.pyplot as plt
from school_intervention import new_schools
from testing_scenarios import generate_scenarios, generate_testing
import synthpops as sp
cv.check_save_version('1.7.2', comments={'SynthPops':sc.gitinfo(sp.__file__)})

do_run = False

par_inds = (0,25) # First and last parameters to run
pop_size = 2.25e5 # 1e5 2.25e4 2.25e5
batch_size = 25

folder = 'v20201015_225k'
stem = f'calib_remote_notest_{par_inds[0]}-{par_inds[1]}'
calibfile = os.path.join(folder, 'pars_cases_begin=75_cases_end=75_re=1.0_prevalence=0.002_yield=0.024_tests=225_pop_size=225000.json')

if __name__ == '__main__':
    scenarios = generate_scenarios()
    scenarios = {k:v for k,v in scenarios.items() if k in ['all_remote']}

    testing = generate_testing()
    testing = {k:v for k,v in testing.items() if k in ['None']}

    par_list = sc.loadjson(calibfile)[par_inds[0]:par_inds[1]]

    if do_run:
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
                    sim.scen = scen
                    sim.tscen = test
                    sim.dynamic_par = par

                    # Modify scen with test
                    this_scen = sc.dcp(scen)
                    for stype, spec in this_scen.items():
                        if spec is not None:
                            spec['testing'] = sc.dcp(test) # dcp probably not needed because deep copied in new_schools
                            spec['beta_s'] = 1.5 # Shouldn't matter considering schools are closed in the 'all_remote' scenario

                    ns = new_schools(this_scen)
                    sim['interventions'] += [ns]
                    sims.append(sim)
                    proc += 1

                    if len(sims) == batch_size or proc == tot:# or (tidx == len(testing)-1 and eidx == len(par_list)-1):
                        print(f'Running sims {proc-len(sims)}-{proc-1} of {tot}')
                        msim = cv.MultiSim(sims)
                        msims.append(msim)
                        msim.run(reseed=False, par_args={'ncpus': 16}, noise=0.0, keep_people=False)
                        sims = []

            print(f'*** Saving after completing {skey}')
            sims_this_scenario = [s for msim in msims for s in msim.sims if s.key1 == skey]
            msim = cv.MultiSim(sims_this_scenario)

        msim = cv.MultiSim.merge(msims)
        msim.save(os.path.join(folder, 'msims', f'{stem}.msim'), keep_people=False)
    else:
        msim = cv.MultiSim.load(os.path.join(folder, 'msims', f'{stem}.msim'))

    # Calib plotting

    sims = [s for s in msim.sims if s.key1=='all_remote' and s.key2=='None']
    ms = cv.MultiSim(sims)

    ms.reduce()
    #ms.plot(to_plot='overview')

    #plt.figure()
    to_plot = sc.odict({
            'New Infections per 225k': [
                'new_infections',
            ],
            'New Diagnoses per 225k': [
                'new_diagnoses',
            ],
            'Test Yield': [
                'test_yield',
            ],
            'Effective Reproduction Number': [
                'r_eff',
            ],
            'New Tests per 225k': [
                'new_tests',
            ],
            'Prevalence': [
                'prevalence',
            ],
        })
    #fig = plt.figure(figsize=(16,10))
    #ms.plot(to_plot=to_plot, n_cols=2, interval=30, legend_args={'show_legend':False}, do_show=False, fig=fig) # , dateformat='%B'

    f, axv = plt.subplots(3,2, figsize=(12,8))
    chs = sc.odict({
        'new_infections': { 'title': 'New Infections per 100k', 'ref':None },
        'new_diagnoses': { 'title': 'New Diagnoses over 14d per 100k', 'ref': 75 },
        'test_yield': { 'title': 'Test Yield', 'ref': 0.022 },
        'r_eff': { 'title': 'Reproduction Number', 'ref': 1.0 },
        'new_tests': { 'title': 'New Tests per 100k', 'ref': 225 },
        'prevalence': { 'title': 'Prevalence', 'ref': 0.002 },
    })

    ri=ci=0
    for ch,info in chs.items():
        if ri == 3:
            ri=0
            ci=1

        rvec = []
        for sim in msim.sims:
            r = sim.results[ch].values
            ps = 100000 / sim.pars['pop_size']*sim.pars['pop_scale']
            if ch in ['new_diagnoses']:
                r *= 14 * ps
            if ch in ['new_infections', 'new_tests']:
                r *= ps
            rvec.append(r)

        ax = axv[ri,ci]
        med = np.median(rvec, axis=0)
        sd = np.std(rvec, axis=0)
        ax.fill_between(sim.results['date'], med+2*sd, med-2*sd, color='lightgray')
        ax.plot(sim.results['date'], med+2*sd, color='gray', lw=1)
        ax.plot(sim.results['date'], med-2*sd, color='gray', lw=1)
        ax.plot(sim.results['date'], med, color='k', lw=2)
        if 'ref' in info and info['ref'] is not None:
            ax.axhline(y=info['ref'], color='r', ls='--', lw=2)
        ax.set_title(info['title'])

        ri+=1

    f.tight_layout()
    cv.savefig(os.path.join(folder, 'img', f'calibration_djk_{int(pop_size)}.png'), dpi=300)

