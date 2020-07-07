'''Show optimized runs'''

#%Imports
import sciris as sc
from SPS_analysis import create_sim as cs
import covasim as cv
import numpy as np
from covasim import utils as cvu
import pandas as pd

cv.check_save_version('1.4.7', die=True)


def school_dict(msims, school_dicts, index):
    school_results = dict()
    for i, sim in enumerate(msims):
        label = sim.base_sim.label
        school_results[label] = dict()
        if len(sim.sims) > 1:  # if running multiple seeds, print all of them
            school_results[label]['num_teachers_tested'] = []
            school_results[label]['num_teachers_test_pos'] = []
            school_results[label]['num_teachers_screen_pos'] = []
            school_results[label]['num_students_screen_pos'] = []
            school_results[label]['num_teacher_cases'] = []
            school_results[label]['num_student_cases'] = []
            for j, sub_sim in enumerate(sim.sims):
                school_results[label]['num_teachers_tested'].append(sub_sim.school_info['num_teachers_tested'])
                school_results[label]['num_teachers_test_pos'].append(sub_sim.school_info['num_teachers_test_pos'])
                school_results[label]['num_teachers_screen_pos'].append(sub_sim.school_info['num_teachers_screen_pos'])
                school_results[label]['num_students_screen_pos'].append(sub_sim.school_info['num_students_screen_pos'])
                school_results[label]['num_teacher_cases'].append(sub_sim.school_info['num_teacher_cases'])
                school_results[label]['num_student_cases'].append(sub_sim.school_info['num_student_cases'])
        else:
            for sub_sim in sim.sims:
                school_results[label]['num_teachers_tested'] = sub_sim.school_info['num_teachers_tested']
                school_results[label]['num_teachers_test_pos'] = sub_sim.school_info['num_teachers_test_pos']
                school_results[label]['num_teachers_screen_pos'] = sub_sim.school_info['num_teachers_screen_pos']
                school_results[label]['num_students_screen_pos'] = sub_sim.school_info['num_students_screen_pos']
                school_results[label]['num_teacher_cases'] = sub_sim.school_info['num_teacher_cases']
                school_results[label]['num_student_cases'] = sub_sim.school_info['num_student_cases']


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
    if index == 0:
        school_dicts[label] = dict()

    school_dicts[label][index] = school_results
    return school_results

def process_school_dicts(school_dicts, n_params, scenarios):
    df_list = []
    for scen in scenarios:
        scen_list = []
        for i in range(n_params):
            dfi = school_dicts[scen][i]
            scen_list.append(dfi)
        df = pd.concat(scen_list, axis=1)
        df = df.mean(axis=1)
        df_list.append(df)
    df_final = pd.concat(df_list, axis=1)
    df_final.columns = scenarios
    return df_final


if __name__ == "__main__":

    do_save = True
    n_params = 2
    n_seeds = 2
    date = '07062020'


    school_reopening_pars = {
                        'test_prob': 0,
                        'trace_prob': 1,
                        'NPI_schools': 0.75,
                        'network_change': True,
                        'school_start_day': '2020-09-01',
                        'intervention_start_day': {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
                        'ttq_scen': 'medium',
                        'mobility_scens': '80_perc',
                        'mobility_file': f'inputs/KC_weeklyinteractions_070120_80perc.csv'
                        }

    teacher_testing_scens = {
                        'no_teacher_testing': {'test_freq': None},
                        # 'every_over_day_teacher_testing': {'test_freq': 2},
                        'weekly_teacher_testing': {'test_freq': 7},
                        'biweekly_teacher_testing': {'test_freq': 14},
                        # 'monthly_teacher_testing': {'test_freq': 30},
                        }

    indices = range(n_params)
    seeds = range(n_seeds)
    jsonfile = 'optimization_v12_safegraph_070120.json'
    json = sc.loadjson(jsonfile)

    school_dicts = dict()
    for scen, teacher_testing in teacher_testing_scens.items():
        analysis_name = f'teacher_testing_analysis_{scen}'
        msims = []
        for index in indices:
            all_sims = []
            entry = json[index]
            pars = entry['pars']
            pars['end_day'] = '2020-10-01'
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
                # filename = f'results/{analysis_name}_param{index}_results.csv'
                # df_means.to_csv(filename, header=True)
                school_results = school_dict(msims, school_dicts, index)
                # filename = f'results/{analysis_name}_param{index}_output.csv'
                # school_results.to_csv(filename, header=True)

    final_results = process_school_dicts(school_dicts, n_params, teacher_testing_scens.keys())
    filename = f'results/teacher_testing_analysis_combined_output_{date}.csv'
    final_results.to_csv(filename, header=True)