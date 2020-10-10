import covasim as cv
import create_sim as cs
from school_intervention import new_schools

def scenario(es, ms, hs):
    return {
        'pk': None,
        'es': es,
        'ms': ms,
        'hs': hs,
        'uv': None,
    }


if __name__ == '__main__':
    params = { 'rand_seed':0 }
    sim = cs.create_sim(params, pop_size=2.25e5)

    base = {
        'start_day': '2020-09-01', # Schools are closed until this day
        'is_hybrid': False,
        'screen_prob': 0,
        'test_prob': 0.5,
        'trace_prob': 0.5,
        'ili_prob': 0.002, # Daily ili probability
        'npi': 1
    }
    s = scenario(es=base, ms=base, hs=base)

    ns = new_schools(s)
    #bc = cv.change_beta(days='2020-09-01', changes=1, layers='s', label='close_school')
    sim['interventions'] += [ns]#, bc]

    sim.run()
    sim.plot()
    cv.savefig('sim.png')
