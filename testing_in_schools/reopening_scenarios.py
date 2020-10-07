import covasim as cv
import create_sim as cs
import sciris as sc
from school_intervention import new_schools

res = [0.9]
incs = [20, 50, 110]
n_seeds = 20

def scenario(es, ms, hs):
    return {
        'pk': None,
        'es': es,
        'ms': ms,
        'hs': hs,
        'uv': None,
    }


def generate_scenarios():

    scns = sc.odict()

    base = {
        'start_day': '2020-09-01',
        'is_hybrid': False,
        'screen_prob': 0,
        'test_prob': 0.5,
        'trace_prob': 0.5,
        'ili_prob': 0.002, # Daily ili probability
        'npi': 1
    }
    scns['As Normal'] = scenario(es=base, ms=base, hs=base)

    # Add screening and NPI
    screening = sc.dcp(base)
    screening['screen_prob'] = 0.9
    screening['npi'] = 0.75
    scns['With Screening'] = scenario(es=screening, ms=screening, hs=screening)
    scns['ES/MS in Person, HS Remote'] = scenario(es=screening, ms=screening, hs=None)
    scns['ES in Person, MS/HS Remote'] = scenario(es=screening, ms=None, hs=None)

    # Add hybrid scheduling
    hybrid = sc.dcp(screening)
    hybrid['is_hybrid'] = True
    scns['All Hybrid'] = scenario(es=hybrid, ms=hybrid, hs=hybrid)
    scns['ES Hybrid'] = scenario(es=hybrid, ms=None, hs=None)

    # All remote
    scns['All Remote'] = scenario(es=None, ms=None, hs=None)

    return scns

def generate_pars(res, incs):
    pars = []
    for re in res:
        for inc in incs:
            rel_trans = False
            if rel_trans:
                jsonfile = f'optimization_school_reopening_re_{re}_cases_{inc}_reltrans.json'
            else:
                jsonfile = f'optimization_school_reopening_re_{re}_cases_{inc}.json'
            json = sc.loadjson(jsonfile)

            for entry in json[:n_seeds]:
                p = entry['pars']
                p['rand_seed'] = int(entry['index'])
                pars.append(p)

    return pars


if __name__ == '__main__':
    scenarios = generate_scenarios()
    pars = generate_pars(res, incs)

    # Temp - make experiment smaller for testing
    scenarios = {s:v for s,v in scenarios.items() if s in ['As Normal', 'All Hybrid']} # , 'All Remote'
    pars = pars[:2]

    sims = []
    for skey, scen in scenarios.items():
        for idx, par in enumerate(pars):
            sim = cs.create_sim(par)

            sim.label = f'scen={skey}; idx={idx}; ' + '; '.join(f'{k}={v}' for k,v in par.items()) + ';'
            sim.scen = scen
            sim.par = par

            ns = new_schools(scen) # Not sure if need new mem for each
            sim['interventions'] += [ns]
            sims.append(sim)

    msim = cv.MultiSim(sims)
    msim.run(reseed=False, par_args={'ncpus': 16}, noise=0.0, keep_people=False)

    cv.save('msim.obj', msim)
