'''
Generate a SynthPops population for use with the schools code.
'''

import sciris as sc
import covasim as cv
import synthpops as sp

def make_population(pop_size, rand_seed=0, do_save=True, popfile=None, cohorting=True, n_brackets=20, **kwargs):
    '''
    Generate the synthpops population.


    '''

    sp.set_nbrackets(n_brackets) # Essential for getting the age distribution right

    pars = sc.objdict(
        n = pop_size,
        rand_seed = rand_seed,

        with_facilities=True,
        use_two_group_reduction = True,
        average_LTCF_degree = 20,
        ltcf_staff_age_min = 20,
        ltcf_staff_age_max = 60,

        with_school_types = True,
        average_class_size = 20,
        inter_grade_mixing = 0.1,
        average_student_teacher_ratio = 20,
        average_teacher_teacher_degree = 3,
        teacher_age_min = 25,
        teacher_age_max = 75,

        with_non_teaching_staff = True,
        # if with_non_teaching_staff is False, but generate is True, then ,average_all_staff_ratio should be average_student_teacher_ratio or 0
        average_student_all_staff_ratio = 11,
        average_additional_staff_degree = 20,
        staff_age_min = 20,
        staff_age_max = 75,
    )

    # For reference re: school_types
    # school_mixing_type = 'random' means that students in the school have edges randomly chosen from other students, teachers, and non teaching staff across the school. Students, teachers, and non teaching staff are treated the same in terms of edge generation.
    # school_mixing_type = 'age_clustered' means that students in the school have edges mostly within their own age/grade, with teachers, and non teaching staff. Strict classrooms are not generated. Teachers have some additional edges with other teachers.
    # school_mixing_type = 'age_and_class_clustered' means that students are cohorted into classes of students of the same age/grade with at least 1 teacher, and then some have contact with non teaching staff. Teachers have some additional edges with other teachers.

    if cohorting:
        strategy = 'clustered'  # students in pre-k, elementary, and middle school are cohorted into strict classrooms
        pars.school_mixing_type = {'pk': 'age_and_class_clustered', 'es': 'age_and_class_clustered', 'ms': 'age_and_class_clustered',
                              'hs': 'random', 'uv': 'random'}
    else:
        strategy = 'normal'
        pars.school_mixing_type = {'pk': 'age_clustered', 'es': 'age_clustered', 'ms': 'age_clustered',
                              'hs': 'random', 'uv': 'random'}

    if popfile is None:
        popfile = f'inputs/kc_{strategy}_{int(pars.n)}_seed{pars.rand_seed}.ppl'

    T = sc.tic()
    print(f'Making "{popfile}"...')

    spop = sp.make_population(**pars)

    sc.toc(T)

    print('Done')
    return spop