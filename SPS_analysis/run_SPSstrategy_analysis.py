'''Show optimized runs'''

# %Imports
import sciris as sc
from SPS_analysis import create_sim as cs
import covasim as cv
import numpy as np
from covasim import utils as cvu
import pandas as pd
import random

cv.check_save_version('1.5.0', die=True)


def school_dict(sim, school_dicts):
    school_results = dict()
    label = sim.base_sim.label
    school_results[label] = dict()
    if len(sim.sims) > 1:  # if running multiple seeds, print all of them
        school_results[label]['num_teachers'] = []
        school_results[label]['num_teachers_tested'] = []
        school_results[label]['num_teachers_test_pos'] = []
        school_results[label]['num_teachers_screen_pos'] = []
        school_results[label]['num_teacher_cases'] = []

        school_results[label]['num_staff'] = []
        school_results[label]['num_staff_tested'] = []
        school_results[label]['num_staff_test_pos'] = []
        school_results[label]['num_staff_screen_pos'] = []
        school_results[label]['num_staff_cases'] = []

        school_results[label]['num_students'] = []
        school_results[label]['num_students_tested'] = []
        school_results[label]['num_students_test_pos'] = []
        school_results[label]['num_students_screen_pos'] = []
        school_results[label]['num_student_cases'] = []

        school_results[label]['cum_infectious_staff'] = []
        school_results[label]['cum_infectious_students'] = []
        school_results[label]['cum_asymp_staff'] = []
        school_results[label]['cum_asymp_students'] = []

        for j, sub_sim in enumerate(sim.sims):
            school_results[label]['num_teachers_tested'].append(sub_sim.school_info['num_teachers_tested'])
            school_results[label]['num_teachers_test_pos'].append(sub_sim.school_info['num_teachers_test_pos'])
            school_results[label]['num_teachers_screen_pos'].append(sub_sim.school_info['num_teachers_screen_pos'])
            school_results[label]['num_teacher_cases'].append(sub_sim.school_info['num_teacher_cases'])
            school_results[label]['num_teachers'].append(sub_sim.school_info['num_teachers'])

            school_results[label]['num_staff_tested'].append(sub_sim.school_info['num_staff_tested'])
            school_results[label]['num_staff_test_pos'].append(sub_sim.school_info['num_staff_test_pos'])
            school_results[label]['num_staff_screen_pos'].append(sub_sim.school_info['num_staff_screen_pos'])
            school_results[label]['num_staff_cases'].append(sub_sim.school_info['num_staff_cases'])
            school_results[label]['num_staff'].append(sub_sim.school_info['num_staff'])

            school_results[label]['num_students_tested'].append(sub_sim.school_info['num_students_tested'])
            school_results[label]['num_students_test_pos'].append(sub_sim.school_info['num_students_test_pos'])
            school_results[label]['num_students_screen_pos'].append(sub_sim.school_info['num_students_screen_pos'])
            school_results[label]['num_student_cases'].append(sub_sim.school_info['num_student_cases'])
            school_results[label]['num_students'].append(sub_sim.school_info['num_students'])

            school_results[label]['cum_infectious_staff'].append(sum(sub_sim.school_info['num_staff_infectious']))
            school_results[label]['cum_infectious_students'].append(
                sum(sub_sim.school_info['num_students_infectious']))
            school_results[label]['cum_asymp_staff'].append(sum(sub_sim.school_info['num_staff_asymptomatic']))
            school_results[label]['cum_asymp_students'].append(
                sum(sub_sim.school_info['num_students_asymptomatic']))
    else:
        for sub_sim in sim.sims:
            school_results[label]['num_teachers_tested'] = sub_sim.school_info['num_teachers_tested']
            school_results[label]['num_teachers_test_pos'] = sub_sim.school_info['num_teachers_test_pos']
            school_results[label]['num_teachers_screen_pos'] = sub_sim.school_info['num_teachers_screen_pos']
            school_results[label]['num_teacher_cases'] = sub_sim.school_info['num_teacher_cases']
            school_results[label]['num_teachers'] = sub_sim.school_info['num_teachers']

            school_results[label]['num_staff_tested'] = sub_sim.school_info['num_staff_tested']
            school_results[label]['num_staff_test_pos'] = sub_sim.school_info['num_staff_test_pos']
            school_results[label]['num_staff_screen_pos'] = sub_sim.school_info['num_staff_screen_pos']
            school_results[label]['num_staff_cases'] = sub_sim.school_info['num_staff_cases']
            school_results[label]['num_staff'] = sub_sim.school_info['num_staff']

            school_results[label]['num_students_tested'] = sub_sim.school_info['num_students_tested']
            school_results[label]['num_students_test_pos'] = sub_sim.school_info['num_students_test_pos']
            school_results[label]['num_students_screen_pos'] = sub_sim.school_info['num_students_screen_pos']
            school_results[label]['num_student_cases'] = sub_sim.school_info['num_student_cases']
            school_results[label]['num_students'] = sub_sim.school_info['num_students']

            school_results[label]['cum_infectious_staff'] = sum(sub_sim.school_info['num_staff_infectious'])
            school_results[label]['cum_infectious_students'] = sum(sub_sim.school_info['num_students_infectious'])
            school_results[label]['cum_asymp_staff'] = sum(sub_sim.school_info['num_staff_asymptomatic'])
            school_results[label]['cum_asymp_students'] = sum(sub_sim.school_info['num_students_asymptomatic'])


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
                    mean = sum(value) / len(value)
                    results[key] = mean

    school_results = pd.DataFrame.from_dict(school_results)
    if index == 0:
        school_dicts[label] = dict()

    school_dicts[label] = school_results
    return school_results


