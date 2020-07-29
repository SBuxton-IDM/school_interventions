'''
Pre-generate the synthpops population including school types. Takes ~102s per seed
'''

import psutil
import sciris  as sc
import covasim as cv
import synthpops as sp
sp.config.set_nbrackets(20) # Essential for getting the age distribution right

def cache_populations(seed=0, popfile=None):
    ''' Pre-generate the synthpops population '''

    pars = sc.objdict(
        pop_size = 2.25e6,
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

    cohorting = True
    if cohorting:
        strategy = 'clustered'
        school_mixing_type = {'pk': 'clustered', 'es': 'clustered', 'ms': 'clustered', 'hs': 'random', 'uv': 'random'}
    else:
        strategy = 'normal'
        school_mixing_type = {'pk': 'age_and_class_clustered', 'es': 'age_and_class_clustered', 'ms': 'age_and_class_clustered',
                              'hs': 'random', 'uv': 'random'}

    if popfile is None:
        popfile = f'inputs/kc_synthpops_{strategy}_withstaff_1m_seed{pars.rand_seed}.ppl'

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

    seeds = [0,1,2,3,4]
    parallelize = True

    if parallelize:
        ram = psutil.virtual_memory().available/1e9
        required = 80*len(seeds) # 8 GB per 225e3 people
        if required < ram:
            print(f'You have {ram} GB of RAM, and this is estimated to require {required} GB: you should be fine')
        else:
            print(f'You have {ram:0.2f} GB of RAM, but this is estimated to require {required} GB -- you are in trouble!!!!!!!!!')
        sc.parallelize(cache_populations, iterarg=seeds) # Run them in parallel
    else:
        for seed in seeds:
            cache_populations(seed)