'''Show optimized runs'''

import covasim as cv
import sciris as sc
import pandas as pd


def school_dict(msims, day_schools_reopen):
    school_results = dict()
    for i, sim in enumerate(msims):
        school_results[schools_reopening_scenarios[i]] = dict()
        if len(sim.sims) > 1:  # if running multiple param sets, print all of them
            school_results[schools_reopening_scenarios[i]]['school_closures'] = []
            school_results[schools_reopening_scenarios[i]]['cum_infections'] = []
            school_results[schools_reopening_scenarios[i]]['num_tested'] = []
            school_results[schools_reopening_scenarios[i]]['num_traced'] = []
            school_results[schools_reopening_scenarios[i]]['test_pos'] = []
            school_results[schools_reopening_scenarios[i]]['school_days_lost'] = []
            school_results[schools_reopening_scenarios[i]]['student_school_days'] = []
            school_results[schools_reopening_scenarios[i]]['perc_school_days_lost'] = []
            school_results[schools_reopening_scenarios[i]]['num_teachers'] = []
            school_results[schools_reopening_scenarios[i]]['num_teachers_tested'] = []
            school_results[schools_reopening_scenarios[i]]['num_teachers_test_pos'] = []
            school_results[schools_reopening_scenarios[i]]['num_teachers_screen_pos'] = []
            school_results[schools_reopening_scenarios[i]]['num_teacher_cases'] = []

            school_results[schools_reopening_scenarios[i]]['num_staff'] = []
            school_results[schools_reopening_scenarios[i]]['num_staff_tested'] = []
            school_results[schools_reopening_scenarios[i]]['num_staff_test_pos'] = []
            school_results[schools_reopening_scenarios[i]]['num_staff_screen_pos'] = []
            school_results[schools_reopening_scenarios[i]]['num_staff_cases'] = []

            school_results[schools_reopening_scenarios[i]]['num_students'] = []
            school_results[schools_reopening_scenarios[i]]['num_students_tested'] = []
            school_results[schools_reopening_scenarios[i]]['num_students_test_pos'] = []
            school_results[schools_reopening_scenarios[i]]['num_students_screen_pos'] = []
            school_results[schools_reopening_scenarios[i]]['num_student_cases'] = []

            school_results[schools_reopening_scenarios[i]]['cum_infectious_staff'] = []
            school_results[schools_reopening_scenarios[i]]['cum_infectious_students'] = []
            school_results[schools_reopening_scenarios[i]]['cum_asymp_staff'] = []
            school_results[schools_reopening_scenarios[i]]['cum_asymp_students'] = []

            school_results[schools_reopening_scenarios[i]]['num_es'] = []
            school_results[schools_reopening_scenarios[i]]['num_ms'] = []
            school_results[schools_reopening_scenarios[i]]['num_hs'] = []
            for j, sub_sim in enumerate(sim.sims):
                school_results[schools_reopening_scenarios[i]]['num_students'].append(
                    sub_sim.school_info['num_students'])
                school_results[schools_reopening_scenarios[i]]['school_closures'].append(
                    sub_sim.school_info['school_closures'])
                school_results[schools_reopening_scenarios[i]]['school_days_lost'].append(
                    sub_sim.school_info['school_days_lost'])
                school_results[schools_reopening_scenarios[i]]['student_school_days'].append(
                    sub_sim.school_info['total_student_school_days'])
                school_results[schools_reopening_scenarios[i]]['perc_school_days_lost'].append(
                    sub_sim.school_info['school_days_lost'] / sub_sim.school_info['total_student_school_days'])
                school_results[schools_reopening_scenarios[i]]['cum_infections'].append(
                    sub_sim.summary['cum_infections'] - sub_sim.results['cum_infections'].values[day_schools_reopen])
                school_results[schools_reopening_scenarios[i]]['num_tested'].append(
                    sub_sim.school_info['num_tested'])
                school_results[schools_reopening_scenarios[i]]['num_traced'].append(
                    sub_sim.school_info['num_traced'])
                school_results[schools_reopening_scenarios[i]]['test_pos'].append(
                    sub_sim.school_info['test_pos'])
                school_results[schools_reopening_scenarios[i]]['num_es'].append(sub_sim.school_info['num_es'])
                school_results[schools_reopening_scenarios[i]]['num_ms'].append(sub_sim.school_info['num_ms'])
                school_results[schools_reopening_scenarios[i]]['num_hs'].append(sub_sim.school_info['num_hs'])
                school_results[schools_reopening_scenarios[i]]['num_teachers_tested'].append(
                    sub_sim.school_info['num_teachers_tested'])
                school_results[schools_reopening_scenarios[i]]['num_teachers_test_pos'].append(
                    sub_sim.school_info['num_teachers_test_pos'])
                school_results[schools_reopening_scenarios[i]]['num_teachers_screen_pos'].append(
                    sub_sim.school_info['num_teachers_screen_pos'])
                school_results[schools_reopening_scenarios[i]]['num_teacher_cases'].append(
                    sub_sim.school_info['num_teacher_cases'])
                school_results[schools_reopening_scenarios[i]]['num_teachers'].append(sub_sim.school_info['num_teachers'])

                school_results[schools_reopening_scenarios[i]]['num_staff_tested'].append(
                    sub_sim.school_info['num_staff_tested'])
                school_results[schools_reopening_scenarios[i]]['num_staff_test_pos'].append(
                    sub_sim.school_info['num_staff_test_pos'])
                school_results[schools_reopening_scenarios[i]]['num_staff_screen_pos'].append(
                    sub_sim.school_info['num_staff_screen_pos'])
                school_results[schools_reopening_scenarios[i]]['num_staff_cases'].append(
                    sub_sim.school_info['num_staff_cases'])
                school_results[schools_reopening_scenarios[i]]['num_staff'].append(sub_sim.school_info['num_staff'])

                school_results[schools_reopening_scenarios[i]]['num_students_tested'].append(
                    sub_sim.school_info['num_students_tested'])
                school_results[schools_reopening_scenarios[i]]['num_students_test_pos'].append(
                    sub_sim.school_info['num_students_test_pos'])
                school_results[schools_reopening_scenarios[i]]['num_students_screen_pos'].append(
                    sub_sim.school_info['num_students_screen_pos'])
                school_results[schools_reopening_scenarios[i]]['num_student_cases'].append(
                    sub_sim.school_info['num_student_cases'])
                school_results[schools_reopening_scenarios[i]]['num_students'].append(sub_sim.school_info['num_students'])

                school_results[schools_reopening_scenarios[i]]['cum_infectious_staff'].append(
                    sum(sub_sim.school_info['num_staff_infectious']))
                school_results[schools_reopening_scenarios[i]]['cum_infectious_students'].append(
                    sum(sub_sim.school_info['num_students_infectious']))
                school_results[schools_reopening_scenarios[i]]['cum_asymp_staff'].append(
                    sum(sub_sim.school_info['num_staff_asymptomatic']))
                school_results[schools_reopening_scenarios[i]]['cum_asymp_students'].append(
                    sum(sub_sim.school_info['num_students_asymptomatic']))

        else:
            for sub_sim in sim.sims:
                school_results[schools_reopening_scenarios[i]]['num_teachers_tested'] = sub_sim.school_info[
                    'num_teachers_tested']
                school_results[schools_reopening_scenarios[i]]['num_teachers_test_pos'] = sub_sim.school_info[
                    'num_teachers_test_pos']
                school_results[schools_reopening_scenarios[i]]['num_teachers_screen_pos'] = sub_sim.school_info[
                    'num_teachers_screen_pos']
                school_results[schools_reopening_scenarios[i]]['num_teacher_cases'] = sub_sim.school_info[
                    'num_teacher_cases']
                school_results[schools_reopening_scenarios[i]]['num_teachers'] = sub_sim.school_info['num_teachers']

                school_results[schools_reopening_scenarios[i]]['num_staff_tested'] = sub_sim.school_info[
                    'num_staff_tested']
                school_results[schools_reopening_scenarios[i]]['num_staff_test_pos'] = sub_sim.school_info[
                    'num_staff_test_pos']
                school_results[schools_reopening_scenarios[i]]['num_staff_screen_pos'] = sub_sim.school_info[
                    'num_staff_screen_pos']
                school_results[schools_reopening_scenarios[i]]['num_staff_cases'] = sub_sim.school_info['num_staff_cases']
                school_results[schools_reopening_scenarios[i]]['num_staff'] = sub_sim.school_info['num_staff']

                school_results[schools_reopening_scenarios[i]]['num_students_tested'] = sub_sim.school_info[
                    'num_students_tested']
                school_results[schools_reopening_scenarios[i]]['num_students_test_pos'] = sub_sim.school_info[
                    'num_students_test_pos']
                school_results[schools_reopening_scenarios[i]]['num_students_screen_pos'] = sub_sim.school_info[
                    'num_students_screen_pos']
                school_results[schools_reopening_scenarios[i]]['num_student_cases'] = sub_sim.school_info[
                    'num_student_cases']
                #school_results[schools_reopening_scenarios[i]]['num_students'] = sub_sim.school_info['num_students']

                school_results[schools_reopening_scenarios[i]]['cum_infectious_staff'] = sum(
                    sub_sim.school_info['num_staff_infectious'])
                school_results[schools_reopening_scenarios[i]]['cum_infectious_students'] = sum(
                    sub_sim.school_info['num_students_infectious'])
                school_results[schools_reopening_scenarios[i]]['cum_asymp_staff'] = sum(
                    sub_sim.school_info['num_staff_asymptomatic'])
                school_results[schools_reopening_scenarios[i]]['cum_asymp_students'] = sum(
                    sub_sim.school_info['num_students_asymptomatic'])

                school_results[schools_reopening_scenarios[i]]['num_students'] = sub_sim.school_info[
                    'num_students']
                school_results[schools_reopening_scenarios[i]]['school_closures'] = sub_sim.school_info[
                    'school_closures']
                school_results[schools_reopening_scenarios[i]]['school_days_lost'] = sub_sim.school_info[
                    'school_days_lost']
                school_results[schools_reopening_scenarios[i]]['student_school_days'] = sub_sim.school_info[
                    'total_student_school_days']
                school_results[schools_reopening_scenarios[i]]['perc_school_days_lost'] = sub_sim.school_info[
                                                                                            'school_days_lost'] / \
                                                                                        sub_sim.school_info[
                                                                                            'total_student_school_days']
                school_results[schools_reopening_scenarios[i]]['cum_infections'] = sub_sim.summary[
                                                                                     'cum_infections'] - \
                                                                                 sub_sim.results[
                                                                                     'cum_infections'].values[day_schools_reopen]
                school_results[schools_reopening_scenarios[i]]['num_tested'] = sub_sim.school_info['num_tested']
                school_results[schools_reopening_scenarios[i]]['num_traced'] = sub_sim.school_info['num_traced']
                school_results[schools_reopening_scenarios[i]]['test_pos'] = sub_sim.school_info['test_pos']

                school_results[schools_reopening_scenarios[i]]['num_es'] = sub_sim.school_info['num_es']
                school_results[schools_reopening_scenarios[i]]['num_ms'] = sub_sim.school_info['num_ms']
                school_results[schools_reopening_scenarios[i]]['num_hs'] = sub_sim.school_info['num_hs']

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

    return school_results


