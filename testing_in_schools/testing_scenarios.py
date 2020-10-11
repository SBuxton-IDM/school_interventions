import os
import covasim as cv
import create_sim as cs
import sciris as sc
from school_intervention import new_schools

n_reps = 5
pop_size = 1e5 # 2.25e4 2.25e5

def scenario(es, ms, hs):
    return {
        'pk': None,
        'es': sc.dcp(es),
        'ms': sc.dcp(ms),
        'hs': sc.dcp(hs),
        'uv': None,
    }


def generate_scenarios():
    ''' Generate scenarios (dictionaries of parameters) for the school intervention '''

    # Create a single sim to get parameters (make_pars is close, but not quite)
    sim = cs.create_sim({'rand_seed':0}, pop_size=pop_size)
    base_beta_s = sim.pars['beta_layer']['s']

    scns = sc.odict()

    remote = {
        'start_day': '2020-09-01',
        'is_hybrid': False,
        'screen_prob': 0,
        'test_prob': 0,
        'trace_prob': 0,
        'ili_prob': 0,
        'beta_s': 0,
        'testing': None,
    }

    normal = {
        'start_day': '2020-09-01',
        'is_hybrid': False,
        'screen_prob': 0,
        'test_prob': 0.5,
        'trace_prob': 0.5,
        'ili_prob': 0.002, # Daily ili probability equates to about 10% incidence over the first 3 months of school
        'beta_s': base_beta_s, # No NPI
        'testing': None,
    }
    scns['as_normal'] = scenario(es=normal, ms=normal, hs=normal)

    # Add screening and NPI
    screening = sc.dcp(normal)
    screening['screen_prob'] = 0.9
    screening['beta_s'] = 0.75 * base_beta_s # 25% reduction due to NPI
    scns['with_screening'] = scenario(es=screening, ms=screening, hs=screening)

    # Add hybrid scheduling
    hybrid = sc.dcp(screening)
    hybrid['is_hybrid'] = True
    scns['all_hybrid'] = scenario(es=hybrid, ms=hybrid, hs=hybrid)

    # All remote
    scns['all_remote'] = scenario(es=remote, ms=remote, hs=remote)

    return scns

def generate_testing():
    # Testing interventions to add
    PCR_1w_prior = [{
        'start_date': '2020-08-29',
        'repeat': None,
        'groups': ['students', 'teachers', 'staff'],
        'coverage': 1,
        'sensitivity': 1,
        'delay': 1
        #'specificity': 1,
    }]

    PCR_every_2w = [{
        'start_date': '2020-09-01',
        'repeat': 14,
        'groups': ['students', 'teachers', 'staff'],
        'coverage': 1,
        'sensitivity': 1,
        'delay': 1
        #'specificity': 1,
    }]

    PCR_daily_starting_1wprior = [{
        'start_date': '2020-08-29',
        'repeat': 1,
        'groups': ['students', 'teachers', 'staff'],
        'coverage': 1,
        'sensitivity': 1,
        'delay': 0
        #'specificity': 1,
    }]

    PCR_1w_prior_and_every_2w = PCR_1w_prior + PCR_every_2w

    return {
        'None': None,
        'PCR 1w prior': PCR_1w_prior,
        'PCR every 2w': PCR_every_2w,
        'PCR 1w prior and every 2w': PCR_1w_prior_and_every_2w,
        'PCR daily starting 1w prior': PCR_daily_starting_1wprior
    }

if __name__ == '__main__':
    scenarios = generate_scenarios()
    #scenarios = {k:v for k,v in scenarios.items() if k in ['as_normal']}

    testing = generate_testing()

    # Hand tuned and replicates instead of optuna pars
    pars = {
        'pop_infected': 160,
        'clip_edges': 0.65,
        'change_beta': 0.525,
    }

    sims = []
    msims = []
    tot = len(scenarios) * len(testing) * n_reps
    proc = 0
    step = 16
    for skey, scen in scenarios.items():
        for tkey, test in testing.items():
            for rep in range(n_reps):
                par = sc.dcp(pars)
                par['rand_seed'] = rep
                sim = cs.create_sim(par, pop_size=pop_size)

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
                        spec['testing'] = sc.dcp(test)

                ns = new_schools(this_scen)
                sim['interventions'] += [ns]
                sims.append(sim)
                proc += 1

                if len(sims) == step or proc == tot:
                    print(f'Running sims {proc-len(sims)}:{proc} of {tot}')
                    msim = cv.MultiSim(sims)
                    msims.append(msim)
                    msim.run(reseed=False, par_args={'ncpus': 16}, noise=0.0, keep_people=False)
                    sims = []

    msim = cv.MultiSim.merge(msims)
    cv.save(os.path.join('msims', f'testing_{int(pop_size)}.msim'), msim)
