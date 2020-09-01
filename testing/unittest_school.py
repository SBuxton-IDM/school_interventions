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
•	Loop through school closure options which are applied to other schools (if you are infecting an ES, modify HS and MS)
Verification
•	Ensure that more and more schools are opened as the simulator steps through the days
Test 4: Number needed to close schools boundaries
Configuation: 
•	pop_infected: 0/school_size
•	"No flu like illness"
•	Enable school closure intervention
Verification:
•	assert that all schools are closed with a pop_infected of 0
•	assert that when num_pos = school_size the school shuts down if all students are infected
Test 5: Determine that iliprev has reasonable boundaries
Configuration:
•	pop_infected = 0
•	Enable school closure intervention
•	Set ili_prev to 0 and -1
Verification:
•	Ensure that both ili_prev values throw appropriate exceptions
Test 6: Test frequency and accuracy should observe all infections when perfect
Configuration
•	pop_infected: 1000
•	"No flu like illness"
•	Set test_freq and test to 1
Verification:
•	num_diagnosed should be equal to cum_infected
Test 7: Raising ili_prev should increase the number of school days lost
•	pop_infected: 1000
•	Set test_freq and test to random but consistent values
Verification:
•	changing ili_prev from .15 to .4 should increase the total number of schools days lost
Test 8: Raising ili_prev should 
•	pop_infected: 1000
•	"No flu like illness"
•	Set test_freq and test to 1
Verification:
•	num_diagnosed should be equal to cum_infected
Test 9: Raising num_pos should lead to same or fewer days lost due to school closures
•	pop_infected: 100
•	"No flu like illness"
•	Set num_pos from 1 to 10 to 100
Verification:
•	As num_pos increases ensure that days lost are either decreasing or the same
•	Test that there is a difference between num_pos=1 and num_pos=100
Test 10: Raising num_pos should lead to same or fewer days lost due to school closures
•	pop_infected: 100
•	"No flu like illness"
•	Set num_pos from 1 to 10 to 100
Verification:
•	As num_pos increases ensure that days lost are either decreasing or the same
•	Test that there is a difference between num_pos=1 and num_pos=100



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
                start_day= day_schools_open,
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
                sim.step()
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

    def iliprevExceptions(self):
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


    def testingParams(self):
        pars = {'pop_size': 1000,
                'pop_scale': 10,
                'pop_type': 'synthpops',
                'pop_infected': 20,
                'rescale': True,
                'verbose': 1,
                'start_day': '2020-08-01',
                'end_day': '2020-09-01',
                'rand_seed': 0,
                }
        popfile = f'inputs/kc_synthpops_clustered_withstaff_10e3.ppl'
        sim = cv.Sim(pars, popfile=popfile, load_pop=True)

        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-01',
                test=1,
                test_freq=1,
                ili_prev=0.25,
                num_pos=None, 
                label='reopen_schools'
            )
        interventions = [
            cv.close_schools(
                    day_schools_closed='2020-08-01',
                    start_day='2020-08-01',
                    label='close_schools'
                ),
            reopen_schools
            ]

        sim['interventions'] = interventions

        sim.run()
        # No students should be left undiagnosed
        self.assertEqual(reopen_schools.num_undiagnosed, 0)

    def testingIliSchoolDays(self):
        pars = {'pop_size': 1000,
                'pop_scale': 10,
                'pop_type': 'synthpops',
                'pop_infected': 20,
                'rescale': True,
                'verbose': 1,
                'start_day': '2020-08-01',
                'end_day': '2020-09-01',
                'rand_seed': 0,
                }
        popfile = f'inputs/kc_synthpops_clustered_withstaff_10e3.ppl'
        sim = cv.Sim(pars, popfile=popfile, load_pop=True)

        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-01',
                test=0.8,
                test_freq=0.5,
                ili_prev=0.15,
                num_pos=None, 
                label='reopen_schools'
            )
        interventions = [
            cv.close_schools(
                    day_schools_closed='2020-08-01',
                    start_day='2020-08-01',
                    label='close_schools'
                ),
            reopen_schools
            ]

        sim['interventions'] = interventions

        sim.run()
        # No students should be left undiagnosed
        num_school_days_lost_i = sim.school_info['school_days_lost']

        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-01',
                test=0.8,
                test_freq=0.5,
                ili_prev=0.5,
                num_pos=None, 
                label='reopen_schools'
            )
        interventions = [
            cv.close_schools(
                    day_schools_closed='2020-08-01',
                    start_day='2020-08-01',
                    label='close_schools'
                ),
            reopen_schools
            ]

        sim['interventions'] = interventions

        sim.run()
        # Can add more cases for greater granularity of testing
        num_school_days_lost_f = sim.school_info['school_days_lost']
        self.assertEqual(num_school_days_lost_i, num_school_days_lost_f)


    def numPosDays(self):
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
                ili_prev=0,
                num_pos=1, 
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

        sim.run()
        num_school_days_lost_a = sim.school_info['school_days_lost']

        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-05',
                test=0.99,
                ili_prev=0,
                num_pos=20, 
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

        sim.run()
        num_school_days_lost_b = sim.school_info['school_days_lost']      
        
        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-05',
                test=0.99,
                ili_prev=0,
                num_pos=100, 
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

        # This requires a bit of fenegling and testing to determine reasonable relative 
        # values
        self.assertGreater(num_school_days_lost_a, num_school_days_lost_b)
        self.assertGreater(num_school_days_lost_b, num_school_days_lost_c)

    @unittest.skip("NYI")
    def testDial(self):
            #Increasing test frequency and accuracy should increase diagnoses



    

    












        


