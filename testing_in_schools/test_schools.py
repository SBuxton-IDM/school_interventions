import covasim as cv
import create_sim as cs
from school_intervention import new_schools, Scenario


if __name__ == '__main__':
    params = { 'rand_seed':0 }
    sim = cs.create_sim(params)

    s = Scenario()

    #ns = new_schools(start_day=None, ili_prev=None, test_freq=None, trace_frac=None, test_frac=None, schedule=None)
    ns = new_schools(s.scenario)
    sim['interventions'] += [ns]

    sim.run()
    sim.plot()
    cv.savefig('sim.png')
