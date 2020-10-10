import covasim as cv
import create_sim as cs
from school_intervention import new_schools

debug = True

def scenario(es, ms, hs):
    return {
        'pk': None,
        'es': es,
        'ms': ms,
        'hs': hs,
        'uv': None,
    }


if __name__ == '__main__':
    params = {
        'rand_seed': 99,
        'pop_infected': 259.6044361233582,
        'clip_edges': 0.12707079671380783
    }
    sim = cs.create_sim(params, pop_size=1e5) # 2.25e4

    base = {
        'start_day': '2020-09-01',
        'is_hybrid': False,
        'screen_prob': 0.9,
        'test_prob': 0.5,
        'trace_prob': 0.5,
        'ili_prob': 0.002, # Daily ili probability equates to about 10% incidence over the first 3 months of school
        'beta_s': 0.75 * sim.pars['beta_layer']['s']
    }

    remote = {
        'start_day': '2020-09-01',
        'is_hybrid': False,
        'screen_prob': 0,
        'test_prob': 0,
        'trace_prob': 0,
        'ili_prob': 0,
        'beta_s': 0 # This turns off transmission in the School class
    }

    s = scenario(es=remote, ms=remote, hs=remote)

    ns = new_schools(s)
    sim['interventions'] += [ns]

    sim.run(keep_people=debug)

    first_school_day = sim.day('2020-09-01')
    last_school_day = sim.day('2020-12-01')
    import pandas as pd
    rdf = pd.DataFrame(sim.results)
    re = rdf['r_eff'].iloc[first_school_day:last_school_day, ].mean(axis=0)
    cases_past14 = rdf['new_diagnoses'].iloc[(first_school_day-14):first_school_day, ].sum(axis=0) * 100e3 / (sim.pars['pop_size'] * sim.pars['pop_scale'])
    cases_during = rdf['new_diagnoses'].iloc[first_school_day:last_school_day, ].mean(axis=0) * 14 * 100e3 / (sim.pars['pop_size'] * sim.pars['pop_scale'])
    re_to_fit = 1.0
    cases_to_fit = 100
    re_mismatch = (re_to_fit - re)**2 / re_to_fit**2
    cases_past14_mismatch = (cases_to_fit - cases_past14)**2 / cases_to_fit**2
    cases_during_mismatch = (cases_to_fit - cases_during)**2 / cases_to_fit**2
    mismatch = re_mismatch + cases_past14_mismatch + cases_during_mismatch

    print(re, cases_past14_mismatch, cases_during_mismatch, mismatch, (sim.pars['pop_size'] * sim.pars['pop_scale']))


    if debug:
        sim.plot(to_plot='overview')
        #t = sim.make_transtree()
    else:
        sim.plot()

    cv.savefig('sim.png')
