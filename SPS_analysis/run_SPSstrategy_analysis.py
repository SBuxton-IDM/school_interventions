'''Show optimized runs'''

import sciris as sc
from SPS_analysis import create_sim as cs
import covasim as cv
import numpy as np
from covasim import utils as cvu
import pandas as pd

cv.check_save_version('1.4.7', die=True)


def process_schools(sub_sim):
    snapshot = sub_sim['analyzers'][1]
    school_snapshot_dict = dict()
    school_snapshot_dict['total_infectious'] = []
    school_snapshot_dict['students_infectious'] = []
    school_snapshot_dict['teachers_infectious'] = []
    school_snapshot_dict['total_cases_in_pk'] = []
    school_snapshot_dict['total_cases_in_es'] = []
    school_snapshot_dict['total_cases_in_ms'] = []
    school_snapshot_dict['total_cases_in_hs'] = []
    school_snapshot_dict['total_cases_in_uv'] = []
    school_snapshot_dict['total_pk_with_at_least_one_case'] = []
    school_snapshot_dict['total_es_with_at_least_one_case'] = []
    school_snapshot_dict['total_ms_with_at_least_one_case'] = []
    school_snapshot_dict['total_hs_with_at_least_one_case'] = []
    school_snapshot_dict['total_uv_with_at_least_one_case'] = []

    for date, shot in snapshot.snapshots.items():

        teacher_inds = np.array([i for i in range(len(shot.teacher_flag)) if shot.teacher_flag[i] == True])
        student_inds = np.array([i for i in range(len(shot.student_flag)) if shot.student_flag[i] == True])

        total = len(cvu.itrue(shot.infectious, shot.age))
        school_snapshot_dict['total_infectious'].append(total)
        teachers = len(cvu.itrue(shot.infectious[teacher_inds],teacher_inds))
        school_snapshot_dict['teachers_infectious'].append(teachers)
        students = len(cvu.itrue(shot.infectious[student_inds], student_inds))
        school_snapshot_dict['students_infectious'].append(students)

        for type, schools in shot.school_types.items():
            total_cases = 0
            total_schools = 0
            if type == 'pk':
                for school in schools:
                    cases_in_school = len(cvu.itrue(shot.infectious[shot.schools[school]], np.array(shot.schools[school])))
                    total_cases += cases_in_school
                    if cases_in_school >= 1:
                        total_schools += 1
                school_snapshot_dict['total_cases_in_pk'].append(total_cases)
                school_snapshot_dict['total_pk_with_at_least_one_case'].append(total_schools)
            elif type == 'es':
                for school in schools:
                    cases_in_school = len(cvu.itrue(shot.infectious[shot.schools[school]], np.array(shot.schools[school])))
                    total_cases += cases_in_school
                    if cases_in_school >= 1:
                        total_schools += 1
                school_snapshot_dict['total_cases_in_es'].append(total_cases)
                school_snapshot_dict['total_es_with_at_least_one_case'].append(total_schools)
            elif type == 'ms':
                for school in schools:
                    cases_in_school = len(cvu.itrue(shot.infectious[shot.schools[school]], np.array(shot.schools[school])))
                    total_cases += cases_in_school
                    if cases_in_school >= 1:
                        total_schools += 1
                school_snapshot_dict['total_cases_in_ms'].append(total_cases)
                school_snapshot_dict['total_ms_with_at_least_one_case'].append(total_schools)
            elif type == 'hs':
                for school in schools:
                    cases_in_school = len(cvu.itrue(shot.infectious[shot.schools[school]], np.array(shot.schools[school])))
                    total_cases += cases_in_school
                    if cases_in_school >= 1:
                        total_schools += 1
                school_snapshot_dict['total_cases_in_hs'].append(total_cases)
                school_snapshot_dict['total_hs_with_at_least_one_case'].append(total_schools)
            elif type == 'uv':
                for school in schools:
                    cases_in_school = len(cvu.itrue(shot.infectious[shot.schools[school]], np.array(shot.schools[school])))
                    total_cases += cases_in_school
                    if cases_in_school >= 1:
                        total_schools += 1
                school_snapshot_dict['total_cases_in_uv'].append(total_cases)
                school_snapshot_dict['total_uv_with_at_least_one_case'].append(total_schools)


    return school_snapshot_dict


