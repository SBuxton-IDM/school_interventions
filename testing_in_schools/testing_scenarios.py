import os
import covasim as cv
import create_sim as cs
import sciris as sc
from school_intervention import new_schools

n_reps = 2
pop_size = 1e5 # 2.25e4 2.25e5

debug = False # Warning: this sets keep_people=True so limit to a few scenarios

def scenario(es, ms, hs):
    return {
        'pk': None,
        'es': es,
        'ms': ms,
        'hs': hs,
        'uv': None,
    }


def generate_scenarios():
    ''' Generate scenarios (dictionaries of parameters) for the school intervention '''

    # Create a single sim to get parameters (make_pars is close, but not quite)
    sim = cs.create_sim({'rand_seed':0}, pop_size=pop_size)
    base_beta_s = sim.pars['beta_layer']['s']

    # Testing interventions to add
    PCR_1w_prior = {
        'start_date': '2020-08-29',
        'repeat': None,
        'school_types': ['es', 'ms'],
        'groups': ['students', 'teachers', 'staff'],
        'coverage': 0.9,
        'trace_prob': 0,
        'sensitivity': 1,
        'specificity': 1,
    }

    PCR_every_2w = {
        'start_date': '2020-09-01',
        'repeat': 14,
        'school_types': ['es', 'ms'],
        'groups': ['students', 'teachers', 'staff'],
        'coverage': 0.9,
        'trace_prob': 0.8,
        'sensitivity': 1,
        'specificity': 1,
    }

    PCR_1w_prior_and_every_2w = [PCR_1w_prior, PCR_every_2w]

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
        'beta_s': base_beta_s # No NPI
        'testing': None,
    }
    scns['as_normal'] = scenario(es=normal, ms=normal, hs=normal)

    # Add screening and NPI
    screening = sc.dcp(normal)
    screening['screen_prob'] = 0.9
    screening['beta_s'] = 0.75 * base_beta_s # 25% reduction due to NPI
    scns['with_screening_1wprior'] = scenario(es=screening, ms=screening, hs=screening)
    scns['with_screening_1wprior']['testing'] = PCR_1w_prior # Add testing

    # Add hybrid scheduling
    hybrid = sc.dcp(screening)
    hybrid['is_hybrid'] = True
    scns['all_hybrid_1wprior_every2w'] = scenario(es=hybrid, ms=hybrid, hs=hybrid)
    scns['all_hybrid_1wprior_every2w']['testing'] = PCR_1w_prior_and_every_2w # Add testing

    # All remote
    scns['all_remote'] = scenario(es=remote, ms=remote, hs=remote)

    return scns

if __name__ == '__main__':
    scenarios = generate_scenarios()

    # Hand tuned and replicates instead of optuna pars
    pars = {
        'pop_infected': 160,
        'clip_edges': 0.65,
        'change_beta': 0.525,
    }

    sims = []
    msims = []
    tot = len(scenarios) * n_reps
    proc = 0
    step = 16
    for skey, scen in scenarios.items():
        for rep in n_reps:
            par = sc.dcp(pars)
            par['rand_seed'] = rep
            sim = cs.create_sim(par, pop_size=pop_size)

            sim.label = skey
            sim.scen = scen
            sim.dynamic_par = par

            ns = new_schools(scen) # Not sure if need new mem for each
            sim['interventions'] += [ns]
            sims.append(sim)
            proc += 1

            if len(sims) == step or proc == tot:
                print(f'Running sims {proc-len(sims)}:{proc} of {tot}')
                msim = cv.MultiSim(sims)
                msims.append(msim)
                msim.run(reseed=False, par_args={'ncpus': 16}, noise=0.0, keep_people=debug)
                sims = []

    msim = cv.MultiSim.merge(msims)
    cv.save(os.path.jsoin('msims', f'msim_{int(pop_size)}.obj'), msim)

    if debug:
        for sim in msim.sims:
            sim.plot(to_plot='overview')
            t = sim.make_transtree()
