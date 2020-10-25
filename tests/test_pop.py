'''
Very simple test of population generation
'''

import covasim_schools as cvsch

def test_school_pop(do_plot=False):
    pop = cvsch.make_population(pop_size=20e3, rand_seed=1, do_save=False)

    if do_plot:
        pop.plot()
    return pop

if __name__ == '__main__':
	pop = test_school_pop(do_plot=True)