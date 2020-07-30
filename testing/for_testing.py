'''Show optimized runs'''

import covasim as cv
import sciris as sc
import pandas as pd
import synthpops as sp
sp.config.set_nbrackets(20) # Essential for getting the age distribution right

pop_size = 20e3 # Set population size

def make_population(seed=0, popfile=None):
    ''' Pre-generate the synthpops population '''

    pars = sc.objdict(
        pop_size = 10e3,
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

    school_mixing_type = {'pk': 'clustered', 'es': 'clustered', 'ms': 'clustered', 'hs': 'random', 'uv': 'random'}

    if popfile is None:
        popfile = f'inputs/kc_synthpops_clustered_withstaff_10e3.ppl'

    T = sc.tic()
    print(f'Making "{popfile}"...')
    sim = cv.Sim(pars)
    cv.make_people(sim,
                   popfile=popfile,
                   save_pop=True,
                   generate=True,
                   with_facilities=True,
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

    make_population()

    date = '2020-07-30'

    n_seeds = 1

    schools_reopening_scenarios = [
        # 'as_normal',
        'with_screening',
        # 'with_hybrid_scheduling',
        # 'ES_MS_inperson_HS_remote',
        # 'ES_inperson_MS_HS_remote',
        # 'all_remote',
    ]
    schools_reopening_scenarios_label = [
        # 'As Normal',
        'With Screening',
        # 'All Hybrid',
        # 'ES/MS in Person, HS Remote',
        # 'ES in Person, MS/HS Remote',
        # 'All Remote',
    ]
    test_prob = [
        # 0,
        .5,
        # .5,
        # .5,
        # .5,
        # 0,
    ]
    trace_prob = [
        # 0,
        .5,
        # .5,
        # .5,
        # .5,
        # 0,
    ]
    NPI = [
        # None,
        0.75,
        # 0.75,
        # 0.75,
        # 0.75,
        # None,
    ]
    intervention_start_day = [
        # None,
        {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
        # {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
        # {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': None, 'uv': None},
        # {'pk': None, 'es': '2020-09-01', 'ms': None, 'hs': None, 'uv': None},
        # None,
    ]
    schedule = [
        # None,
        None,
        # {'pk': None, 'es': True, 'ms': True, 'hs': True, 'uv': None},
        # None,
        # None,
        # None,
    ]
    day_schools_close = '2020-07-01'
    day_schools_open = [
        # {'pk': '2020-09-01', 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
        {'pk': '2020-09-01', 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
        # {'pk': '2020-09-01', 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
        # {'pk': '2020-09-01', 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': None, 'uv': None},
        # {'pk': '2020-09-01', 'es': '2020-09-01', 'ms': None, 'hs': None, 'uv': None},
        # None,
    ]
    tp = sc.objdict(
        symp_prob=0.12,
        asymp_prob=0.0015,
        symp_quar_prob=0.8,
        asymp_quar_prob=0.1,
        test_delay=2.0,
    )
    ct = sc.objdict(
        trace_probs=0.25,
        trace_time=3.0,
    )

    for i, scen in enumerate(schools_reopening_scenarios):
        analysis_name = f'{scen}'
        pars = {'pop_size': 10e3,
                'pop_scale': 10,
                'pop_type': 'synthpops',
                'pop_infected': 200,
                'rescale': True,
                'rescale_factor': 1.1,
                'verbose': 0.1,
                'start_day': '2020-07-01',
                'end_day': '2020-12-01',
                'rand_seed': 0,
                }
        popfile = f'inputs/kc_synthpops_clustered_withstaff_10e3.ppl'
        sim = cv.Sim(pars, popfile=popfile, load_pop=True, label=scen)
        day_schools_reopen = sim.day('2020-09-01')
        interventions = [
            cv.test_prob(start_day='2020-07-01', **tp),
            cv.contact_tracing(start_day='2020-07-01', **ct),
            cv.clip_edges(days='2020-08-01', changes=0.63, layers='w', label='close_work'),
            cv.clip_edges(days='2020-08-01', changes=0.63, layers='c', label='close_community'),
            cv.change_beta(days='2020-08-01', changes=0.75, layers='c', label='NPI_community'),
            cv.change_beta(days='2020-08-01', changes=0.75, layers='w', label='NPI_work'),
            cv.close_schools(
                day_schools_closed=day_schools_close,
                start_day=day_schools_open[i],
                label='close_schools'
            ),
            cv.reopen_schools(
                start_day=intervention_start_day[i],
                test=test_prob[i],
                trace=trace_prob[i],
                ili_prev=0,
                schedule=schedule[i],
                num_pos=None,
                label='reopen_schools'
            )
        ]

        if NPI[i] is not None:
            interventions += [
                cv.change_beta(days='2020-09-01', changes=NPI[i], layers='s', label='NPI_schools')]
        sim['interventions'] = interventions
        for interv in sim['interventions']:
            interv.do_plot = False

        ## if i want to infect students in a school:
        school_type_to_infect = 'es'
        school_id = sim.people.school_types[school_type_to_infect][0]
        inds_of_school = sim.people.schools[school_id]
        student_inds = [x for x in inds_of_school if sim.people.student_flag[x] is True]
        sim.people.infect(inds=student_inds, layer='seed_infection')
        sim.people.symptomatic[student_inds] = True

        sim.run()
        num_school_days_lost = sim.school_info['school_days_lost']
        num_student_school_days = sim.school_info['total_student_school_days']

