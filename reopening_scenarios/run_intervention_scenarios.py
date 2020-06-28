'''Show optimized runs'''

import sciris as sc
from reopening_scenarios import create_sim as cs
import covasim as cv
import numpy as np
from covasim import utils as cvu

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


if __name__ == "__main__":

    rerun = True
    do_save = True
    n_reps = 20
    date = '06272020'

    analysis_name = 'school_reopening_analysis_80perc_mobility_withmasks'

    schools_closure_scenarios = ['no_school', 'with_NPI', 'with_cohorting', 'with_screening_notesting',
                                 'with_25perctest_notracing', 'with_50perctest_25tracing', 'with_200perctest_50tracing']

    schools_closure_scenarios_label = ['No School', 'School with NPI', 'School with NPI + Cohorting',
                                       'School with NPI, Cohorting, Screening', 'School with NPI, Cohorting, Screening, 25 Percent Follow-Up Testing',
                                       'School with NPI, Cohorting, Screening, 50% Follow-Up Testing, 25% Follow-Up Tracing',
                                       'School with NPI, Cohorting, Screening, 100% Follow-Up Testing, 50% Follow-Up Tracing']

    test_prob = [0, 0, 0, 0, .25, .5, 1]
    trace_prob = [0, 0, 0, 0, 0, .25, .5]
    NPI_schools = [None, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75]
    test_freq = None
    network_change = [False, False, True, True, True, True, True]
    school_start_day = [{'pk': None, 'es': None, 'ms': None, 'hs': None, 'uv': None},
                        '2020-09-01', '2020-09-01', '2020-09-01', '2020-09-01', '2020-09-01', '2020-09-01']
    intervention_start_day = [None, None, None,
                              {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
                              {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
                              {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
                              {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None}
                              ]

    # schools_closure_scenarios = ['with_cohorting']
    #
    # schools_closure_scenarios_label = ['School with NPI + Cohorting']
    #
    # test_prob = [ 0]
    # trace_prob = [0]
    # NPI_schools = [0.75]
    # test_freq = [None]
    # network_change = [True]
    # school_start_day = ['2020-09-01']
    # intervention_start_day = [None]

    if rerun:
        indices = range(n_reps)
        jsonfile = 'optimization_v12_safegraph_062620.json'
        json = sc.loadjson(jsonfile)

        msims = []
        for i, changes in enumerate(schools_closure_scenarios_label):
            all_sims = []
            num_school_closures = []
            for index in indices:
                entry = json[index]
                pars = entry['pars']
                pars['end_day'] = '2020-12-01'
                pars['rand_seed'] = int(entry['index'])
                all_sims.append(cs.create_sim(pars=pars, test_prob=test_prob[i],
                                              trace_prob=trace_prob[i], NPI_schools=NPI_schools[i],
                                              label=changes, test_freq=test_freq,
                                              network_change=network_change[i], school_start_day=school_start_day[i],
                                              intervention_start_day=intervention_start_day[i]))

            msim = cv.MultiSim(sims=all_sims)
            msim.run(reseed=False, par_args={'maxload': 0.8}, noise=0.0, keep_people=False)
            msim.reduce()
            if do_save:
                cv.save(filename=f'msims/calibrated_{schools_closure_scenarios[i]}.msim', obj=msim)
            msims.append(msim)

        sim_plots = cv.MultiSim.merge(msims, base=True)

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
                school_results[schools_closure_scenarios[i]]['num_students'] = []
                school_results[schools_closure_scenarios[i]]['total_cases'] = []
                school_results[schools_closure_scenarios[i]]['student_cases'] = []
                school_results[schools_closure_scenarios[i]]['teacher_cases'] = []
                school_results[schools_closure_scenarios[i]]['cases_in_pk'] = []
                school_results[schools_closure_scenarios[i]]['cases_in_es'] = []
                school_results[schools_closure_scenarios[i]]['cases_in_ms'] = []
                school_results[schools_closure_scenarios[i]]['cases_in_hs'] = []
                school_results[schools_closure_scenarios[i]]['cases_in_uv'] = []
                school_results[schools_closure_scenarios[i]]['pk_with_a_case'] = []
                school_results[schools_closure_scenarios[i]]['es_with_a_case'] = []
                school_results[schools_closure_scenarios[i]]['ms_with_a_case'] = []
                school_results[schools_closure_scenarios[i]]['hs_with_a_case'] = []
                school_results[schools_closure_scenarios[i]]['uv_with_a_case'] = []
                for j, sub_sim in enumerate(sim.sims):
                    if 'school_info' in sub_sim:
                        school_snapshot_dict = process_schools(sub_sim)
                        school_results[schools_closure_scenarios[i]]['total_cases'].append(school_snapshot_dict['total_infectious'])
                        school_results[schools_closure_scenarios[i]]['teacher_cases'].append(school_snapshot_dict['teachers_infectious'])
                        school_results[schools_closure_scenarios[i]]['student_cases'].append(school_snapshot_dict['students_infectious'])
                        school_results[schools_closure_scenarios[i]]['cases_in_pk'].append(
                            school_snapshot_dict['total_cases_in_pk'])
                        school_results[schools_closure_scenarios[i]]['cases_in_es'].append(school_snapshot_dict['total_cases_in_es'])
                        school_results[schools_closure_scenarios[i]]['cases_in_ms'].append(
                            school_snapshot_dict['total_cases_in_ms'])
                        school_results[schools_closure_scenarios[i]]['cases_in_hs'].append(
                            school_snapshot_dict['total_cases_in_hs'])
                        school_results[schools_closure_scenarios[i]]['cases_in_uv'].append(
                            school_snapshot_dict['total_cases_in_uv'])
                        school_results[schools_closure_scenarios[i]]['pk_with_a_case'].append(
                            school_snapshot_dict['total_pk_with_at_least_one_case'])
                        school_results[schools_closure_scenarios[i]]['es_with_a_case'].append(school_snapshot_dict['total_es_with_at_least_one_case'])
                        school_results[schools_closure_scenarios[i]]['ms_with_a_case'].append(
                            school_snapshot_dict['total_ms_with_at_least_one_case'])
                        school_results[schools_closure_scenarios[i]]['hs_with_a_case'].append(
                            school_snapshot_dict['total_hs_with_at_least_one_case'])
                        school_results[schools_closure_scenarios[i]]['uv_with_a_case'].append(
                            school_snapshot_dict['total_uv_with_at_least_one_case'])
                        school_results[schools_closure_scenarios[i]]['num_students'].append(
                            sub_sim.school_info['num_students'])
                        school_results[schools_closure_scenarios[i]]['school_closures'].append(
                            sub_sim.school_info['school_closures'])
                        school_results[schools_closure_scenarios[i]]['school_days_lost'].append(
                            sub_sim.school_info['school_days_lost'])
                        school_results[schools_closure_scenarios[i]]['cum_infections'].append(
                            sub_sim.summary['cum_infections'])
                        school_results[schools_closure_scenarios[i]]['num_tested'].append(
                            sub_sim.school_info['num_tested'])
                        school_results[schools_closure_scenarios[i]]['num_traced'].append(
                            sub_sim.school_info['num_traced'])
                        school_results[schools_closure_scenarios[i]]['test_pos'].append(
                            sub_sim.school_info['test_pos'])
            else:
                for sub_sim in sim.sims:
                    school_snapshot_dict = process_schools(sub_sim)
                    school_results[schools_closure_scenarios[i]]['total_cases'] = school_snapshot_dict['total_infectious']
                    school_results[schools_closure_scenarios[i]]['teacher_cases'] = school_snapshot_dict['teachers_infectious']
                    school_results[schools_closure_scenarios[i]]['student_cases'] = school_snapshot_dict['students_infectious']
                    school_results[schools_closure_scenarios[i]]['cases_in_pk'] = school_snapshot_dict[
                        'total_cases_in_pk']
                    school_results[schools_closure_scenarios[i]]['cases_in_es'] = school_snapshot_dict['total_cases_in_es']
                    school_results[schools_closure_scenarios[i]]['cases_in_ms'] = school_snapshot_dict['total_cases_in_ms']
                    school_results[schools_closure_scenarios[i]]['cases_in_hs'] = school_snapshot_dict['total_cases_in_hs']
                    school_results[schools_closure_scenarios[i]]['cases_in_uv'] = school_snapshot_dict[
                        'total_cases_in_uv']
                    school_results[schools_closure_scenarios[i]]['pk_with_a_case'] = school_snapshot_dict[
                        'total_pk_with_at_least_one_case']
                    school_results[schools_closure_scenarios[i]]['es_with_a_case'] = school_snapshot_dict['total_es_with_at_least_one_case']
                    school_results[schools_closure_scenarios[i]]['ms_with_a_case'] = school_snapshot_dict['total_ms_with_at_least_one_case']
                    school_results[schools_closure_scenarios[i]]['hs_with_a_case'] = school_snapshot_dict['total_hs_with_at_least_one_case']
                    school_results[schools_closure_scenarios[i]]['uv_with_a_case'] = school_snapshot_dict[
                        'total_uv_with_at_least_one_case']
                    school_results[schools_closure_scenarios[i]]['num_students'] = sub_sim.school_info[
                        'num_students']
                    school_results[schools_closure_scenarios[i]]['school_closures'] = sub_sim.school_info[
                        'school_closures']
                    school_results[schools_closure_scenarios[i]]['school_days_lost'] = sub_sim.school_info[
                        'school_days_lost']
                    school_results[schools_closure_scenarios[i]]['cum_infections'] = sub_sim.summary[
                        'cum_infections']
                    school_results[schools_closure_scenarios[i]]['num_tested'] = sub_sim.school_info['num_tested']
                    school_results[schools_closure_scenarios[i]]['num_traced'] = sub_sim.school_info['num_traced']
                    school_results[schools_closure_scenarios[i]]['test_pos'] = sub_sim.school_info['test_pos']

        csvfile = f'{analysis_name}_output.csv'
        with open(csvfile, 'w') as f:
            for key in school_results.keys():
                f.write("%s,%s\n" % (key, school_results[key]))

        figname = analysis_name
        fig1 = sim_plots.plot(to_plot=['new_infections'], do_show=False, max_sims=7)
        # for ax in fig1.axes:
        #     ax.set_xlim([200, 305])
        #     ax.set_ylim([0, 2000])
        fig1.savefig(f'new_infections_{figname}_{date}.png')
        fig2 = sim_plots.plot(to_plot=['cum_infections'], do_show=False, max_sims=7)
        fig2.savefig(f'cum_infections_{figname}_{date}.png')

    else:
        msims = []
        for i in schools_closure_scenarios:
            filename = f'msims/calibrated_{i}.msim'
            msims.append(cv.load(filename))
        sim_plots = cv.MultiSim.merge(msims, base=True)
        # school_results = dict()
        # for i, sim in enumerate(msims):
        #     school_results[schools_closure_scenarios[i]] = dict()
        #     if len(sim.sims) > 1:  # if running multiple param sets, print all of them
        #         school_results[schools_closure_scenarios[i]]['school_closures'] = []
        #         school_results[schools_closure_scenarios[i]]['cum_infections'] = []
        #         school_results[schools_closure_scenarios[i]]['num_tested'] = []
        #         school_results[schools_closure_scenarios[i]]['num_traced'] = []
        #         school_results[schools_closure_scenarios[i]]['test_pos'] = []
        #         school_results[schools_closure_scenarios[i]]['school_days_lost'] = []
        #         school_results[schools_closure_scenarios[i]]['num_students'] = []
        #         school_results[schools_closure_scenarios[i]]['total_cases'] = []
        #         school_results[schools_closure_scenarios[i]]['student_cases'] = []
        #         school_results[schools_closure_scenarios[i]]['teacher_cases'] = []
        #         school_results[schools_closure_scenarios[i]]['cases_in_pk'] = []
        #         school_results[schools_closure_scenarios[i]]['cases_in_es'] = []
        #         school_results[schools_closure_scenarios[i]]['cases_in_ms'] = []
        #         school_results[schools_closure_scenarios[i]]['cases_in_hs'] = []
        #         school_results[schools_closure_scenarios[i]]['cases_in_uv'] = []
        #         school_results[schools_closure_scenarios[i]]['pk_with_a_case'] = []
        #         school_results[schools_closure_scenarios[i]]['es_with_a_case'] = []
        #         school_results[schools_closure_scenarios[i]]['ms_with_a_case'] = []
        #         school_results[schools_closure_scenarios[i]]['hs_with_a_case'] = []
        #         school_results[schools_closure_scenarios[i]]['uv_with_a_case'] = []
        #         for j, sub_sim in enumerate(sim.sims):
        #             if 'school_info' in sub_sim:
        #                 school_snapshot_dict = process_schools(sub_sim)
        #                 school_results[schools_closure_scenarios[i]]['total_cases'].append(
        #                     school_snapshot_dict['total_infectious'])
        #                 school_results[schools_closure_scenarios[i]]['teacher_cases'].append(
        #                     school_snapshot_dict['teachers_infectious'])
        #                 school_results[schools_closure_scenarios[i]]['student_cases'].append(
        #                     school_snapshot_dict['students_infectious'])
        #                 school_results[schools_closure_scenarios[i]]['cases_in_pk'].append(
        #                     school_snapshot_dict['total_cases_in_pk'])
        #                 school_results[schools_closure_scenarios[i]]['cases_in_es'].append(
        #                     school_snapshot_dict['total_cases_in_es'])
        #                 school_results[schools_closure_scenarios[i]]['cases_in_ms'].append(
        #                     school_snapshot_dict['total_cases_in_ms'])
        #                 school_results[schools_closure_scenarios[i]]['cases_in_hs'].append(
        #                     school_snapshot_dict['total_cases_in_hs'])
        #                 school_results[schools_closure_scenarios[i]]['cases_in_uv'].append(
        #                     school_snapshot_dict['total_cases_in_uv'])
        #                 school_results[schools_closure_scenarios[i]]['pk_with_a_case'].append(
        #                     school_snapshot_dict['total_pk_with_at_least_one_case'])
        #                 school_results[schools_closure_scenarios[i]]['es_with_a_case'].append(
        #                     school_snapshot_dict['total_es_with_at_least_one_case'])
        #                 school_results[schools_closure_scenarios[i]]['ms_with_a_case'].append(
        #                     school_snapshot_dict['total_ms_with_at_least_one_case'])
        #                 school_results[schools_closure_scenarios[i]]['hs_with_a_case'].append(
        #                     school_snapshot_dict['total_hs_with_at_least_one_case'])
        #                 school_results[schools_closure_scenarios[i]]['uv_with_a_case'].append(
        #                     school_snapshot_dict['total_uv_with_at_least_one_case'])
        #                 school_results[schools_closure_scenarios[i]]['num_students'].append(
        #                     sub_sim.school_info['num_students'])
        #                 school_results[schools_closure_scenarios[i]]['school_closures'].append(
        #                     sub_sim.school_info['school_closures'])
        #                 school_results[schools_closure_scenarios[i]]['school_days_lost'].append(
        #                     sub_sim.school_info['school_days_lost'])
        #                 school_results[schools_closure_scenarios[i]]['cum_infections'].append(
        #                     sub_sim.summary['cum_infections'])
        #                 school_results[schools_closure_scenarios[i]]['num_tested'].append(
        #                     sub_sim.school_info['num_tested'])
        #                 school_results[schools_closure_scenarios[i]]['num_traced'].append(
        #                     sub_sim.school_info['num_traced'])
        #                 school_results[schools_closure_scenarios[i]]['test_pos'].append(
        #                     sub_sim.school_info['test_pos'])
        #     else:
        #         for sub_sim in sim.sims:
        #             school_snapshot_dict = process_schools(sub_sim)
        #             school_results[schools_closure_scenarios[i]]['total_cases'] = school_snapshot_dict[
        #                 'total_infectious']
        #             school_results[schools_closure_scenarios[i]]['teacher_cases'] = school_snapshot_dict[
        #                 'teachers_infectious']
        #             school_results[schools_closure_scenarios[i]]['student_cases'] = school_snapshot_dict[
        #                 'students_infectious']
        #             school_results[schools_closure_scenarios[i]]['cases_in_pk'] = school_snapshot_dict[
        #                 'total_cases_in_pk']
        #             school_results[schools_closure_scenarios[i]]['cases_in_es'] = school_snapshot_dict[
        #                 'total_cases_in_es']
        #             school_results[schools_closure_scenarios[i]]['cases_in_ms'] = school_snapshot_dict[
        #                 'total_cases_in_ms']
        #             school_results[schools_closure_scenarios[i]]['cases_in_hs'] = school_snapshot_dict[
        #                 'total_cases_in_hs']
        #             school_results[schools_closure_scenarios[i]]['cases_in_uv'] = school_snapshot_dict[
        #                 'total_cases_in_uv']
        #             school_results[schools_closure_scenarios[i]]['pk_with_a_case'] = school_snapshot_dict[
        #                 'total_pk_with_at_least_one_case']
        #             school_results[schools_closure_scenarios[i]]['es_with_a_case'] = school_snapshot_dict[
        #                 'total_es_with_at_least_one_case']
        #             school_results[schools_closure_scenarios[i]]['ms_with_a_case'] = school_snapshot_dict[
        #                 'total_ms_with_at_least_one_case']
        #             school_results[schools_closure_scenarios[i]]['hs_with_a_case'] = school_snapshot_dict[
        #                 'total_hs_with_at_least_one_case']
        #             school_results[schools_closure_scenarios[i]]['uv_with_a_case'] = school_snapshot_dict[
        #                 'total_uv_with_at_least_one_case']
        #             school_results[schools_closure_scenarios[i]]['num_students'] = sub_sim.school_info[
        #                 'num_students']
        #             school_results[schools_closure_scenarios[i]]['school_closures'] = sub_sim.school_info[
        #                 'school_closures']
        #             school_results[schools_closure_scenarios[i]]['school_days_lost'] = sub_sim.school_info[
        #                 'school_days_lost']
        #             school_results[schools_closure_scenarios[i]]['cum_infections'] = sub_sim.summary[
        #                 'cum_infections']
        #             school_results[schools_closure_scenarios[i]]['num_tested'] = sub_sim.school_info['num_tested']
        #             school_results[schools_closure_scenarios[i]]['num_traced'] = sub_sim.school_info['num_traced']
        #             school_results[schools_closure_scenarios[i]]['test_pos'] = sub_sim.school_info['test_pos']
        # csvfile = f'{analysis_name}_output.csv'
        # with open(csvfile, 'w') as f:
        #     for key in school_results.keys():
        #         f.write("%s,%s\n" % (key, school_results[key]))

        figname = analysis_name
        fig1 = sim_plots.plot(to_plot=['n_infectious'], do_show=False, max_sims=7)
        for ax in fig1.axes:
            ax.set_xlim([200, 309])
            ax.set_ylim([0, 2000])
        fig1.savefig(f'infectious_{figname}_{date}.png')

        fig2 = sim_plots.plot(to_plot=['new_infections'], do_show=False, max_sims=7)
        for ax in fig2.axes:
            ax.set_xlim([200, 309])
            ax.set_ylim([0, 500])
        fig2.savefig(f'new_infections_{figname}_{date}.png')

        fig3 = sim_plots.plot(to_plot=['cum_infections'], do_show=False, max_sims=7)
        for ax in fig3.axes:
            ax.set_xlim([200, 309])
            ax.set_ylim([70000, 100000])
        fig3.savefig(f'cum_infections_{figname}_{date}.png')
