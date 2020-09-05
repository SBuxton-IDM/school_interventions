"""
Test 1: No one infected ever
Configuation: 
•	pop_infected: 0
•	"No flu like illness"
•	Enable school closure intervention
Verification:
•	assert that there are 0 school days lost
•	assert that total school days is non-zero
Test 2: All persons infected all the time
Configuration:
•	pop_infected = pop_size
•	Symptomatic duration starts day 1, runs to end of sim
•	Enable school closure intervention
Verification:
•	total school days lost == total potential school days
•	total potential school days is non-zero (greater than 100 would be reasonable)
Test 3: Each school type (ES, MS, HS) has its own schedule 
Configuration:
•	Beta set to 0 
•	Symptomatic period is the whole simulation (same number of infected people at all times)
•	Loop through school closure options which are applied to other schools (if you are infecting an ES, modify HS and MS)
Verification
•	Ensure that more and more schools are opened as the simulator steps through the days
Test 4: Number needed to close schools boundaries
Configuration: 
•	pop_infected: equal to num_pos for each school (DOES NOT CURRENTLY DO THIS, it is set to 100 as a placeholder)
•	"No flu like illness"
•	Enable school closure intervention
Verification:
•	assert that all schools are closed with a num_pos of 0
•	assert that when num_pos = school_size the school shuts down when num_pos students are infected
Test 5: Determine that iliprev has reasonable boundaries
Configuration:
•	pop_infected = 0
•	Set ili_prev to 1.1 and -1
Verification:
•	Ensure that both ili_prev values throw appropriate exceptions
Test 6: Test frequency and accuracy should observe all infections when perfect
Configuration
•	set all betas to 0
•	pop_infected: 1000
•	"No flu like illness"
•	Set test_freq and test to 1
Verification:
•	num_diagnosed should be equal to num_infected
Test 7: Raising ili_prev should increase the number of school days lost
•	pop_infected: 1000
•	Set test_freq and test to random but consistent values
Verification:
•	changing ili_prev from .15 to .4 should increase the total number of schools days lost
Test 8: Raising num_pos should lead to same or fewer days lost due to school closures
•	pop_infected: 100
•	"No flu like illness"
•	Set num_pos from 1 to 10 to 100
Verification:
•	As num_pos increases ensure that days lost are either decreasing or the same
•	Test that there is a difference between num_pos=1 and num_pos=100
Test 9: Increasing test should increase diagnoses
•	pop_infected: 100
•	Trace set to 0
•	Set test to 0.1 then 0.4 then 0.7
Verification:
•	As test increases num_diagnoses should also increase
Test 10: Increasing test_freq should increase diagnoses
•	pop_infected: 100
•	Trace set to 0
•	Set test_freq to daily, bi-daily, and every third day (1, 2, 3)
Verification:
•	As test_freq increases the number of diagnoses should increase
Test 11: Increasing test tracing should decrease number infected
•	pop_infected: 100
•	Trace set to 0.1, then 0.4, then 0.7
•   ili+prev set to 0
Verification:
•	As test_freq increases the number of diagnoses should increase
Test 12: Making the start day sooner should lead to more infections and fewer school days lost for each layer
•	pop_infected: 100
•	set array of schedules with increasing number of layers opening later
Verification:
•	As layers open later, number of days lost should increase
•	As layers open later, number of cum_infected should decrease


"""
import covasim as cv
import unittest
from for_testing import make_population
import sciris as sc

# This test suite tests the parameters of the two school related interventions in covid-schools
# Must run make_population first
make_population()
SIM_PARAMS = pars = {'pop_size': 20e3,
                'pop_type': 'synthpops',
                'pop_infected': 100,
                'verbose': 1,
                'start_day': '2020-08-01',
                'end_day': '2020-09-01',
                'rand_seed': 0,
                }
