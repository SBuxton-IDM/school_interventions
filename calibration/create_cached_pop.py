'''
Pre-generate the population including school types. Takes about 70 s.
'''

import psutil
import sciris  as sc
import covasim as cv
import synthpops as sp
sp.config.set_nbrackets(20) # Essential for getting the age distribution right

def cache_populations(seed=0, popfile=None):
    ''' Pre-generate the hyrbid population '''

    pars = sc.objdict(
        pop_size = 225e3,
        pop_type = 'hybrid',
        rand_seed = seed,
    )

    if popfile is None:
        popfile = f'inputs/kc_hybrid_seed{pars.rand_seed}.ppl'

    T = sc.tic()
    print(f'Making "{popfile}"...')
    sim = cv.Sim(pars)
    cv.make_people(sim, popfile=popfile, save_pop=True, school_type=True,
                   school_type_ages=[[6, 11], [11, 14], [14, 18], [18, 22]])
    sc.toc(T)

    print('Done')
    return


if __name__ == '__main__':

    seeds = [0,1,2,3,4] # NB, each one takes 8 GB of RAM! -- split up 0-4 in pieces
    ram = psutil.virtual_memory().available/1e9
    required = 8*len(seeds)
    # if required < ram:
    #     print(f'You have {ram} GB of RAM, and this is estimated to require {required} GB: you should be fine')
    # else:
    #     raise ValueError(f'You have {ram:0.2f} GB of RAM, but this is estimated to require {required} GB')
    sc.parallelize(cache_populations, iterarg=seeds) # Run them in parallel