if __name__ == '__main__':

    popfile_stem = 'inputs/kc_synthpops_normal_withstaff_seed'
    popfile_stem_change = 'inputs/kc_synthpops_clustered_withstaff_seed'
    date = '2020-08-04'

    n_seeds = 20

    rel_trans = False
    beta_layer = False

    schools_reopening_scenarios = [
        'as_normal',
        'with_screening',
        'with_hybrid_scheduling',
        'ES_MS_inperson_HS_remote',
        'ES_inperson_MS_HS_remote',
        'ES_hybrid',
        'all_remote',
    ]
    schools_reopening_scenarios_label = [
        'As Normal',
        'With Screening',
        'All Hybrid',
        'ES/MS in Person, HS Remote',
        'ES in Person, MS/HS Remote',
        'ES Hybrid',
        'All Remote',
    ]
    test_prob = [
        0,
        .5,
        .5,
        .5,
        .5,
        .5,
        0,
    ]
    trace_prob = [
        0,
        .5,
        .5,
        .5,
        .5,
        .5,
        0,
    ]
    NPI = [
        None,
        0.75,
        0.75,
        0.75,
        0.75,
        0.75,
        None,
    ]
    intervention_start_day = [
        None,
        {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
        {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
        {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': None, 'uv': None},
        {'pk': None, 'es': '2020-09-01', 'ms': None, 'hs': None, 'uv': None},
        {'pk': None, 'es': '2020-09-01', 'ms': None, 'hs': None, 'uv': None},
        None,
    ]
    schedule = [
        None,
        None,
        {'pk': None, 'es': True, 'ms': True, 'hs': True, 'uv': None},
        None,
        None,
        {'pk': None, 'es': True, 'ms': None, 'hs': None, 'uv': None},
        None,
    ]
    day_schools_close = '2020-07-01'
    day_schools_open = [
        {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
        {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
        {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
        {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': None, 'uv': None},
        {'pk': None, 'es': '2020-09-01', 'ms': None, 'hs': None, 'uv': None},
        {'pk': None, 'es': '2020-09-01', 'ms': None, 'hs': None, 'uv': None},
        None,
    ]
    tp = sc.objdict(
        symp_prob=0.03,
        asymp_prob=0.001,
        symp_quar_prob=0.01,
        asymp_quar_prob=0.001,
        test_delay=5.0,
    )
    ct = sc.objdict(
        trace_probs={'w': 0.1, 'c': 0, 'h': 0.8, 's': 0.8},
        trace_time=5.0,
    )
    res = ['0.9', '1.1']
    if rel_trans or beta_layer:
        cases = ['50']
    else:
        cases = ['20', '50', '110']
    for re in res:
        for case in cases:
            if rel_trans:
                jsonfile = f'optimization_school_reopening_re_{re}_cases_{case}_reltrans.json'
            else:
                jsonfile = f'optimization_school_reopening_re_{re}_cases_{case}.json'
            json = sc.loadjson(jsonfile)
            msims = []
            es_with_a_case = []
            ms_with_a_case = []
            hs_with_a_case = []
            for i, scen in enumerate(schools_reopening_scenarios):
                analysis_name = f'{scen}_{case}_cases_re_{re}'
                if rel_trans:
                    analysis_name = analysis_name + '_under10_0.5trans'

                if beta_layer:
                    analysis_name = analysis_name + '_3xschool_beta_layer'

                all_sims = []
                for j in range(n_seeds):
                    entry = json[j]
                    p = entry['pars']
                    pars = {'pop_size': 225e3,
                            'pop_scale': 10,
                            'pop_type': 'synthpops',
                            'pop_infected': p['pop_infected'],
                            'rescale': True,
                            'rescale_factor': 1.1,
                            'verbose': 0,
                            'start_day': '2020-07-01',
                            'end_day': '2020-12-01',
                            'rand_seed': int(entry['index']),
                            }
                    n_popfiles = 5
                    popfile = popfile_stem_change + str(pars['rand_seed'] % n_popfiles) + '.ppl'
                    popfile_new = popfile_stem_change + str(pars['rand_seed'] % n_popfiles) + '.ppl'
                    if scen == 'as_normal':
                        popfile = popfile
                    else:
                        popfile = popfile_new
                    sim = cv.Sim(pars, popfile=popfile, load_pop=True, label=scen)
                    day_schools_reopen = sim.day('2020-09-01')
                    interventions = [
                        cv.test_prob(start_day='2020-07-01', **tp),
                        cv.contact_tracing(start_day='2020-07-01', **ct),
                        cv.clip_edges(days='2020-08-01', changes=p['clip_edges'], layers='w', label='close_work'),
                        cv.clip_edges(days='2020-08-01', changes=p['clip_edges'], layers='c', label='close_community'),
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
                            ili_prev=0.002,
                            schedule=schedule[i],
                            num_pos=None,
                            label='reopen_schools'
                        )
                    ]
                    if rel_trans:
                        sim['prognoses']['trans_ORs'][0] = 0.5
                    if beta_layer:
                        sim['beta_layer']['s'] = 3

                    if NPI[i] is not None:
                        interventions += [
                            cv.change_beta(days='2020-09-01', changes=NPI[i], layers='s', label='NPI_schools')]
                    sim['interventions'] = interventions
                    for interv in sim['interventions']:
                        interv.do_plot = False
                    all_sims.append(sim)
                msim = cv.MultiSim(all_sims)
                msim.run(reseed=False, par_args={'maxload': 0.8}, noise=0.0, keep_people=True)
                msim.reduce()
                msims.append(msim)
                es = []
                ms = []
                hs = []
                df = []
                for j in range(len(msim.sims)):
                    # fig = msim.sims[j].people.plot()
                    # fig.show()
                    # staff_cases = msim.sims[j].school_info['num_teacher_cases']
                    # staff_cases += msim.sims[j].school_info['num_staff_cases']
                    # student_cases = msim.sims[j].school_info['num_student_cases']
                    # print(f'Re = {re}, cases = {case}')
                    # print(f'number staff cases on 09/01 {staff_cases}')
                    # print(f'number student cases on 09/01 {student_cases}')
                    filename = f'results/{analysis_name}_param{j}_results_{date}.csv'
                    results = pd.DataFrame(msim.sims[j].results)
                    results.to_csv(filename, header=True)
                    df.append(results)
                    es.append(pd.DataFrame(msim.sims[j].school_info['es_with_a_case']))
                    ms.append(pd.DataFrame(msim.sims[j].school_info['ms_with_a_case']))
                    hs.append(pd.DataFrame(msim.sims[j].school_info['hs_with_a_case']))
                    msim.sims[j].school_info = msim.sims[j].school_info

                del msim.orig_base_sim
                msim.save(filename=f'{analysis_name}.msim')
                df_concat = pd.concat(df)
                by_row_index = df_concat.groupby(df_concat.index)
                df_means = by_row_index.mean()
                filename = f'results/{analysis_name}_results_{date}.csv'
                df_means.to_csv(filename, header=True)

                es_concat = pd.concat(es)
                by_row_index = es_concat.groupby(es_concat.index)
                es_means = by_row_index.mean()
                es_means.columns = [scen]
                es_with_a_case.append(es_means)

                ms_concat = pd.concat(ms)
                by_row_index = ms_concat.groupby(ms_concat.index)
                ms_means = by_row_index.mean()
                ms_means.columns = [scen]
                ms_with_a_case.append(ms_means)

                hs_concat = pd.concat(hs)
                by_row_index = hs_concat.groupby(hs_concat.index)
                hs_means = by_row_index.mean()
                hs_means.columns = [scen]
                hs_with_a_case.append(hs_means)

            es_with_a_case = pd.concat(es_with_a_case, ignore_index=True, axis=1)
            es_with_a_case.columns = schools_reopening_scenarios_label
            ms_with_a_case = pd.concat(ms_with_a_case, ignore_index=True, axis=1)
            ms_with_a_case.columns = schools_reopening_scenarios_label
            hs_with_a_case = pd.concat(hs_with_a_case, ignore_index=True, axis=1)
            hs_with_a_case.columns = schools_reopening_scenarios_label
            with pd.ExcelWriter(f'results/schools_with_a_case_{case}_cases_re_{re}_{date}.xlsx') as writer:
                es_with_a_case.to_excel(writer, sheet_name='ES')
                ms_with_a_case.to_excel(writer, sheet_name='MS')
                hs_with_a_case.to_excel(writer, sheet_name='HS')

            school_results = school_dict(msims, day_schools_reopen)
            filename = f'results/school_reopening_analysis_output_{case}_cases_re_{re}_{date}.csv'
            if rel_trans:
                filename = f'results/school_reopening_analysis_output_{case}_cases_re_{re}_under10_0.5trans_{date}.csv'
            if beta_layer:
                filename = f'results/school_reopening_analysis_output_{case}_cases_re_{re}_3xschool_beta_layer_{date}.csv'

            school_results.to_csv(filename, header=True)
