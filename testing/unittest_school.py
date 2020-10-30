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
Test 4: Numpos value of 0 leads to all schools closing
Configuration: 
•	"No flu like illness"
•	Enable school closure intervention
Verification:
•	assert that all schools are closed with a num_pos of 0
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
import os

# This test suite tests the parameters of the two school related interventions in covid-schools
# Must run make_population first
popfile = f'inputs/kc_synthpops_clustered_withstaff_10e3.ppl'
if not os.path.exists(popfile):
    make_population()
    
SIM_PARAMS = pars = {'pop_size': 10e3,
                'pop_type': 'synthpops',
                'pop_infected': 100,
                'verbose': 1,
                'start_day': '2020-08-01',
                'end_day': '2020-09-01',
                'rand_seed': 0,
                }
class SchoolParameters(unittest.TestCase):

    def test_no_infected(self):
        SIM_PARAMS2 = {'pop_size': 10e3,
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
                start_day= '2020-08-01',
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
        self.assertEqual(num_school_days_lost, 0)
        self.assertGreater(num_student_school_days, 0)

    def test_all_infected(self):
        SIM_PARAMS3 = {'pop_size': 10e3,
                'pop_type': 'synthpops',
                'pop_infected': 10e3,
                'verbose': 1,
                'start_day': '2020-08-01',
                'end_day': '2020-09-01',
                'rand_seed': 0,
                }

        sim = cv.Sim(SIM_PARAMS3, popfile=popfile, load_pop=True)
        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-05',
                test=0.99,
                ili_prev=0,
                num_pos=50, 
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
        #asserting that all schools are closed 
        self.assertEqual(reopen_schools.num_schools, reopen_schools.school_closures)
        
        num_school_days_lost = sim.school_info['school_days_lost']
        num_student_school_days = sim.school_info['total_student_school_days']

        #assertinhg that all school days are lost
        self.assertEqual(num_school_days_lost, num_student_school_days)

    # Works as intended but produces bug
    def test_different_schedules(self):
        day_schools_open1 = {'pk': '2020-08-05', 'es': '2020-09-05', 'ms': '2020-09-05', 'hs': '2020-09-05', 'uv': '2020-09-05'}
        day_schools_open2 = {'pk': '2020-08-05', 'es': '2020-08-05', 'ms': '2020-09-05', 'hs': '2020-09-05', 'uv': '2020-09-05'}
        day_schools_open3 = {'pk': '2020-08-05', 'es': '2020-08-05', 'ms': '2020-09-05', 'hs': '2020-09-05', 'uv': '2020-09-05'}
        day_schools_open4 = {'pk': '2020-08-05', 'es': '2020-08-05', 'ms': '2020-08-05', 'hs': '2020-08-05', 'uv': '2020-09-05'}
        day_schools_open5 = {'pk': '2020-08-05', 'es': '2020-08-05', 'ms': '2020-08-05', 'hs': '2020-08-05', 'uv': '2020-08-05'}

        school_types = ['pk', 'es', 'ms', 'hs', 'uv']

        schedules = [day_schools_open1, day_schools_open2, day_schools_open3, day_schools_open4, day_schools_open5]
        popfile = f'inputs/kc_synthpops_clustered_withstaff_10e3.ppl'
        SIM_PARAMS5 = pars = {'pop_size': 10e3,
                        'pop_type': 'synthpops',
                        'pop_infected': 100,
                        'verbose': 1,
                        'start_day': '2020-08-01',
                        'end_day': '2020-09-10',
                        'rand_seed': 0,
                        }


        sim = cv.Sim(SIM_PARAMS5, popfile=popfile, load_pop=True)

        opened_initial = 10000 #arbitrarily large number
        for i, schedule in enumerate(schedules):
            reopen_schools = cv.reopen_schools(
                    start_day= schedule,
                    test=0.99, # high test in order to make the validation less prone to "stochastic effects"
                    ili_prev=0,
                    num_pos=None, 
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
            new_opened = reopen_schools.closed.count(False) #ensuring that fewer and fewer schools closed
            self.assertGreater(new_opened, initial_opened)
            opened_initial = new_opened
    
    #Checks to see that if num_pos is 0 then no schools should be open
    def test_numpos_limit(self):
        SIM_PARAMS6 = {'pop_size': 10e3,
                'pop_type': 'synthpops',
                'pop_infected': 100,
                'verbose': 1,
                'start_day': '2020-08-01',
                'end_day': '2020-08-10',
                'rand_seed': 0,
                }

        sim = cv.Sim(SIM_PARAMS6, popfile=popfile, load_pop=True)
        reopen_schools = cv.reopen_schools(
                start_day= {'pk': '2020-08-05', 'es': '2020-08-05', 'ms': '2020-08-05', 'hs': '2020-08-05', 'uv': '2020-08-05'},
                test=0.99,
                ili_prev=0,
                num_pos=0, 
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
        self.assertEqual(reopen_schools.num_schools, reopen_schools.closed.count(True)) # Ensuring that all schools are closed


    def test_iliprev_exceptions(self):
        SIM_PARAMS6 = {'pop_size': 10e3,
                'pop_type': 'synthpops',
                'pop_infected': 100,
                'verbose': 1,
                'start_day': '2020-08-01',
                'end_day': '2020-09-91',
                'rand_seed': 0,
                }
        # testing higher value of ili_prev
        sim = cv.Sim(SIM_PARAMS6, popfile=popfile, load_pop=True)
        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-05',
                test=0.99,
                ili_prev=2,
                label='reopen_schools'
            )
        # testing negative value of ili_prev
        interventions = [
            cv.close_schools(
                    day_schools_closed='2020-08-01',
                    start_day='2020-08-05',
                    label='close_schools'
                ),
            reopen_schools
            ]
        sim['interventions'] = interventions
        self.assertRaises(ValueError, sim.run) # Need to either skip this test or fine tune error message

        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-05',
                ili_prev= -1,
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
        self.assertRaises(ValueError, sim.run)

    # Works as intended but produces error
    def test_testing_params(self):
        SIM_PARAMS = {'pop_size': 10e3,
                        'pop_type': 'synthpops',
                        'pop_infected': 100,
                        'verbose': 1,
                        'start_day': '2020-08-01',
                        'end_day': '2020-09-01',
                        'rand_seed': 0,
                        }
        sim = cv.Sim(SIM_PARAMS, popfile=popfile, load_pop=True)

        reopen_schools = cv.reopen_schools(
                start_day= {'pk': '2020-08-05', 'es': '2020-08-05', 'ms': '2020-08-05', 'hs': '2020-08-05', 'uv': '2020-08-05'},
                test=1,
                test_freq=1,
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
        self.assertEqual(reopen_schools.num_undiagnosed, 0)

    def test_ili_schooldays(self):

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
                ili_prev=0.8,
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

        self.assertGreater(num_school_days_lost_b, num_school_days_lost_a)

    #@unittest.skip("Works as intended but creates issue: #47")
    def test_numpos_days(self):

        sim = cv.Sim(SIM_PARAMS, popfile=popfile, load_pop=True)
        reopen_schools = cv.reopen_schools(
                start_day= '2020-08-05',
                test=0.99,
                num_pos=1, 
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
        num_school_days_lost_a = sim.school_info['school_days_lost']      
        
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
                    label='close_schools'
                ),
            reopen_schools
            ]
        sim['interventions'] = interventions

        sim.run()
        num_school_days_lost_b = sim.school_info['school_days_lost']  

        # This will require a bit of fenegling and testing to determine reasonable relative 
        # values
        self.assertGreater(num_school_days_lost_a, num_school_days_lost_b)

    #@unittest.skip("Works as intended but produces bug #47")
    def test_testing_dial(self):
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
                test=0.8,
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

    #@unittest.skip("Reveals a bug (increased testing yields 0 more teachers tested)")
    def test_freq_dial(self):
        is_debugging = False
        SIM_PARAMS8 = {'pop_size': 10e3,
                'pop_type': 'synthpops',
                'pop_infected': 5e3,
                'verbose': 1,
                'start_day': '2020-08-01',
                'end_day': '2020-08-30',
                'rand_seed': 0,
                }
        sim = cv.Sim(SIM_PARAMS8, popfile=popfile, load_pop=True)
        # Testing daily, bidaily, and every third day testing, trace set to 0 so it doesn't mess with validation
        # since if you have teachers tested and traced then infectious kiddos would be sent home and the infection rate would
        # be substantially lower
        results = []
        for i in range(1, 3):
            reopen_schools = cv.reopen_schools(
                    start_day= {'pk': '2020-08-05', 'es': '2020-08-05', 'ms': '2020-08-05', 'hs': '2020-08-05', 'uv': '2020-08-05'},
                    test_freq=i,
                    trace=0,
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
            
            # May want to load school_info from differently saved json
            #sim.to_json(output_filename=f"DEBUG_test_freq_{i}.json")
            #with open(f"json_test_allinfected.json") as f:
            #    json_format = json.load(f)
            
            results.append(sim.school_info['num_teachers_tested'])

           

            

        # This requires a bit of fenegling and testing to determine reasonable relative 
        # values, but more frequent testing should lead to more diagnoses in absence of tracing
        self.assertGreater(results[0], results[1])
        self.assertGreater(results[1], results[2])

    #@unittest.skip("Still need to mess with relative values to get it to be reasonable")
    def test_tracing_dial(self):

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
    @unittest.skip("Not yet tested and takes a long time to run")
    def test_lost_days_startday(self):
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

def make_population(seed=1, popfile=None):
    ''' Pre-generate the synthpops population '''

    pars = sc.objdict(
        pop_size = 20e3,
        pop_type = 'synthpops',
        rand_seed = seed,
    )

    use_two_group_reduction = True
    average_LTCF_degree = 20
    ltcf_staff_age_min = 20
    ltcf_staff_age_max = 60

    with_school_types = True
    average_class_size = 20
    inter_grade_mixing = 0.1
    average_student_teacher_ratio = 20
    average_teacher_teacher_degree = 3
    teacher_age_min = 25
    teacher_age_max = 75

    with_non_teaching_staff = True
    # if with_non_teaching_staff is False, but generate is True, then average_all_staff_ratio should be average_student_teacher_ratio or 0
    average_student_all_staff_ratio = 11
    average_additional_staff_degree = 20
    staff_age_min = 20
    staff_age_max = 75

    school_mixing_type = {'pk': 'age_clustered', 'es': 'age_clustered', 'ms': 'age_clustered', 'hs': 'random', 'uv': 'random'}

    popfile = f'inputs/kc_synthpops_clustered_withstaff_10e3.ppl'

    T = sc.tic()
    print(f'Making "{popfile}"...')
    sim = cv.Sim(pars)
    cv.make_people(sim,
                popfile=popfile,
                save_pop=True,
                generate=True,
                with_facilities=True, # dependent on "school_mixing_type" and "with_school_types"
                    use_two_group_reduction=use_two_group_reduction,
                    average_LTCF_degree=average_LTCF_degree,
                    ltcf_staff_age_min=ltcf_staff_age_min,
                    ltcf_staff_age_max=ltcf_staff_age_max,
                    with_school_types=with_school_types,
                    school_mixing_type=school_mixing_type,
                    average_class_size=average_class_size,
                    inter_grade_mixing=inter_grade_mixing,
                    average_student_teacher_ratio=average_student_teacher_ratio,
                    average_teacher_teacher_degree=average_teacher_teacher_degree,
                    teacher_age_min=teacher_age_min,
                    teacher_age_max=teacher_age_max,
                    with_non_teaching_staff=with_non_teaching_staff,
                    average_student_all_staff_ratio=average_student_all_staff_ratio,
                    average_additional_staff_degree=average_additional_staff_degree,
                    staff_age_min=staff_age_min,
                    staff_age_max=staff_age_max
                )
    sc.toc(T)

    print('Done')
    return

if __name__ == '__main__':
    unittest.main()