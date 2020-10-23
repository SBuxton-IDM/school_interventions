'''
Generate a SynthPops population for use with the schools code.
'''

import os
import numpy as np
import sciris as sc
import covasim as cv
import synthpops as sp

def make_population(pop_size, rand_seed=1, do_save=True, popfile=None, cohorting=True, n_brackets=20, community_contacts=20,**kwargs):
    '''
    Generate the synthpops population.

    Args:
        pop_size (int): number of people in the model
        rand_seed (int): random seed to use for generating the population
        do_save (bool): whether to save the population
        popfile (str): if so, where to save it to
        cohorting (bool): whether to use cohorting
        n_brackets (int): whether to use 16- or 20-bracket age bins
        community_contacts (int): how many community contacts there are
        kwargs (dict): passed to sp.make_population()
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

    pars.update(kwargs) # Update any parameters

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
        popfile = os.path.join('inputs', f'kc_{strategy}_{int(pars.n)}_seed{pars.rand_seed}.ppl')

    T = sc.tic()
    print(f'Making "{popfile}"...')

    # Make the population
    population = sp.make_population(**pars)

    # Convert to a popdict
    popdict = cv.make_synthpop(population=population, community_contacts=community_contacts)
    school_ids = [None] * int(pop_size)
    teacher_flag = [False] * int(pop_size)
    staff_flag = [False] * int(pop_size)
    student_flag = [False] * int(pop_size)
    school_types = {'pk': [], 'es': [], 'ms': [], 'hs': [], 'uv': []}
    school_type_by_person = [None] * int(pop_size)
    schools = dict()

    for uid,person in population.items():
        if person['scid'] is not None:
            school_ids[uid] = person['scid']
            school_type_by_person[uid] = person['sc_type']
            if person['scid'] not in school_types[person['sc_type']]:
                school_types[person['sc_type']].append(person['scid'])
            if person['scid'] in schools:
                schools[person['scid']].append(uid)
            else:
                schools[person['scid']] = [uid]
            if person['sc_teacher'] is not None:
                teacher_flag[uid] = True
            elif person['sc_student'] is not None:
                student_flag[uid] = True
            elif person['sc_staff'] is not None:
                staff_flag[uid] = True

    popdict['school_id'] = np.array(school_ids)
    popdict['schools'] = schools
    popdict['teacher_flag'] = teacher_flag
    popdict['student_flag'] = student_flag
    popdict['staff_flag'] = staff_flag
    popdict['school_types'] = school_types
    popdict['school_type_by_person'] = school_type_by_person

    # Actually create the people
    people_pars = dict(
        pop_size = pars.n,
        beta_layer = {k:1.0 for k in 'hswcl'} # Since this is used to define hat layers exist
    )
    people = cv.People(people_pars, strict=False, uid=popdict['uid'], age=popdict['age'], sex=popdict['sex'],
                          contacts=popdict['contacts'], school_id=popdict['school_id'],
                          schools=popdict['schools'], school_types=popdict['school_types'],
                          student_flag=popdict['student_flag'], teacher_flag=popdict['teacher_flag'],
                          staff_flag=popdict['staff_flag'], school_type_by_person=popdict['school_type_by_person'])

    if do_save:
        sc.saveobj(popfile, people)

    sc.toc(T)

    print('Done')
    return people