popfile = f'inputs/kc_synthpops_clustered_withstaff_10e3.ppl'
class SchoolParameters(unittest.TestCase):

    def noinfected(self):
        SIM_PARAMS2 = pars = {'pop_size': 20e3,
                'pop_type': 'synthpops',
                'pop_infected': 0,
                'verbose': 1,
                'start_day': '2020-08-01',
                'end_day': '2020-09-01',
                'rand_seed': 0,
                }
    popfile = f'inputs/kc_synthpops_clustered_withstaff_10e3.ppl'

    sim = cv.Sim(SIM_PARAMS2, popfile=popfile, load_pop=True)


    interventions = [
        cv.close_schools(
                day_schools_closed='2020-08-01',
                label='close_schools'
            ),
        cv.reopen_schools(
            start_day= {'pk': '2020-08-01', 'es': '2020-08-01', 'ms': '2020-08-01', 'hs': '2020-08-01', 'uv': '2020-08-01'},
            test=0.99,
            ili_prev=0,
            num_pos=None, 
            label='reopen_schools'
        ),
        cv.change_beta(1, 0)
        ]

    sim['interventions'] = interventions

    sim.run()
    num_school_days_lost = sim.school_info['school_days_lost']
    num_student_school_days = sim.school_info['total_student_school_days']

    #assertinhg that all school days are lost
    self.assertEqual(num_school_days_lost, num_student_school_days)
    self.assertGreater(num_school_days, 0)

    def allInfected(self):

        sim = cv.Sim(SIM_PARAMS, popfile=popfile, load_pop=True)
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
        day_schools_open = {'pk': '2020-08-05', 'es': '2020-08-10', 'ms': '2020-08-15', 'hs': '2020-08-20', 'uv': '2020-08-25'},


        sim = cv.Sim(SIM_PARAMS, popfile=popfile, load_pop=True)
        reopen_schools = cv.reopen_schools(
                start_day= day_schools_open,
                test=0.99, # high test in order to make the validation less prone to "stochastic effects"
                ili_prev=0,
                num_pos=None, 
                label='reopen_schools'
            )

        interventions = [
            cv.close_schools(
                    day_schools_closed='2020-08-01',
                    start_day='2020-08-05', # should be ignored
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
                newOpening = len(num for num in list(reopen_schools.close_school) if num is False) # error says .close_school is not a list??
                if newOpening > openedCounter:
                    openedCounter = newOpening
                else:
                    self.assertGreater(newOpening, openedCounter)
    
    def numposLimit(self):

        sim = cv.Sim(SIM_PARAMS, popfile=popfile, load_pop=True)
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
        self.assertEqual(list(reopen_schools.close_school).count(False), 0) # Will figure out this weird list issue promptly

        sim2 = cv.Sim(SIM_PARAMS, popfile=popfile, load_pop=True)
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
        self.assertEqual(list(reopen_schools.close_school).count(False), 0)

    def iliprevExceptions(self):

        sim = cv.Sim(SIM_PARAMS, popfile=popfile, load_pop=True)
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
        self.assertRaises(AttributeError, sim.run()) # Need to either skip this test or fine tune error message

        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-05',
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
        sim = cv.Sim(SIM_PARAMS, popfile=popfile, load_pop=True)

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
                    day_schools_closed='2020-08-01', # School shouldn't be closed at any point
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

        sim = cv.Sim(SIM_PARAMS, popfile=popfile, load_pop=True)

        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-01',
                test=0.8,
                test_freq=0.5, # Random but consistent
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
        num_school_days_lost_i = sim.school_info['school_days_lost'] # Once it's run it'll have school_info ignore the squiggly line :)

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
        self.assertGreater(num_school_days_lost_i, num_school_days_lost_f)


    def numPosDays(self):

        sim = cv.Sim(SIM_PARAMS, popfile=popfile, load_pop=True)
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

        sim.run()
        num_school_days_lost_c = sim.school_info['school_days_lost']  

        # This will require a bit of fenegling and testing to determine reasonable relative 
        # values
        self.assertGreater(num_school_days_lost_a, num_school_days_lost_b)
        self.assertGreater(num_school_days_lost_b, num_school_days_lost_c)

    def testDial(self):
        sim = cv.Sim(SIM_PARAMS, popfile=popfile, load_pop=True)
        # Setting test to 0.1, trace to 0 so that trace doesn't mess up validation
        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-05',
                test=0.1,
                trace=0,
                ili_prev=0,
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
        diagnoses_a = reopen_schools.num_diagnosed

        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-05',
                test=0.4,
                ili_prev=0,
                trace=0, 
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
        diagnoses_b = reopen_schools.num_diagnosed   
        
        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-05',
                test=0.7,
                ili_prev=0,
                trace=0,
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

        diagnoses_c = reopen_schools.num_diagnosed

        # This requires a bit of fenegling and testing to determine reasonable relative 
        # values
        self.assertGreater(diagnoses_a, diagnoses_b)
        self.assertGreater(diagnoses_b, diagnoses_c)

    
    def testFreqDial(self):
        
        sim = cv.Sim(SIM_PARAMS, popfile=popfile, load_pop=True)
        # Testing daily, bidaily, and every third day testing, trace set to 0 so it doesn't mess with validation
        # since if you have teachers tested and traced then infectious kiddos would be sent home and the infection rate would
        # be substantially lower
        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-05',
                test_freq=1,
                trace=0,
                ili_prev=0,
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
        diagnoses_a = reopen_schools.num_diagnosed

        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-05',
                test_freq=2,
                ili_prev=0,
                trace=0, 
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
        diagnoses_b = reopen_schools.num_diagnosed   
        
        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-05',
                test_freq=3,
                ili_prev=0,
                trace=0, 
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

        diagnoses_c = reopen_schools.num_diagnosed

        # This requires a bit of fenegling and testing to determine reasonable relative 
        # values
        self.assertGreater(diagnoses_c, diagnoses_b)
        self.assertGreater(diagnoses_b, diagnoses_a)

    def tracingDial(self):

        sim = cv.Sim(SIM_PARAMS, popfile=popfile, load_pop=True)

        interventions = [
            cv.close_schools(
                    day_schools_closed='2020-08-01',
                    start_day='2020-08-05',
                    label='close_schools'
                ),
            cv.reopen_schools(
                start_day= '2020-08-05',
                ili_prev=0,
                num_pos=None, 
                trace=0.1,
                label='reopen_schools'
            )
            ]

        sim['interventions'] = interventions

        sim.run()
        cum_infected_a = sim.results['cum_infections']

        interventions = [
            cv.close_schools(
                    day_schools_closed='2020-08-01',
                    start_day='2020-08-05',
                    label='close_schools'
                ),
            cv.reopen_schools(
                start_day= '2020-08-05',
                ili_prev=0,
                num_pos=None, 
                trace=0.4,
                label='reopen_schools'
            )
            ]

        sim['interventions'] = interventions

        sim.run()
        cum_infected_b = sim.results['cum_infections']

        interventions = [
            cv.close_schools(
                    day_schools_closed='2020-08-01',
                    start_day='2020-08-05',
                    label='close_schools'
                ),
            cv.reopen_schools(
                start_day= '2020-08-05',
                ili_prev=0,
                num_pos=None, 
                trace=0.7,
                label='reopen_schools'
            )
            ]

        sim['interventions'] = interventions

        sim.run()
        cum_infected_c = sim.results['cum_infections']

        self.assertGreater(cum_infected_c, cum_infected_b)
        self.assertGreater(cum_infected_b, cum_infected_a)

    # Takes a long time to run so probably best skipped in most cases
    def lostDaysStartDay(self):
        day_schools_open1 = {'pk': '2020-08-05', 'es': '2020-08-05', 'ms': '2020-08-05', 'hs': '2020-08-05', 'uv': '2020-08-05'}
        day_schools_open2 = {'pk': '2020-08-25', 'es': '2020-08-05', 'ms': '2020-08-05', 'hs': '2020-08-05', 'uv': '2020-08-05'}
        day_schools_open3 = {'pk': '2020-08-25', 'es': '2020-08-25', 'ms': '2020-08-05', 'hs': '2020-08-05', 'uv': '2020-08-05'}
        day_schools_open4 = {'pk': '2020-08-25', 'es': '2020-08-25', 'ms': '2020-08-25', 'hs': '2020-08-05', 'uv': '2020-08-05'}
        day_schools_open5 = {'pk': '2020-08-25', 'es': '2020-08-25', 'ms': '2020-08-25', 'hs': '2020-08-25', 'uv': '2020-08-05'}
        day_schools_open6 = {'pk': '2020-08-25', 'es': '2020-08-25', 'ms': '2020-08-25', 'hs': '2020-08-25', 'uv': '2020-08-25'}
        day_schools_open = [day_schools_open1, day_schools_open2, day_schools_open3, day_schools_open4, day_schools_open5, day_schools_open6]
        

        sim = cv.Sim(SIM_PARAMS, popfile=popfile, load_pop=True)

        cum_infected_prev = -1
        num_school_days_lost_prev = 10000000
        for schedule in day_schools_open:
            interventions = [
                cv.close_schools(
                        day_schools_closed='2020-08-01',
                        start_day='2020-08-05',
                        label='close_schools'
                    ),
                cv.reopen_schools(
                    start_day= schedule,
                    ili_prev=0,
                    num_pos=None, 
                    trace=0.1,
                    label='reopen_schools'
                )
                ]

            sim['interventions'] = interventions

            sim.run()
            cum_infected_current = sim.results['cum_infections']
            num_school_days_lost = sim.school_info['school_days_lost']

            self.assertGreater(cum_infected_current, cum_infected_prev)
            self.assertGreater(num_school_days_lost_prev, num_school_days_lost)

            cum_infected_prev = cum_infected_current
            num_school_days_lost_prev = num_school_days_lost



        






    











    

    












        


