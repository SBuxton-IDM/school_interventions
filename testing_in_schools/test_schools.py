import os
import covasim as cv
import numpy as np
import create_sim as cs
import sciris as sc
from school_intervention import new_schools
from testing_scenarios import generate_scenarios, generate_testing
from calibrate_model import evaluate_sim

debug = False
folder = 'v20201013_225k_v2'
pop_size = 2.25e5 # 1e5 2.25e4 2.25e5
calibfile = os.path.join(folder, 'pars_cases_begin=75_cases_end=75_re=1.0_prevalence=0.002_yield=0.024_tests=225_v2_pop_size=225000.json')

def scenario(es, ms, hs):
    return {
        'pk': None,
        'es': sc.dcp(es),
        'ms': sc.dcp(ms),
        'hs': sc.dcp(hs),
        'uv': None,
    }

if __name__ == '__main__':

    entry = sc.loadjson(calibfile)[0]
    params = sc.dcp(entry['pars'])
    params['rand_seed'] = int(entry['index'])

    scen = generate_scenarios()['all_remote']
    testing = generate_testing()['None']
    #testing[0]['delay'] = 0
    for stype, spec in scen.items():
        if spec is not None:
            spec['testing'] = testing
    scen['testing'] = testing
    scen['es']['verbose'] = scen['ms']['verbose'] = scen['hs']['verbose'] = debug

    sim = cs.create_sim(params, pop_size=pop_size, folder=folder)

    ns = new_schools(scen)
    sim['interventions'] += [ns]

    sim.run(keep_people=debug)

    stats = evaluate_sim(sim)
    print(stats)

    if debug:
        sim.plot(to_plot='overview')
        #t = sim.make_transtree()
    else:
        sim.plot()

    cv.savefig('sim.png')
