'''
Pre-generate the synthpops population including school types. Takes ~102s per seed
'''

import psutil
import sciris  as sc
import covasim_schools as cvsch

pop_size = 20e3
seeds = [0,1,2,3,4]
parallelize = True
# parallelize = False

if parallelize:
    ram = psutil.virtual_memory().available/1e9
    required = 1*len(seeds)*pop_size/225e3 # 8 GB per 225e3 people
    if required < ram:
        print(f'You have {ram} GB of RAM, and this is estimated to require {required} GB: you should be fine')
    else:
        print(f'You have {ram:0.2f} GB of RAM, but this is estimated to require {required} GB -- you are in trouble!!!!!!!!!')
    sc.parallelize(cvsch.make_population, kwargs={'pop_size':pop_size}, iterkwargs={'rand_seed':seeds}) # Run them in parallel
else:
    for seed in seeds:
        cvsch.make_population(pop_size=pop_size, rand_seed=seed)
