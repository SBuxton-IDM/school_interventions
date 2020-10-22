import covasim as cv
import sciris as sc

popfile = f'kc_synthpops_clustered_withstaff_10e3.ppl'

def make_pop(seed=0):
    ''' Pre-generate the synthpops population '''

    pars = sc.objdict(
        # pop_size = 2.25e6,
        pop_size = 11e3, #2.25e5,
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

    # For reference re: school_types
    # school_mixing_type = 'random' means that students in the school have edges randomly chosen from other students, teachers, and non teaching staff across the school. Students, teachers, and non teaching staff are treated the same in terms of edge generation.
    # school_mixing_type = 'age_clustered' means that students in the school have edges mostly within their own age/grade, with teachers, and non teaching staff. Strict classrooms are not generated. Teachers have some additional edges with other teachers.
    # school_mixing_type = 'age_and_class_clustered' means that students are cohorted into classes of students of the same age/grade with at least 1 teacher, and then some have contact with non teaching staff. Teachers have some additional edges with other teachers.

    cohorting = True
    if cohorting:
        strategy = 'clustered'  # students in pre-k, elementary, and middle school are cohorted into strict classrooms
        school_mixing_type = {'pk': 'age_and_class_clustered', 'es': 'age_and_class_clustered', 'ms': 'age_and_class_clustered',
                              'hs': 'random', 'uv': 'random'}
    else:
        strategy = 'normal'
        school_mixing_type = {'pk': 'age_clustered', 'es': 'age_clustered', 'ms': 'age_clustered',
                              'hs': 'random', 'uv': 'random'}


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
                   staff_age_max=staff_age_max,
                   layer_mapping={'LTCF':'l'},
                   )
    sc.toc(T)

    print('Done')
    return


make_pop()

pars = {'pop_size': 11e3,
        'pop_scale': 1,
        'pop_type': 'synthpops',
        'pop_infected': 100,
        'rescale': True,
        'rescale_factor': 1.1,
        'verbose': 0.1,
        'start_day': '2020-07-01',
        'end_day': '2020-12-01',
        'rand_seed': 3,
        }

days = dict(h=40,s=40,w=40, c=40, l=40)
interventions = []
for key,day in days.items():
        interventions.append(cv.change_beta(days=day, changes=0.0, layers=key))

sim = cv.Sim(pars, popfile=popfile, load_pop=True, label="No transmission")
sim['interventions'] = interventions


sim.run()
print(sim.results['new_infections'])