def process_school_dicts(school_dicts, scenarios):
    df_list = []
    for scen in scenarios:
        df_list.append(school_dicts[scen])
    df_final = pd.concat(df_list, axis=1)
    df_final.columns = scenarios
    return df_final


if __name__ == "__main__":

    do_save = True
    n_params = 1
    n_seeds = 1
    date = '07182020'

    school_reopening_pars = {
        'NPI_schools': 0.75,
        'network_change': True,
        'school_start_day': '2020-09-01',
        'intervention_start_day': {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
        'ttq_scen': 'medium',
        'mobility_scens': '90_perc',
        'mobility_file': f'inputs/KC_weeklyinteractions_070120_90perc.csv'
    }

    teacher_testing_scens = {
        'no_teacher_testing': {
            'test_freq': None,
            'test_prob': 0,
            'trace_prob': 0,
        },
        'monthly_teacher_testing': {
            'test_freq': 28,
            'test_prob': 1,
            'trace_prob': 1,
        },
        'biweekly_teacher_testing': {
            'test_freq': 14,
            'test_prob': 1,
            'trace_prob': 1,
        },
        'weekly_teacher_testing': {
            'test_freq': 7,
            'test_prob': 1,
            'trace_prob': 1,
        },
        # 'daily_teacher_testing': {
        #     'test_freq': 1,
        #     'test_prob': 1,
        #     'trace_prob': 1,
        # },
    }

    indices = range(n_params)
    jsonfile = 'optimization_v12_safegraph_070120.json'
    json = sc.loadjson(jsonfile)

    school_dicts = dict()
    infectious_staff_by_scen = []
    infectious_students_by_scen = []
    asymptomatic_staff_by_scen = []
    asymptomatic_students_by_scen = []
    diagnosed_by_scen = []
    for scen, teacher_testing in teacher_testing_scens.items():
        analysis_name = f'teacher_testing_analysis_{scen}'
        all_sims = []
        for index in indices:
            entry = json[index]
            pars = entry['pars']
            pars['end_day'] = '2020-12-01'
            pars['rand_seed'] = int(entry['index'])
            all_sims.append(cs.create_sim(pars=pars, label=scen, school_reopening_pars=school_reopening_pars,
                                          teacher_test_scen=teacher_testing))
        msim = cv.MultiSim(sims=all_sims)
        msim.run(reseed=False, par_args={'maxload': 0.8}, noise=0.0, keep_people=False)
        msim.reduce()
        df = []
        infectious_staff = []
        infectious_students = []
        asymptomatic_staff = []
        asymptomatic_students = []
        diagnosed = []
        for j in range(len(msim.sims)):
            filename = f'results/{analysis_name}_param{j}_results.csv'
            results = pd.DataFrame(msim.sims[j].results)
            results.to_csv(filename, header=True)
            df.append(results)
            infectious_staff.append(pd.DataFrame(msim.sims[j].school_info['num_staff_infectious']))
            infectious_students.append(pd.DataFrame(msim.sims[j].school_info['num_students_infectious']))
            asymptomatic_staff.append(pd.DataFrame(msim.sims[j].school_info['num_staff_asymptomatic']))
            asymptomatic_students.append(pd.DataFrame(msim.sims[j].school_info['num_students_asymptomatic']))
            diagnosed.append(pd.DataFrame(msim.sims[j].school_info['num_diagnosed']))

        df_concat = pd.concat(df)
        by_row_index = df_concat.groupby(df_concat.index)
        df_means = by_row_index.mean()

        infectious_staff_concat = pd.concat(infectious_staff)
        by_row_index = infectious_staff_concat.groupby(infectious_staff_concat.index)
        infectious_staff_means = by_row_index.mean()
        infectious_staff_means.columns = [scen]
        infectious_staff_by_scen.append(infectious_staff_means)

        infectious_students_concat = pd.concat(infectious_students)
        by_row_index = infectious_students_concat.groupby(infectious_students_concat.index)
        infectious_students_means = by_row_index.mean()
        infectious_students_means.columns = [scen]
        infectious_students_by_scen.append(infectious_students_means)

        asymptomatic_staff_concat = pd.concat(asymptomatic_staff)
        by_row_index = asymptomatic_staff_concat.groupby(asymptomatic_staff_concat.index)
        asymptomatic_staff_means = by_row_index.mean()
        asymptomatic_staff_means.columns = [scen]
        asymptomatic_staff_by_scen.append(asymptomatic_staff_means)

        asymptomatic_students_concat = pd.concat(asymptomatic_students)
        by_row_index = asymptomatic_students_concat.groupby(asymptomatic_students_concat.index)
        asymptomatic_students_means = by_row_index.mean()
        asymptomatic_students_means.columns = [scen]
        asymptomatic_students_by_scen.append(asymptomatic_students_means)

        diagnosed_concat = pd.concat(diagnosed)
        by_row_index = diagnosed_concat.groupby(diagnosed_concat.index)
        diagnosed_means = by_row_index.mean()
        diagnosed_means.columns = [scen]
        diagnosed_by_scen.append(diagnosed_means)

        if do_save:
            filename = f'results/{analysis_name}_results.csv'
            df_means.to_csv(filename, header=True)
            school_results = school_dict(msim, school_dicts)

    infectious_staff_by_scen = pd.concat(infectious_staff_by_scen, ignore_index=True, axis=1)
    infectious_staff_by_scen.columns = teacher_testing_scens.keys()

    infectious_students_by_scen = pd.concat(infectious_students_by_scen, ignore_index=True, axis=1)
    infectious_students_by_scen.columns = teacher_testing_scens.keys()

    asymptomatic_staff_by_scen = pd.concat(asymptomatic_staff_by_scen, ignore_index=True, axis=1)
    asymptomatic_staff_by_scen.columns = teacher_testing_scens.keys()

    asymptomatic_students_by_scen = pd.concat(asymptomatic_students_by_scen, ignore_index=True, axis=1)
    asymptomatic_students_by_scen.columns = teacher_testing_scens.keys()

    diagnosed_by_scen = pd.concat(diagnosed_by_scen, ignore_index=True, axis=1)
    diagnosed_by_scen.columns = teacher_testing_scens.keys()

    # filename = f'results/teacher_testing_analysis_infectious_staff_{date}.csv'
    # infectious_staff_by_scen.to_csv(filename, header=True)
    #
    # filename = f'results/teacher_testing_analysis_infectious_students_{date}.csv'
    # infectious_students_by_scen.to_csv(filename, header=True)
    #
    # filename = f'results/teacher_testing_analysis_asymptomatic_staff_{date}.csv'
    # asymptomatic_staff_by_scen.to_csv(filename, header=True)
    #
    # filename = f'results/teacher_testing_analysis_asymptomatic_students_{date}.csv'
    # asymptomatic_students_by_scen.to_csv(filename, header=True)
    #
    # filename = f'results/teacher_testing_analysis_diagnosed_{date}.csv'
    # diagnosed_by_scen.to_csv(filename, header=True)

    final_results = process_school_dicts(school_dicts, teacher_testing_scens.keys())
    filename = f'results/teacher_testing_analysis_combined_output_{date}.csv'
    final_results.to_csv(filename, header=True)