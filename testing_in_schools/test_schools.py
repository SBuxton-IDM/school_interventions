import covasim as cv
import create_sim as cs


if __name__ == '__main__':
    params = { 'rand_seed':0 }
    sim = cs.run_sim(params, run=False)

    ns = cv.new_schools(start_day=None, ili_prev=None, test_freq=None, trace_frac=None, test_frac=None, schedule=None)

    sim['interventions'] += [ns]
    sim.run()