def school_dict(msims):
    school_results = dict()
    for i, sim in enumerate(msims):
        school_results[teacher_testing_scens[i]] = dict()
        if len(sim.sims) > 1:  # if running multiple param sets, print all of them
            school_results[teacher_testing_scens[i]]['school_closures'] = []
            school_results[teacher_testing_scens[i]]['cum_infections'] = []
            school_results[teacher_testing_scens[i]]['num_tested'] = []
            school_results[teacher_testing_scens[i]]['num_traced'] = []
            school_results[teacher_testing_scens[i]]['test_pos'] = []
            school_results[teacher_testing_scens[i]]['school_days_lost'] = []
            school_results[teacher_testing_scens[i]]['num_students'] = []
            school_results[teacher_testing_scens[i]]['total_cases'] = []
            school_results[teacher_testing_scens[i]]['student_cases'] = []
            school_results[teacher_testing_scens[i]]['teacher_cases'] = []
            school_results[teacher_testing_scens[i]]['cases_in_pk'] = []
            school_results[teacher_testing_scens[i]]['cases_in_es'] = []
            school_results[teacher_testing_scens[i]]['cases_in_ms'] = []
            school_results[teacher_testing_scens[i]]['cases_in_hs'] = []
            school_results[teacher_testing_scens[i]]['cases_in_uv'] = []
            school_results[teacher_testing_scens[i]]['pk_with_a_case'] = []
            school_results[teacher_testing_scens[i]]['es_with_a_case'] = []
            school_results[teacher_testing_scens[i]]['ms_with_a_case'] = []
            school_results[teacher_testing_scens[i]]['hs_with_a_case'] = []
            school_results[teacher_testing_scens[i]]['uv_with_a_case'] = []
            for j, sub_sim in enumerate(sim.sims):
                school_snapshot_dict = process_schools(sub_sim)
                school_results[teacher_testing_scens[i]]['total_cases'].append(
                    school_snapshot_dict['total_infectious'])
                school_results[teacher_testing_scens[i]]['teacher_cases'].append(
                    school_snapshot_dict['teachers_infectious'])
                school_results[teacher_testing_scens[i]]['student_cases'].append(
                    school_snapshot_dict['students_infectious'])
                school_results[teacher_testing_scens[i]]['cases_in_pk'].append(
                    school_snapshot_dict['total_cases_in_pk'])
                school_results[teacher_testing_scens[i]]['cases_in_es'].append(
                    school_snapshot_dict['total_cases_in_es'])
                school_results[teacher_testing_scens[i]]['cases_in_ms'].append(
                    school_snapshot_dict['total_cases_in_ms'])
                school_results[teacher_testing_scens[i]]['cases_in_hs'].append(
                    school_snapshot_dict['total_cases_in_hs'])
                school_results[teacher_testing_scens[i]]['cases_in_uv'].append(
                    school_snapshot_dict['total_cases_in_uv'])
                school_results[teacher_testing_scens[i]]['pk_with_a_case'].append(
                    school_snapshot_dict['total_pk_with_at_least_one_case'])
                school_results[teacher_testing_scens[i]]['es_with_a_case'].append(
                    school_snapshot_dict['total_es_with_at_least_one_case'])
                school_results[teacher_testing_scens[i]]['ms_with_a_case'].append(
                    school_snapshot_dict['total_ms_with_at_least_one_case'])
                school_results[teacher_testing_scens[i]]['hs_with_a_case'].append(
                    school_snapshot_dict['total_hs_with_at_least_one_case'])
                school_results[teacher_testing_scens[i]]['uv_with_a_case'].append(
                    school_snapshot_dict['total_uv_with_at_least_one_case'])
                school_results[teacher_testing_scens[i]]['num_students'].append(
                    sub_sim.school_info['num_students'])
                school_results[teacher_testing_scens[i]]['school_closures'].append(
                    sub_sim.school_info['school_closures'])
                school_results[teacher_testing_scens[i]]['school_days_lost'].append(
                    sub_sim.school_info['school_days_lost'])
                school_results[teacher_testing_scens[i]]['cum_infections'].append(
                    sub_sim.summary['cum_infections'])
                school_results[teacher_testing_scens[i]]['num_tested'].append(
                    sub_sim.school_info['num_tested'])
                school_results[teacher_testing_scens[i]]['num_traced'].append(
                    sub_sim.school_info['num_traced'])
                school_results[teacher_testing_scens[i]]['test_pos'].append(
                    sub_sim.school_info['test_pos'])

        else:
            for sub_sim in sim.sims:
                school_snapshot_dict = process_schools(sub_sim)
                school_results[teacher_testing_scens[i]]['total_cases'] = school_snapshot_dict['total_infectious']
                school_results[teacher_testing_scens[i]]['teacher_cases'] = school_snapshot_dict[
                    'teachers_infectious']
                school_results[teacher_testing_scens[i]]['student_cases'] = school_snapshot_dict[
                    'students_infectious']
                school_results[teacher_testing_scens[i]]['cases_in_pk'] = school_snapshot_dict[
                    'total_cases_in_pk']
                school_results[teacher_testing_scens[i]]['cases_in_es'] = school_snapshot_dict['total_cases_in_es']
                school_results[teacher_testing_scens[i]]['cases_in_ms'] = school_snapshot_dict['total_cases_in_ms']
                school_results[teacher_testing_scens[i]]['cases_in_hs'] = school_snapshot_dict['total_cases_in_hs']
                school_results[teacher_testing_scens[i]]['cases_in_uv'] = school_snapshot_dict[
                    'total_cases_in_uv']
                school_results[teacher_testing_scens[i]]['pk_with_a_case'] = school_snapshot_dict[
                    'total_pk_with_at_least_one_case']
                school_results[teacher_testing_scens[i]]['es_with_a_case'] = school_snapshot_dict[
                    'total_es_with_at_least_one_case']
                school_results[teacher_testing_scens[i]]['ms_with_a_case'] = school_snapshot_dict[
                    'total_ms_with_at_least_one_case']
                school_results[teacher_testing_scens[i]]['hs_with_a_case'] = school_snapshot_dict[
                    'total_hs_with_at_least_one_case']
                school_results[teacher_testing_scens[i]]['uv_with_a_case'] = school_snapshot_dict[
                    'total_uv_with_at_least_one_case']
                school_results[teacher_testing_scens[i]]['num_students'] = sub_sim.school_info[
                    'num_students']
                school_results[teacher_testing_scens[i]]['school_closures'] = sub_sim.school_info[
                    'school_closures']
                school_results[teacher_testing_scens[i]]['school_days_lost'] = sub_sim.school_info[
                    'school_days_lost']
                school_results[teacher_testing_scens[i]]['cum_infections'] = sub_sim.summary[
                    'cum_infections']
                school_results[teacher_testing_scens[i]]['num_tested'] = sub_sim.school_info['num_tested']
                school_results[teacher_testing_scens[i]]['num_traced'] = sub_sim.school_info['num_traced']
                school_results[teacher_testing_scens[i]]['test_pos'] = sub_sim.school_info['test_pos']

    for _, results in school_results.items():
        for key, value in results.items():
            if isinstance(value, list):
                if isinstance(value[0], list):
                    total = [sum(x) for x in zip(*value)]
                    num_sublists = len(value)
                    for ind, value in enumerate(total):
                        total[ind] = value / num_sublists
                    results[key] = total
                else:
                    mean = sum(value)/len(value)
                    results[key] = mean

    school_results = pd.DataFrame.from_dict(school_results)

    return school_results


