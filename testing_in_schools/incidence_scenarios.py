import os
import covasim as cv
import create_sim as cs
import sciris as sc
from school_intervention import new_schools
import synthpops as sp
cv.check_save_version('1.7.2', comments={'SynthPops':sc.gitinfo(sp.__file__)})


res = [1.0]
incs = [20, 100, 150] #[20, 50, 110]
n_seeds = 5
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

    scns = sc.odict()

    remote = {
        'start_day': '2020-09-01',
        'schedule': 'remote',
        'screen_prob': 0,
        'test_prob': 0,
        'trace_prob': 0,
        'ili_prob': 0,
        'beta_s': 0
    }

    base = {
        'start_day': '2020-09-01',
        'schedule': 'full',
        'screen_prob': 0,
        'test_prob': 0.5,
        'trace_prob': 0.5,
        'ili_prob': 0.002, # Daily ili probability equates to about 10% incidence over the first 3 months of school
        'beta_s': base_beta_s # No NPI
    }
    scns['as_normal'] = scenario(es=base, ms=base, hs=base)

    # Add screening and NPI
    screening = sc.dcp(base)
    screening['screen_prob'] = 0.9
    screening['beta_s'] = 0.75 * base_beta_s # 25% reduction due to NPI
    scns['with_screening'] = scenario(es=screening, ms=screening, hs=screening)
    scns['ES_MS_inperson_HS_remote'] = scenario(es=screening, ms=screening, hs=remote)
    scns['ES_inperson_MS_HS_remote'] = scenario(es=screening, ms=remote, hs=remote)

    # Add hybrid scheduling
    hybrid = sc.dcp(screening)
    hybrid['schedule'] = 'hybrid'
    scns['all_hybrid'] = scenario(es=hybrid, ms=hybrid, hs=hybrid)
    scns['ES_hybrid'] = scenario(es=hybrid, ms=remote, hs=remote)

    # All remote
    scns['all_remote'] = scenario(es=remote, ms=remote, hs=remote)

    return scns

def generate_pars(res, incs):
    pars = []
    for re in res:
        for inc in incs:
            rel_trans = False
            if rel_trans:
                jsonfile = f'optimization_school_reopening_re_{re}_cases_{inc}_{int(pop_size)}_reltrans.json'
            else:
                jsonfile = f'optimization_school_reopening_re_{re}_cases_{inc}_{int(pop_size)}.json'
            json = sc.loadjson(jsonfile)

            for entry in json[:n_seeds]:
                p = entry['pars']
                p['rand_seed'] = int(entry['index'])
                # These are not model parameters, but useful to have later
                p['re'] = re
                p['inc'] = inc
                pars.append(p)

    return pars


if __name__ == '__main__':
    scenarios = generate_scenarios()
    dynamic_pars = generate_pars(res, incs)

    # Temp - make experiment smaller for testing
    scenarios = {s:v for s,v in scenarios.items() if s in ['as_normal', 'all_hybrid', 'all_remote']}
    #dynamic_pars = dynamic_pars[:2]

    sims = []
    msims = []
    tot = len(scenarios) * len(dynamic_pars)
    proc = 0
    step = 16
    for skey, scen in scenarios.items():
        for idx, dp in enumerate(dynamic_pars):
            sim = cs.create_sim(dp, pop_size=pop_size)

            sim.label = skey
            sim.scen = scen
            sim.dynamic_par = dp

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
