'''Fitting for theoretical reopening'''

import covasim as cv
import sciris as sc
import pandas as pd

def define_pars(which='best', kind='default', ):
    ''' Define the parameter best guesses and bounds '''

    pardata = {}
    if kind in ['default', 'both']:
        pardata.update(dict(
            pop_infected = [250, 70, 700],
            clip_edges=[0.5, 0, 1],
        ))

    output = {}
    for key,arr in pardata.items():
        if which == 'best':
            output[key] = arr[0]
        elif which == 'bounds':
            output[key] = arr[1:3]

    return output

def run_sim(params):

    popfile_stem = f'inputs/kc_synthpops_clustered_withstaff_seed'


    tp = sc.objdict(
        symp_prob=0.03,
        asymp_prob=0.001,
        symp_quar_prob=0.01,
        asymp_quar_prob=0.001,
        test_delay=5.0,
    )
    ct = sc.objdict(
        trace_probs={'w': 0.1, 'c': 0, 'h': 0.8, 's': 0.8},
        trace_time=5.0,
    )

    all_sims = []
    pars = {'pop_size': 225e3,
            'pop_scale': 10,
            'pop_type': 'synthpops',
            'pop_infected': params['pop_infected'],
            'rescale': True,
            'rescale_factor': 1.1,
            'verbose': 0,
            'start_day': '2020-07-01',
            'end_day': '2020-09-02',
            'rand_seed': j,
            }
    n_popfiles = 5
    popfile = popfile_stem + str(params['rand_seed'] % n_popfiles) + '.ppl'
    sim = cv.Sim(pars, popfile=popfile, load_pop=True)
    interventions = [
        cv.test_prob(start_day='2020-07-01', **tp),
        cv.contact_tracing(start_day='2020-07-01', **ct),
        cv.clip_edges(days='2020-08-01', changes=params['clip_edges'], layers='w', label='close_work'),
        cv.clip_edges(days='2020-08-01', changes=params['clip_edges'], layers='c', label='close_community'),
        cv.change_beta(days='2020-08-01', changes=0.75, layers='c', label='NPI_community'),
        cv.change_beta(days='2020-08-01', changes=0.75, layers='w', label='NPI_work'),
        cv.close_schools(
            day_schools_closed='2020-07-01',
            start_day=None,
            label='close_schools'
        )
    ]
    sim['interventions'] = interventions
    for interv in sim['interventions']:
        interv.do_plot = False
    sim.run(reseed=False, par_args={'maxload': 0.8}, noise=0.0, keep_people=True)
    results = pd.DataFrame(sim.results)
    re = results['r_eff'][sim.day('2020-09-01')]
    cases = results['new_diagnoses'].iloc[49:63, ].sum(axis=0) * 100e3 / 2.25e6
    print(f'Reff is {round(re, 2)}')
    print(f'In last 14 days, there were {round(cases, 4)} cases per 100k')

if __name__ == '__main__':

