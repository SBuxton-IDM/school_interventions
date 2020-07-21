'''Show optimized runs'''

import sciris as sc
from reopening_scenarios import create_sim as cs
import covasim as cv
import numpy as np
from covasim import utils as cvu
import pandas as pd

cv.check_save_version('1.5.0', die=True)


def school_dict(msims):

    school_results = dict()
    for i, sim in enumerate(msims):
        school_results[schools_closure_scenarios[i]] = dict()
        if len(sim.sims) > 1:  # if running multiple param sets, print all of them
            school_results[schools_closure_scenarios[i]]['school_closures'] = []
            school_results[schools_closure_scenarios[i]]['cum_infections'] = []
            school_results[schools_closure_scenarios[i]]['num_tested'] = []
            school_results[schools_closure_scenarios[i]]['num_traced'] = []
            school_results[schools_closure_scenarios[i]]['test_pos'] = []
            school_results[schools_closure_scenarios[i]]['school_days_lost'] = []
            school_results[schools_closure_scenarios[i]]['student_school_days'] = []
            school_results[schools_closure_scenarios[i]]['perc_school_days_lost'] = []
            school_results[schools_closure_scenarios[i]]['num_teachers'] = []
            school_results[schools_closure_scenarios[i]]['num_teachers_tested'] = []
            school_results[schools_closure_scenarios[i]]['num_teachers_test_pos'] = []
            school_results[schools_closure_scenarios[i]]['num_teachers_screen_pos'] = []
            school_results[schools_closure_scenarios[i]]['num_teacher_cases'] = []

            school_results[schools_closure_scenarios[i]]['num_staff'] = []
            school_results[schools_closure_scenarios[i]]['num_staff_tested'] = []
            school_results[schools_closure_scenarios[i]]['num_staff_test_pos'] = []
            school_results[schools_closure_scenarios[i]]['num_staff_screen_pos'] = []
            school_results[schools_closure_scenarios[i]]['num_staff_cases'] = []

            school_results[schools_closure_scenarios[i]]['num_students'] = []
            school_results[schools_closure_scenarios[i]]['num_students_tested'] = []
            school_results[schools_closure_scenarios[i]]['num_students_test_pos'] = []
            school_results[schools_closure_scenarios[i]]['num_students_screen_pos'] = []
            school_results[schools_closure_scenarios[i]]['num_student_cases'] = []

            school_results[schools_closure_scenarios[i]]['cum_infectious_staff'] = []
            school_results[schools_closure_scenarios[i]]['cum_infectious_students'] = []
            school_results[schools_closure_scenarios[i]]['cum_asymp_staff'] = []
            school_results[schools_closure_scenarios[i]]['cum_asymp_students'] = []
            for j, sub_sim in enumerate(sim.sims):
                
                school_results[schools_closure_scenarios[i]]['num_students'].append(
                    sub_sim.school_info['num_students'])
                school_results[schools_closure_scenarios[i]]['school_closures'].append(
                    sub_sim.school_info['school_closures'])
                school_results[schools_closure_scenarios[i]]['school_days_lost'].append(
                    sub_sim.school_info['school_days_lost'])
                school_results[schools_closure_scenarios[i]]['student_school_days'].append(
                    sub_sim.school_info['total_student_school_days'])
                school_results[schools_closure_scenarios[i]]['perc_school_days_lost'].append(
                    sub_sim.school_info['school_days_lost']/sub_sim.school_info['total_student_school_days'])
                school_results[schools_closure_scenarios[i]]['cum_infections'].append(
                    sub_sim.summary['cum_infections'] - sub_sim.results['cum_infections'].values[218])
                school_results[schools_closure_scenarios[i]]['num_tested'].append(
                    sub_sim.school_info['num_tested'])
                school_results[schools_closure_scenarios[i]]['num_traced'].append(
                    sub_sim.school_info['num_traced'])
                school_results[schools_closure_scenarios[i]]['test_pos'].append(
                    sub_sim.school_info['test_pos'])
                school_results[schools_closure_scenarios[i]]['num_teachers_tested'].append(sub_sim.school_info['num_teachers_tested'])
                school_results[schools_closure_scenarios[i]]['num_teachers_test_pos'].append(sub_sim.school_info['num_teachers_test_pos'])
                school_results[schools_closure_scenarios[i]]['num_teachers_screen_pos'].append(sub_sim.school_info['num_teachers_screen_pos'])
                school_results[schools_closure_scenarios[i]]['num_teacher_cases'].append(sub_sim.school_info['num_teacher_cases'])
                school_results[schools_closure_scenarios[i]]['num_teachers'].append(sub_sim.school_info['num_teachers'])

                school_results[schools_closure_scenarios[i]]['num_staff_tested'].append(sub_sim.school_info['num_staff_tested'])
                school_results[schools_closure_scenarios[i]]['num_staff_test_pos'].append(sub_sim.school_info['num_staff_test_pos'])
                school_results[schools_closure_scenarios[i]]['num_staff_screen_pos'].append(sub_sim.school_info['num_staff_screen_pos'])
                school_results[schools_closure_scenarios[i]]['num_staff_cases'].append(sub_sim.school_info['num_staff_cases'])
                school_results[schools_closure_scenarios[i]]['num_staff'].append(sub_sim.school_info['num_staff'])

                school_results[schools_closure_scenarios[i]]['num_students_tested'].append(sub_sim.school_info['num_students_tested'])
                school_results[schools_closure_scenarios[i]]['num_students_test_pos'].append(sub_sim.school_info['num_students_test_pos'])
                school_results[schools_closure_scenarios[i]]['num_students_screen_pos'].append(sub_sim.school_info['num_students_screen_pos'])
                school_results[schools_closure_scenarios[i]]['num_student_cases'].append(sub_sim.school_info['num_student_cases'])
                school_results[schools_closure_scenarios[i]]['num_students'].append(sub_sim.school_info['num_students'])

                school_results[schools_closure_scenarios[i]]['cum_infectious_staff'].append(sum(sub_sim.school_info['num_staff_infectious']))
                school_results[schools_closure_scenarios[i]]['cum_infectious_students'].append(
                    sum(sub_sim.school_info['num_students_infectious']))
                school_results[schools_closure_scenarios[i]]['cum_asymp_staff'].append(sum(sub_sim.school_info['num_staff_asymptomatic']))
                school_results[schools_closure_scenarios[i]]['cum_asymp_students'].append(
                    sum(sub_sim.school_info['num_students_asymptomatic']))

        else:
            for sub_sim in sim.sims:
                school_results[schools_closure_scenarios[i]]['num_teachers_tested'] = sub_sim.school_info['num_teachers_tested']
                school_results[schools_closure_scenarios[i]]['num_teachers_test_pos'] = sub_sim.school_info['num_teachers_test_pos']
                school_results[schools_closure_scenarios[i]]['num_teachers_screen_pos'] = sub_sim.school_info['num_teachers_screen_pos']
                school_results[schools_closure_scenarios[i]]['num_teacher_cases'] = sub_sim.school_info['num_teacher_cases']
                school_results[schools_closure_scenarios[i]]['num_teachers'] = sub_sim.school_info['num_teachers']

                school_results[schools_closure_scenarios[i]]['num_staff_tested'] = sub_sim.school_info['num_staff_tested']
                school_results[schools_closure_scenarios[i]]['num_staff_test_pos'] = sub_sim.school_info['num_staff_test_pos']
                school_results[schools_closure_scenarios[i]]['num_staff_screen_pos'] = sub_sim.school_info['num_staff_screen_pos']
                school_results[schools_closure_scenarios[i]]['num_staff_cases'] = sub_sim.school_info['num_staff_cases']
                school_results[schools_closure_scenarios[i]]['num_staff'] = sub_sim.school_info['num_staff']

                school_results[schools_closure_scenarios[i]]['num_students_tested'] = sub_sim.school_info['num_students_tested']
                school_results[schools_closure_scenarios[i]]['num_students_test_pos'] = sub_sim.school_info['num_students_test_pos']
                school_results[schools_closure_scenarios[i]]['num_students_screen_pos'] = sub_sim.school_info['num_students_screen_pos']
                school_results[schools_closure_scenarios[i]]['num_student_cases'] = sub_sim.school_info['num_student_cases']
                school_results[schools_closure_scenarios[i]]['num_students'] = sub_sim.school_info['num_students']

                school_results[schools_closure_scenarios[i]]['cum_infectious_staff'] = sum(sub_sim.school_info['num_staff_infectious'])
                school_results[schools_closure_scenarios[i]]['cum_infectious_students'] = sum(sub_sim.school_info['num_students_infectious'])
                school_results[schools_closure_scenarios[i]]['cum_asymp_staff'] = sum(sub_sim.school_info['num_staff_asymptomatic'])
                school_results[schools_closure_scenarios[i]]['cum_asymp_students'] = sum(sub_sim.school_info['num_students_asymptomatic'])

                school_results[schools_closure_scenarios[i]]['num_students'] = sub_sim.school_info[
                    'num_students']
                school_results[schools_closure_scenarios[i]]['school_closures'] = sub_sim.school_info[
                    'school_closures']
                school_results[schools_closure_scenarios[i]]['school_days_lost'] = sub_sim.school_info[
                    'school_days_lost']
                school_results[schools_closure_scenarios[i]]['student_school_days'] = sub_sim.school_info[
                    'total_student_school_days']
                school_results[schools_closure_scenarios[i]]['perc_school_days_lost'] = sub_sim.school_info[
                    'school_days_lost'] / sub_sim.school_info['total_student_school_days']
                school_results[schools_closure_scenarios[i]]['cum_infections'] = sub_sim.summary[
                    'cum_infections'] - sub_sim.results['cum_infections'].values[218]
                school_results[schools_closure_scenarios[i]]['num_tested'] = sub_sim.school_info['num_tested']
                school_results[schools_closure_scenarios[i]]['num_traced'] = sub_sim.school_info['num_traced']
                school_results[schools_closure_scenarios[i]]['test_pos'] = sub_sim.school_info['test_pos']

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

    n_params = 15
    date = '07212020'

    # ttq_scen = ['lower', 'medium', 'upper']
    #
    # mobility_scens = ['70perc', '80perc', '90perc', '100perc']
    #
    # schools_closure_scenarios = ['no_school', 'as_normal', 'with_NPI', 'with_cohorting', 'with_screening_notesting',
    #                              'with_25perctest_100tracing', 'with_50perctest_100tracing',
    #                              'with_100perctest_100tracing']
    #
    # schools_closure_scenarios_label = ['No School', 'School as Normal', 'School with NPI', 'School with NPI + Cohorting',
    #                                    'School with NPI, Cohorting, Screening',
    #                                    'School with NPI, Cohorting, Screening, 25% Follow-Up Testing, 100% Follow-Up Tracing',
    #                                    'School with NPI, Cohorting, Screening, 50% Follow-Up Testing, 100% Follow-Up Tracing',
    #                                    'School with NPI, Cohorting, Screening, 100% Follow-Up Testing, 100% Follow-Up Tracing']
    #
    # test_prob = [0, 0, 0, 0, 0, .25, .5, 1]
    # trace_prob = [0, 0, 0, 0, 0, 1, 1, 1]
    # NPI_schools = [None, None, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75]
    # test_freq = None
    # network_change = [False, False, False, True, True, True, True, True]
    # intervention_start_day = [None, None, None, None,
    #                           {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
    #                           {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
    #                           {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
    #                           {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None}
    #                           ]
    # school_start_day = [{'pk': None, 'es': None, 'ms': None, 'hs': None, 'uv': None}, '2020-09-01',
    #                     '2020-09-01', '2020-09-01', '2020-09-01', '2020-09-01', '2020-09-01', '2020-09-01']

    # school_start_day = [{'pk': None, 'es': None, 'ms': None, 'hs': None, 'uv': None},
    #                     {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
    #                     {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
    #                     {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
    #                     {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
    #                     {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
    #                     {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
    #                     {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},]

    ttq_scen = 'medium'

    mobility = ['70perc', '80perc', '90perc']

    schools_closure_scenarios = ['no_school', 'with_screening_notesting', 'with_25perctest_100tracing',
                                 'with_hybrid_scheduling']

    schools_closure_scenarios_label = ['No School', 'School with NPI, Cohorting, Screening',
                                       'School with NPI, Cohorting, Screening, 25% Follow-Up Testing, 100% Follow-Up Tracing',
        'Hybrid School Scheduling with NPI, Cohorting, Screening, 25% Follow-Up Testing, 100% Follow-Up Tracing']

    test_prob = [0, 0, .25, .25]
    trace_prob = [0, 0, 1, 1]
    NPI_schools = [None, 0.75, 0.75, 0.75]
    test_freq = None
    network_change = [False, True, True, True]
    intervention_start_day = [None, {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
                              {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
                              {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None}
                              ]
    school_start_day = [None, '2020-09-01', '2020-09-01', '2020-09-01']

    school_start_day = [None, {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
                        {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
                        {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None}]

    schedule = [None, None, None,
                {'pk': None, 'es': True, 'ms': True, 'hs': True, 'uv': None}]

    indices = range(n_params)
    jsonfile = 'optimization_v12_safegraph_070120.json'
    json = sc.loadjson(jsonfile)


    for scen in mobility:
        msims = []
        mobility_file = f'inputs/KC_weeklyinteractions_070120_{scen}.csv'
        for i, changes in enumerate(schools_closure_scenarios_label):
            analysis_name = f'{changes}_{scen}_mobility_{ttq_scen}'
            all_sims = []
            for index in indices:
                entry = json[index]
                pars = entry['pars']
                pars['end_day'] = '2020-10-01'
                pars['rand_seed'] = int(entry['index'])
                all_sims.append(cs.create_sim(pars=pars, test_prob=test_prob[i],
                                              trace_prob=trace_prob[i], NPI_schools=NPI_schools[i],
                                              label=changes, test_freq=test_freq, schedule=schedule[i],
                                              network_change=network_change[i],
                                              school_start_day=school_start_day[i],
                                              intervention_start_day=intervention_start_day[i],
                                              mobility_file=mobility_file, ttq_scen=ttq_scen))

            msim = cv.MultiSim(sims=all_sims)
            msim.run(reseed=False, par_args={'maxload': 0.8}, noise=0.0, keep_people=False)
            msim.reduce()
            msims.append(msim)
            df = []
            for j in range(len(msim.sims)):
                filename = f'results/{analysis_name}_param{j}_results_{date}.csv'
                results = pd.DataFrame(msim.sims[j].results)
                results.to_csv(filename, header=True)
                df.append(results)

            df_concat = pd.concat(df)
            by_row_index = df_concat.groupby(df_concat.index)
            df_means = by_row_index.mean()
            filename = f'results/{analysis_name}_results_{date}.csv'
            df_means.to_csv(filename, header=True)

        school_results = school_dict(msims)
        filename = f'results/school_reopening_analysis_output_{scen}_{ttq_scen}_{date}.csv'
        school_results.to_csv(filename, header=True)


