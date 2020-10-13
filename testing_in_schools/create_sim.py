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
            change_beta=[0.5, 0, 1],
        ))

    output = {}
    for key,arr in pardata.items():
        if which == 'best':
            output[key] = arr[0]
        elif which == 'bounds':
            output[key] = arr[1:3]

    return output

def create_sim(params, pop_size=2.25e5):

    pop_scale = 1# 2.25e6 / pop_size

    p = sc.objdict(sc.mergedicts(define_pars(which='best', kind='both'), params))
    if 'rand_seed' not in p:
        seed = 1
        print(f'Note, could not find random seed in {params}! Setting to {seed}')
        p['rand_seed'] = seed  # Ensure this exists

    popfile_stem = f'inputs/kc_synthpops_clustered_{int(pop_size)}_withstaff_seed'

    ''' #V1:
    tp = sc.objdict(
        symp_prob=0.03,
        asymp_prob=0.0022,
        symp_quar_prob=0.01,
        asymp_quar_prob=0.001,
        test_delay=5.0,
    )
    '''

    # V2
    tp = sc.objdict(
        symp_prob=0.10,
        asymp_prob=0.0022,
        symp_quar_prob=0.10,
        asymp_quar_prob=0.001,
        test_delay=2.0,
    )

    ct = sc.objdict(
        trace_probs = {'w': 0.1, 'c': 0, 'h': 0.9, 's': 0.8}, # N.B. 's' will be ignored if using the Schools class
        trace_time  = {'w': 2,   'c': 0, 'h': 1,   's': 2},
    )

    pars = {
        'pop_size': pop_size,
        'pop_scale': pop_scale,
        'pop_type': 'synthpops',
        'pop_infected': p.pop_infected,
        'rescale': True,
        'rescale_factor': 1.1,
        'verbose': 0, #0.1,
        'start_day': '2020-09-01',
        'end_day': '2021-01-31',
        'rand_seed': p.rand_seed,
    }

    n_popfiles = 5
    popfile = popfile_stem + str(params['rand_seed'] % n_popfiles) + '.ppl'
    sim = cv.Sim(pars, popfile=popfile, load_pop=True)

    interventions = [
        cv.test_prob(start_day='2020-09-01', **tp),
        cv.contact_tracing(start_day='2020-09-01', **ct),
        #cv.change_beta(days='2020-08-01', changes=0.75, layers=['w', 'c'], label='NPI_work_community'),
        cv.change_beta(days='2020-09-01', changes=p.change_beta, layers=['w', 'c'], label='NPI_work_community'),
        cv.clip_edges(days='2020-09-01', changes=p.clip_edges, layers=['w', 'c'], label='close_work_community'),

        # N.B. Schools are not closed in create_sim, must be handled outside this function
    ]
    sim['interventions'] = interventions
    for interv in sim['interventions']:
        interv.do_plot = False

    return sim

def run_sim(params):
    sim = create_sim()
    sim.run()
    return sim


