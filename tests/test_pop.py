'''
Very simple test of population generation
'''

import numpy as np
import pylab as pl
import sciris as sc
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

    results = {}
    for sc_id,sc_type in school_types_by_ind.items():
        thisres = sc.objdict()
        sc_inds = (pop.school_id == sc_id)
        thisres.all = sc_inds
        thisres.students = cv.true(np.array(pop.student_flag) * sc_inds)
        thisres.teachers = cv.true(np.array(pop.teacher_flag) * sc_inds)
        thisres.staff    = cv.true(np.array(pop.staff_flag) * sc_inds)
        results[sc_id] = thisres

    # Do plotting
    fig = pl.figure()
    n_schools = len(results)
    i = 0
    for s,sc_id in enumerate(results.keys()):
        pl.subplot(n_schools, 4, i+1)
    # cv.maximize(fig=fig)

    return results


if __name__ == '__main__':
    pop = test_school_pop(do_plot=True)
    results = plot_schools(pop)