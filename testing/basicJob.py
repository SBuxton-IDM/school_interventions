import covasim as cv
import unittest
from for_testing import make_population
import sciris as sc
import os

popfile = f'inputs/kc_synthpops_clustered_withstaff_10e3.ppl'
if not os.path.exists(popfile):
    make_population()


SIM_PARAMS = {'pop_size': 10e3,
                'pop_type': 'synthpops',
                'pop_infected': 0,
                'verbose': 1,
                'start_day': '2020-08-01',
                'end_day': '2020-08-30',
                'rand_seed': 0,
                }
sim = cv.Sim(SIM_PARAMS, popfile=popfile, load_pop=True)

reopen_schools = cv.reopen_schools(
        start_day= {'pk': '2020-08-05', 'es': '2020-08-05', 'ms': '2020-08-05', 'hs': '2020-08-05', 'uv': '2020-08-05'},
        ili_prev=0, 
        label='reopen_schools'
    )
interventions = [
    cv.close_schools(
            day_schools_closed='2020-08-01',
            label='close_schools'
        ),
    reopen_schools
    ]

sim['interventions'] = interventions

sim.run()
# No students should be left undiagnosed
num_school_days_lost_a = sim.school_info['school_days_lost']

reopen_schools = cv.reopen_schools(
        start_day= {'pk': '2020-08-05', 'es': '2020-08-05', 'ms': '2020-08-05', 'hs': '2020-08-05', 'uv': '2020-08-05'},
        ili_prev=1,
        test=0,
        label='reopen_schools'
    )
interventions = [
    cv.close_schools(
            day_schools_closed='2020-08-01',
            label='close_schools'
        ),
    reopen_schools
    ]

sim['interventions'] = interventions

sim.run()
# Can add more cases for greater granularity of testing
num_school_days_lost_b = sim.school_info['school_days_lost']

assert num_school_days_lost_b >num_school_days_lost_a, f"{num_school_days_lost_b} not greater than {num_school_days_lost_a}"