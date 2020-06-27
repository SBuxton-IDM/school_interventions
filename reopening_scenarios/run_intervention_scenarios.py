'''Show optimized runs'''

import sciris as sc
from reopening_scenarios import create_sim as cs
import covasim as cv
import numpy as np
from covasim import utils as cvu

cv.check_save_version('1.4.7', die=True)

def process_schools(sub_sim):
    snapshot = sub_sim['analyzers'][1]
    num_asymp = []
    num_symp = []
    num_exposed = []

    for _, shot in snapshot.snapshots.items():
        inds_of_exposed = []
        inds_of_infectious = []
        inds_of_symptomatic = []

        for _, school in shot.schools.items():
            if isinstance(school, int):
                school = [school]
            inds_of_exposed += cvu.itrue(shot.exposed[school], np.array(school)).tolist()
            inds_of_infectious += cvu.itrue(shot.infectious[school], np.array(school)).tolist()
            inds_of_symptomatic += cvu.itrue(shot.symptomatic[school], np.array(school)).tolist()

        inds_asymptomatic = [x for x in inds_of_infectious if x not in inds_of_symptomatic]
        inds_not_yet_infected = [x for x in inds_of_exposed if x not in inds_of_infectious]
        num_exposed.append(len(inds_not_yet_infected))
        num_asymp.append(len(inds_asymptomatic))
        num_symp.append(len(inds_of_symptomatic))

    return num_asymp, num_symp


if __name__ == "__main__":

    rerun = True
    do_save = False
    n_reps = 1
    date = '06262020'

    analysis_name = 'school_reopening'

    schools_closure_scenarios = ['as_normal', 'with_NPI', 'with_screening',
                                 'with_test_trace', 'with_daily_testing']

    schools_closure_scenarios_label = ['As Normal', 'NPI', 'NPI, Screening',
                                       'NPI, Screening, Testing, Tracing',
                                       'NPI, Screening, Testing, Tracing, Daily Testing']

    test_prob = [0, 0, 0, 1, 1]
    trace_prob = [0, 0, 0, 1, 1]
    NPI_schools = [None, 0.75, 0.75, 0.75, 0.75]
    test_freq = [None, None, None, None, 1]
    network_change = False
    school_start_day = {'pk': '2020-09-01', 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None}
    intervention_start_day = [None, None,
                              {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
                              {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None},
                              {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None}]

    # schools_closure_scenarios = ['weekly_testing', 'daily_testing']
    #
    # schools_closure_scenarios_label = ['NPI, Screening, Testing, Tracing, Weekly Testing',
    #                                    'NPI, Screening, Testing, Tracing, Daily Testing']

    # test_prob = [1, 1]
    # trace_prob = [1, 1]
    # NPI_schools = [0.75, 0.75]
    # test_freq = [7, 1]
    # network_change = False
    # school_start_day = {'pk': '2020-09-01', 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None}
    # intervention_start_day = {'pk': None, 'es': '2020-09-01', 'ms': '2020-09-01', 'hs': '2020-09-01', 'uv': None}


    if rerun:
        indices = range(n_reps)
        jsonfile = 'optimization_v12_safegraph_061720.json'
        json = sc.loadjson(jsonfile)

        msims = []
        for i, changes in enumerate(schools_closure_scenarios):
            all_sims = []
            num_school_closures = []
            for index in indices:
                entry = json[index]
                pars = entry['pars']
                pars['end_day'] = '2020-12-01'
                pars['rand_seed'] = int(entry['index'])
                all_sims.append(cs.create_sim(pars=pars, test_prob=test_prob[i],
                                              trace_prob=trace_prob[i], NPI_schools=NPI_schools[i],
                                              label=changes, test_freq=test_freq[i],
                                              network_change=network_change, school_start_day=school_start_day,
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
                school_results[schools_closure_scenarios[i]]['num_symptomatic'] = []
                school_results[schools_closure_scenarios[i]]['num_asymptomatic'] = []
                for j, sub_sim in enumerate(sim.sims):
                    if 'school_info' in sub_sim:
                        # num_asymp, num_symp = process_schools(sub_sim)
                        # school_results[schools_closure_scenarios[i]]['num_asymptomatic'].append(num_asymp)
                        # school_results[schools_closure_scenarios[i]]['num_symptomatic'].append(num_symp)
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
                    # num_asymp, num_symp = process_schools(sub_sim)
                    # school_results[schools_closure_scenarios[i]]['num_asymptomatic'] = num_asymp
                    # school_results[schools_closure_scenarios[i]]['num_symptomatic'] = num_symp
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
        fig1 = sim_plots.plot(to_plot=['n_infectious'], do_show=False, max_sims=7)
        for ax in fig1.axes:
            ax.set_xlim([200, 305])
            ax.set_ylim([0, 2000])
        fig1.savefig(f'infectious_{figname}_{date}.png')
        fig2 = sim_plots.plot(to_plot=['r_eff'], do_show=False)
        fig2.savefig(f'reff_{figname}_{date}.png')

    else:
        msims = []
        for i in schools_closure_scenarios:
            filename = f'msims/calibrated_{i}.msim'
            msims.append(cv.load(filename))
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
                school_results[schools_closure_scenarios[i]]['num_symptomatic'] = []
                school_results[schools_closure_scenarios[i]]['num_asymptomatic'] = []
                for j, sub_sim in enumerate(sim.sims):
                    if 'school_info' in sub_sim:
                        # num_asymp, num_symp = process_schools(sub_sim)
                        # school_results[schools_closure_scenarios[i]]['num_asymptomatic'].append(num_asymp)
                        # school_results[schools_closure_scenarios[i]]['num_symptomatic'].append(num_symp)
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
                    # num_asymp, num_symp = process_schools(sub_sim)
                    # school_results[schools_closure_scenarios[i]]['num_asymptomatic'] = num_asymp
                    # school_results[schools_closure_scenarios[i]]['num_symptomatic'] = num_symp
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
        fig1 = sim_plots.plot(to_plot=['n_infectious'], do_show=False, max_sims=7)
        for ax in fig1.axes:
            ax.set_xlim([200, 309])
            ax.set_ylim([0, 2000])
        fig1.savefig(f'infectious_{figname}_{date}.png')

        fig2 = sim_plots.plot(to_plot=['r_eff'], do_show=False)
        fig2.savefig(f'reff_{figname}_{date}.png')

        # fig3 = sim_plots.plot(to_plot=['new_tests', 'new_quarantined'], do_show=False)
        # for ax in fig3.axes:
        #     ax.set_xlim([210, 249])
        # fig3.savefig(f'resources_{figname}_{date}.png')




