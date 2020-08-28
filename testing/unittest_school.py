"""
Test 1: No one infected ever
Configuation: 
•	pop_infected: 0
•	"No flu like illness"
•	Enable school closure intervention
Verification:
•	assert that there are 0 school days lost
•	assert that there are "some number" of school days (more than 0 is probably okay, but maybe we could pick a bigger number… more than 40 or something)
Test 2: All persons infected all the time
Configuration:
•	pop_infected = pop_size
•	Symptomatic duration starts day 1, runs to end of sim (I think I know how to do this)
•	Enable school closure intervention
Verification:
•	total school days lost == total potential school days
•	total potential school days is "some believable number"
Test 3: Each school type (ES, MS, HS) has its own schedule
Configuration:
•	Beta set to 0 
•	Symptomatic period is the whole simulation (same number of infected people at all times)
•	0 people infected at start, infect an entire school (just student?) population on day 1, school year starts day 2
•	Loop through school closure options which are applied to other schools (if you are infecting an ES, modify HS and MS)
"""
import covasim as cv
import unittest
from for_testing import make_population
import sciris as sc

# This test suite tests the parameters of the two school related interventions in covid-schools
# Must run make_population first
class SchoolParameters():
    def noinfected(self):

        pars = {'pop_size': 20e3,
                'pop_scale': 10,
                'pop_type': 'synthpops',
                'pop_infected': 0,
                'rescale': True,
                'verbose': 1,
                'start_day': '2020-08-01',
                'end_day': '2020-09-01',
                'rand_seed': 0,
                }
        popfile = f'inputs/kc_synthpops_clustered_withstaff_10e3.ppl'
        sim = cv.Sim(pars, popfile=popfile, load_pop=True)

        interventions = [
            cv.close_schools(
                    day_schools_closed='2020-08-01',
                    start_day='2020-08-15',
                    label='close_schools'
                ),
            cv.reopen_schools(
                start_day= '2020-08-15',
                test=0.99,
                ili_prev=0,
                num_pos=None, 
                label='reopen_schools'
            )
            ]

        sim['interventions'] = interventions

        sim.run()
        cum_infected = sim.results['cum_infections']

        assert cum_infected[-1] == 0

    def allInfected(self):
        make_population()

        day_schools_open = {'pk': None, 'es': '2020-08-05', 'ms': '2020-08-05', 'hs': '2020-08-05', 'uv': None},

        pars = {'pop_size': 20e3,
                'pop_scale': 10,
                'pop_type': 'synthpops',
                'pop_infected': 20e3,
                'rescale': True,
                'verbose': 1,
                'start_day': '2020-08-01',
                'end_day': '2020-08-30',
                'rand_seed': 0,
                }
        popfile = f'inputs/kc_synthpops_clustered_withstaff_10e3.ppl'
        sim = cv.Sim(pars, popfile=popfile, load_pop=True)
        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-10',
                test=0.99,
                ili_prev=0,
                num_pos=None, 
                label='reopen_schools'
            )

        interventions = [
            cv.close_schools(
                    day_schools_closed='2020-08-01',
                    start_day='2020-08-10',
                    label='close_schools'
                ),
            reopen_schools
            ]

        sim['interventions'] = interventions

        sim.run()
        #asserting that all schools are closed 
        self.assertEqual(len([i for i in reopen_schools.close_school if i == False]), 0)
        
        num_school_days_lost = sim.school_info['school_days_lost']
        num_student_school_days = sim.school_info['total_student_school_days']

        #assertinhg that all school days are lost
        self.assertEqual(num_school_days_lost, num_student_school_days)

    def differentSchedules(self):
        # Setting up different schedules and ensuring that the simulation closes schools on right days
        make_population()

        day_schools_open = {'pk': '2020-08-05', 'es': '2020-08-10', 'ms': '2020-08-15', 'hs': '2020-08-20', 'uv': '2020-08-25'},

        pars = {'pop_size': 20e3,
                'pop_scale': 10,
                'pop_type': 'synthpops',
                'pop_infected': 100,
                'rescale': True,
                'verbose': 1,
                'start_day': '2020-08-01',
                'end_day': '2020-08-31',
                'rand_seed': 0,
                }
        popfile = f'inputs/kc_synthpops_clustered_withstaff_10e3.ppl'
        sim = cv.Sim(pars, popfile=popfile, load_pop=True)
        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-05',
                test=0.99,
                ili_prev=0,
                num_pos=None, 
                label='reopen_schools'
            )

        interventions = [
            cv.close_schools(
                    day_schools_closed='2020-08-01',
                    start_day='2020-08-05',
                    label='close_schools'
                ),
            reopen_schools
            ]

        sim['interventions'] = interventions
        openedCounter = 0
        # asserts that each 5th day there are more opened schools than before
        for i in range(1, 26):
            sim.step()
            if i % 5 == 0:
                sim.step():
                    newOpening = len(num for num in reopen_schools.close_school if num is False)
                    if newOpening > openedCounter:
                        openedCounter = newOpening
                    else:
                        self.assertGreater(newOpening, openedCounter)
    
    def numposLimit(self):
        make_population()

        day_schools_open = {'pk': '2020-08-05', 'es': '2020-08-10', 'ms': '2020-08-15', 'hs': '2020-08-20', 'uv': '2020-08-25'},

        pars = {'pop_size': 20e3,
                'pop_scale': 10,
                'pop_type': 'synthpops',
                'pop_infected': 20e3,
                'rescale': True,
                'verbose': 1,
                'start_day': '2020-08-01',
                'end_day': '2020-08-30',
                'rand_seed': 0,
                }
        popfile = f'inputs/kc_synthpops_clustered_withstaff_10e3.ppl'
        sim = cv.Sim(pars, popfile=popfile, load_pop=True)
        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-05',
                test=0.99,
                ili_prev=0,
                num_pos=0, 
                label='reopen_schools'
            )

        interventions = [
            cv.close_schools(
                    day_schools_closed='2020-08-01',
                    start_day='2020-08-05',
                    label='close_schools'
                ),
            reopen_schools
            ]
        
        sim.run()
        self.assertEqual(reopen_schools.close_school.count(False), 0)

        sim2 = cv.Sim(pars, popfile=popfile, load_pop=True)
        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-05',
                test=0.99,
                ili_prev=0,
                num_pos=100, #need to find a way to get sizes of schools
                label='reopen_schools'
            )

        interventions = [
            cv.close_schools(
                    day_schools_closed='2020-08-01',
                    start_day='2020-08-05',
                    label='close_schools'
                ),
            reopen_schools
            ]
        
        sim.run()
        self.assertEqual(reopen_schools.close_school.count(False), 0)

    def iliprevExceptions:
        make_population()

        pars = {'pop_size': 20e3,
                'pop_scale': 10,
                'pop_type': 'synthpops',
                'pop_infected': 20e3,
                'rescale': True,
                'verbose': 1,
                'start_day': '2020-08-01',
                'end_day': '2020-08-30',
                'rand_seed': 0,
                }
        popfile = f'inputs/kc_synthpops_clustered_withstaff_10e3.ppl'
        sim = cv.Sim(pars, popfile=popfile, load_pop=True)
        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-05',
                test=0.99,
                ili_prev=2,
                num_pos=0, 
                label='reopen_schools'
            )

        interventions = [
            cv.close_schools(
                    day_schools_closed='2020-08-01',
                    start_day='2020-08-05',
                    label='close_schools'
                ),
            reopen_schools
            ]
        sim['interventions'] = interventions
        self.assertRaises(AttributeError, sim.run())

        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-05',
                test=0.99,
                ili_prev=-1,
                num_pos=0, 
                label='reopen_schools'
            )

        interventions = [
            cv.close_schools(
                    day_schools_closed='2020-08-01',
                    start_day='2020-08-05',
                    label='close_schools'
                ),
            reopen_schools
            ]
        sim['interventions'] = interventions
        self.assertRaises(AttributeError, sim.run())












        


