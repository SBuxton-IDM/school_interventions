'''
Pre-generate the synthpops population including school types. Takes ~102s per seed
'''

import psutil
import sciris  as sc
import covasim as cv
import synthpops as sp
sp.config.set_nbrackets(20) # Essential for getting the age distribution right

def cache_populations(seed=0, popfile=None):
    ''' Pre-generate the synthpops population '''

    pars = sc.objdict(
        pop_size = 225e3,
        pop_type = 'synthpops',
        rand_seed = seed,
    )

    with_school_types = True
    school_mixing_type = 'clustered'

    if popfile is None:
        popfile = f'inputs/kc_synthpops_with_ltcf_seed{pars.rand_seed}.ppl'

    T = sc.tic()
    print(f'Making "{popfile}"...')
    sim = cv.Sim(pars)
    cv.make_people(sim, popfile=popfile, save_pop=True, generate=True, with_facilities=True,
                   with_school_types=with_school_types, school_mixing_type=school_mixing_type)
    sc.toc(T)

    print('Done')
    return


if __name__ == '__main__':

    seeds = [0,1,2,3,4]

    for seed in seeds:
        cache_populations(seed)