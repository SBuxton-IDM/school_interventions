import covasim as cv
import sciris as sc
import matplotlib.pyplot as plt
import os
import numpy as np
import create_sim as cs
from school_intervention import new_schools

do_run = True
msim_fn = os.path.join('msims', 'remote_reps.msim')
msim_nopeople_fn = os.path.join('msims', 'remote_no_people_reps.msim')
n_runs = 16
re_to_fit = 1.0
cases_to_fit = 75
pop_size = 1e5


def scenario(es, ms, hs):
    return {
        'pk': None,
        'es': sc.dcp(es),
        'ms': sc.dcp(ms),
        'hs': sc.dcp(hs),
        'uv': None,
    }


if __name__ == '__main__':

    params_all = {}
    # 75
    params_all[75] = {
        'pop_infected': 100,
        'clip_edges': 0.65,
        'change_beta': 0.525,
    }

    # 75 - v1
    params_all['75_good'] = {
        'pop_infected': 160,
        'clip_edges': 0.65,
        'change_beta': 0.525,
    }
    # 150
    params_all[150] = {
        'pop_infected': 300,
        'clip_edges': 0.65,
        'change_beta': 0.55,
    }
    params = params_all[cases_to_fit]

    sim = cs.create_sim({'rand_seed':0}, pop_size=pop_size)
    base_beta_s = sim.pars['beta_layer']['s']

    full_with_countermeasures = {
        'start_day': '2020-11-02',
        'schedule': 'Full',
        'screen_prob': 0.9,
        'test_prob': 0.5, # Amongst those who screen positive
        'trace_prob': 0.75, # Fraction of newly diagnosed index cases who are traced
        'quar_prob': 0.75, # Of those reached by contact tracing, this fraction will quarantine
        'ili_prob': 0.002, # Daily ili probability equates to about 10% incidence over the first 3 months of school
        'beta_s': 0.75 * base_beta_s, # 25% reduction due to NPI
        'testing': None,
    }

    remote = { # <-- Used for calibration
        'start_day': '2020-11-02',
        'schedule': 'Remote',
        'screen_prob': 0,
        'test_prob': 0,
        'trace_prob': 0,
        'quar_prob': 0,
        'ili_prob': 0,
        'beta_s': 0, # NOTE: No transmission in school layers
        'testing': None,
    }

    if do_run:
        s = scenario(es=remote, ms=remote, hs=remote)

        sims = []
        for seed in range(n_runs):
            params['rand_seed'] = seed

            sim = cs.create_sim(params, pop_size=pop_size)
            sim.label = f'{seed}'
            ns = new_schools(s)
            sim['interventions'] += [ns]

            sims.append(sim)

        ###### TEMP ms = cv.MultiSim(sims, noise=0, keep_people=True)
        ms = cv.MultiSim(sims, noise=0, keep_people=False)
        ms.run()
        ###### #ms.save(msim_fn, keep_people=True)
        ms.save(msim_nopeople_fn, keep_people=False)
    else:
        print(f'Loading from file {msim_nopeople_fn}')
        ms = cv.MultiSim.load(msim_nopeople_fn)

    '''
    for s in ms.sims:
        first_school_day = s.day('2020-11-02')
        last_school_day = s.day('2021-01-31')
        re = np.mean(s.results['r_eff'][first_school_day:last_school_day])
        cases_past14 = np.sum(s.results['new_diagnoses'][(first_school_day-14):first_school_day]) * 100e3 / (s.pars['pop_size'] * s.pars['pop_scale'])
        cases_during = np.mean(s.results['new_diagnoses'][first_school_day:last_school_day]) * 14 * 100e3 / (s.pars['pop_size'] * s.pars['pop_scale'])

        re_mismatch = (re_to_fit - re)**2 / re_to_fit**2
        cases_past14_mismatch = (cases_to_fit - cases_past14)**2 / cases_to_fit**2
        cases_during_mismatch = (cases_to_fit - cases_during)**2 / cases_to_fit**2
        mismatch = re_mismatch + cases_past14_mismatch + cases_during_mismatch

        print(re, cases_past14, cases_during, mismatch)
    '''
    print('Reduce')

    ms.reduce()
    #ms.save(msim_nopeople_fn, keep_people=False)
    ms.plot(to_plot='overview')

    #plt.savefig('sim.png')

    #plt.figure()
    to_plot = sc.odict({
            'New Infections per 100k': [
                'new_infections',
            ],
            'New Diagnoses per 100k': [
                'new_diagnoses',
            ],
            'Test Yield': [
                'test_yield',
            ],
            'Effective Reproduction Number': [
                'r_eff',
            ],
            'Infectious per 100k': [
                'n_infectious',
            ],
            'Prevalence': [
                'prevalence',
            ],
        })
    ms.plot(to_plot=to_plot, n_cols=2)
