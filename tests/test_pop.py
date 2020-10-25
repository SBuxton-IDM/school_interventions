'''
Very simple test of population generation
'''

import pylab as pl
import covasim as cv
import covasim_schools as cvsch

def test_school_pop(do_plot=False):
    ''' Test basic population creation '''

    pop = cvsch.make_population(pop_size=20e3, rand_seed=1, do_save=False)

    if do_plot:
        pop.plot()

    return pop


def plot_schools(pop):
    ''' Not a formal test, but a sanity check for school distributions '''
    keys = ['pk', 'es', 'ms', 'hs'] # Exclude universities for this analysis
    school_types_by_ind = {}
    for key,vals in pop.school_types.items():
        for val in vals:
            if key in keys:
                school_types_by_ind[val] = key

    fig = pl.figure()
    cv.maximize()

    return fig


if __name__ == '__main__':
    pop = test_school_pop(do_plot=True)
    fig = plot_schools(pop)