if __name__ == "__main__":

    do_save = True
    n_params = 5
    n_seeds = 5
    date = '07022020'


    school_reopening_pars = {
                        'test_prob': 0.5,
                        'trace_prob': 0.25,
                        'NPI_schools': 0.75,
                        'test_freq': None,
                        'network_change': True,
                        'school_start_day': '2020-09-01',
                        'intervention_start_day': {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
                        'ttq_scen': 'medium',
                        'mobility_scens': '80_perc',
                        'mobility_file': f'inputs/KC_weeklyinteractions_20200616_80_perc.csv'
                        }

    teacher_testing_scens = {
                        'no_teacher_testing': {'test_freq': None},
                        'weekly_teacher_testing': {'test_freq': 7},
                        'biweekly_teacher_testing': {'test_freq': 14},
                        'monthly_teacher_testing': {'test_freq': 30},
                        }

    indices = range(n_params)
    seeds = range(n_seeds)
    jsonfile = 'optimization_v12_safegraph_070120.json'
    json = sc.loadjson(jsonfile)

    for scen, teacher_testing in teacher_testing_scens.items():
        analysis_name = f'teacher_testing_analysis_{scen}'
        msims = []
        for index in indices:
            all_sims = []
            entry = json[index]
            pars = entry['pars']
            pars['end_day'] = '2020-12-01'
            for seed in seeds:
                pars['rand_seed'] = seed
                all_sims.append(cs.create_sim(pars=pars, label=scen, school_reopening_pars=school_reopening_pars,
                                              teacher_test_scen=teacher_testing))

            msim = cv.MultiSim(sims=all_sims)
            msim.run(reseed=False, par_args={'maxload': 0.8}, noise=0.0, keep_people=False)
            msim.reduce()
            df = []
            for j in range(len(msim.sims)):
                df.append(pd.DataFrame(msim.sims[j].results))
            df_concat = pd.concat(df)
            by_row_index = df_concat.groupby(df_concat.index)
            df_means = by_row_index.mean()
            msims.append(msim)

            if do_save:
                filename = f'results/{analysis_name}_param{index}_results.csv'
                df_means.to_csv(filename, header=True)
                school_results = school_dict(msims)
                filename = f'results/{analysis_name}_param{index}_output.csv'
                school_results.to_csv(filename, header=True)