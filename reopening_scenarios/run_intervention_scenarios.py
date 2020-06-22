'''Show optimized runs'''

import sciris as sc
from reopening_scenarios import create_sim as cs
import covasim as cv
import numpy as np
from covasim import utils as cvu

cv.check_save_version('1.4.7', die=True)

def process_schools(sub_sim):
    snapshot = sub_sim['analyzers'][1]
    num_students = []
    num_asymp = []
    num_symp = []
    num_exposed = []

    for _, shot in snapshot.snapshots.items():
        inds_of_exposed = []
        inds_of_infectious = []
        inds_of_symptomatic = []
        num_of_students = 0

        for _, school in shot.schools.items():
            if isinstance(school, int):
                school = [school]
            num_of_students += len(school)
            inds_of_exposed += cvu.itrue(shot.exposed[school], np.array(school)).tolist()
            inds_of_infectious += cvu.itrue(shot.infectious[school], np.array(school)).tolist()
            inds_of_symptomatic += cvu.itrue(shot.symptomatic[school], np.array(school)).tolist()

        inds_asymptomatic = [x for x in inds_of_infectious if x not in inds_of_symptomatic]
        inds_not_yet_infected = [x for x in inds_of_exposed if x not in inds_of_infectious]
        num_exposed.append(len(inds_not_yet_infected))
        num_asymp.append(len(inds_asymptomatic))
        num_symp.append(len(inds_of_symptomatic))
        num_students.append(num_of_students)

    return num_students, num_asymp, num_symp

if __name__ == "__main__":

    rerun = True
    do_save = True
    n_reps = 5
    date = '06222020'

    analysis_name = 'school_reopening_analysis'

    # schools_closure_scenarios = ['as_normal', 'with_NPI', 'with_NPI_screen_test_trace',
    #                              'with_NPI_screen_test_trace_close']
    # num_pos = [None, None, 10000, 10]
    # test_prob = 1
    # trace_prob = 1
    # NPI_schools = [None, 0.5, 0.5, 0.5]

    schools_closure_scenarios = ['schools_stay_closed']
    num_pos = [None]
    test_prob = 1
    trace_prob = 1
    NPI_schools = [0]


    if rerun:
        indices = range(n_reps)
        jsonfile = 'optimization_v12_safegraph_061720.json'
        json = sc.loadjson(jsonfile)

        for i, changes in enumerate(num_pos):
            all_sims = []
            num_school_closures = []
            for index in indices:
                entry = json[index]
                pars = entry['pars']
                pars['end_day'] = '2020-10-02'
                pars['rand_seed'] = int(entry['index'])
                all_sims.append(cs.create_sim(pars=pars, num_pos=changes, test_prob=test_prob, trace_prob=trace_prob,
                                              NPI_schools=NPI_schools[i], label=schools_closure_scenarios[i]))

            msim = cv.MultiSim(sims=all_sims)
            msim.run(reseed=False, par_args={'maxload': 0.8}, noise=0.0, keep_people=False)
            msim.reduce()
            if do_save:
                cv.save(filename=f'msims/calibrated_{schools_closure_scenarios[i]}.msim', obj=msim)

        msims = []
        for i in schools_closure_scenarios:
            filename = f'msims/calibrated_{i}.msim'
            msims.append(cv.load(filename))
        sim_plots = cv.MultiSim.merge(msims, base=True)

        # school_results = dict()
        # for i, sim in enumerate(msims):
        #     if num_pos[i] is not None:
        #         school_results[schools_closure_scenarios[i]] = dict()
        #         if len(sim.sims) > 1:  # if running multiple param sets, print all of them
        #             school_results[schools_closure_scenarios[i]]['school_closures'] = []
        #             school_results[schools_closure_scenarios[i]]['cum_infections'] = []
        #             school_results[schools_closure_scenarios[i]]['num_tested'] = []
        #             school_results[schools_closure_scenarios[i]]['num_traced'] = []
        #             school_results[schools_closure_scenarios[i]]['school_days_lost'] = []
        #             school_results[schools_closure_scenarios[i]]['num_students'] = []
        #             school_results[schools_closure_scenarios[i]]['num_infectious'] = []
        #             school_results[schools_closure_scenarios[i]]['num_symptomatic'] = []
        #             school_results[schools_closure_scenarios[i]]['num_asymptomatic'] = []
        #             for j, sub_sim in enumerate(sim.sims):
        #                 num_students, num_asymp, num_symp = process_schools(sub_sim)
        #                 school_results[schools_closure_scenarios[i]]['num_students'].append(num_students)
        #                 school_results[schools_closure_scenarios[i]]['num_asymptomatic'].append(num_asymp)
        #                 school_results[schools_closure_scenarios[i]]['num_symptomatic'].append(num_symp)
        #                 school_results[schools_closure_scenarios[i]]['school_closures'].append(
        #                     sub_sim.school_info['school_closures'])
        #                 school_results[schools_closure_scenarios[i]]['cum_infections'].append(
        #                     sub_sim.summary['cum_infections'])
        #                 school_results[schools_closure_scenarios[i]]['num_tested'].append(
        #                     sub_sim.school_info['num_tested'])
        #                 school_results[schools_closure_scenarios[i]]['num_traced'].append(
        #                     sub_sim.school_info['num_traced'])
        #         else:
        #             for sub_sim in sim.sims:
        #                 num_students, num_asymp, num_symp = process_schools(sub_sim)
        #                 school_results[schools_closure_scenarios[i]]['num_students'] = num_students
        #                 school_results[schools_closure_scenarios[i]]['num_asymptomatic'] = num_asymp
        #                 school_results[schools_closure_scenarios[i]]['num_symptomatic'] = num_symp
        #                 school_results[schools_closure_scenarios[i]]['school_closures'] = sub_sim.school_info[
        #                     'school_closures']
        #                 school_results[schools_closure_scenarios[i]]['cum_infections'] = sub_sim.summary[
        #                     'cum_infections']
        #                 school_results[schools_closure_scenarios[i]]['num_tested'] = sub_sim.school_info['num_tested']
        #                 school_results[schools_closure_scenarios[i]]['num_traced'] = sub_sim.school_info['num_traced']
        #
        # csvfile = f'{analysis_name}_output.csv'
        # with open(csvfile, 'w') as f:
        #     for key in school_results.keys():
        #         f.write("%s,%s\n" % (key, school_results[key]))

        figname = analysis_name
        fig1 = sim_plots.plot(to_plot=['n_infectious'], do_show=False)
        for ax in fig1.axes:
            ax.set_xlim([200, 280])
            ax.set_ylim([0, 6000])
        fig1.savefig(f'infectious_{figname}_{date}.png')
        fig2 = sim_plots.plot(to_plot=['r_eff'], do_show=False)
        fig2.savefig(f'reff_{figname}_{date}.png')
        fig3 = sim_plots.plot(to_plot=['cum_infections'], do_show=False)
        for ax in fig3.axes:
            ax.set_xlim([200, 280])
            ax.set_ylim([60000, 100000])
        fig3.savefig(f'cuminfections_{figname}_{date}.png')

    else:
        msims = []
        for i in schools_closure_scenarios:
            filename = f'msims/calibrated_{i}.msim'
            msims.append(cv.load(filename))
        sim_plots = cv.MultiSim.merge(msims, base=True)
        # school_results = dict()
        # for i, sim in enumerate(msims):
        #     if num_pos[i] is not None:
        #         school_results[schools_closure_scenarios[i]] = dict()
        #         if len(sim.sims) > 1:  # if running multiple param sets, print all of them
        #             school_results[schools_closure_scenarios[i]]['school_closures'] = []
        #             school_results[schools_closure_scenarios[i]]['cum_infections'] = []
        #             school_results[schools_closure_scenarios[i]]['num_tested'] = []
        #             school_results[schools_closure_scenarios[i]]['num_traced'] = []
        #             school_results[schools_closure_scenarios[i]]['school_days_lost'] = []
        #             school_results[schools_closure_scenarios[i]]['num_students'] = []
        #             school_results[schools_closure_scenarios[i]]['num_infectious'] = []
        #             school_results[schools_closure_scenarios[i]]['num_symptomatic'] = []
        #             school_results[schools_closure_scenarios[i]]['num_asymptomatic'] = []
        #             for j, sub_sim in enumerate(sim.sims):
        #                 num_students, num_asymp, num_symp = process_schools(sub_sim)
        #                 school_results[schools_closure_scenarios[i]]['num_students'].append(num_students)
        #                 school_results[schools_closure_scenarios[i]]['num_asymptomatic'].append(num_asymp)
        #                 school_results[schools_closure_scenarios[i]]['num_symptomatic'].append(num_symp)
        #                 school_results[schools_closure_scenarios[i]]['school_closures'].append(
        #                     sub_sim.school_info['school_closures'])
        #                 school_results[schools_closure_scenarios[i]]['cum_infections'].append(
        #                     sub_sim.summary['cum_infections'])
        #                 school_results[schools_closure_scenarios[i]]['num_tested'].append(
        #                     sub_sim.school_info['num_tested'])
        #                 school_results[schools_closure_scenarios[i]]['num_traced'].append(
        #                     sub_sim.school_info['num_traced'])
        #         else:
        #             for sub_sim in sim.sims:
        #                 num_students, num_asymp, num_symp = process_schools(sub_sim)
        #                 school_results[schools_closure_scenarios[i]]['num_students'] = num_students
        #                 school_results[schools_closure_scenarios[i]]['num_asymptomatic'] = num_asymp
        #                 school_results[schools_closure_scenarios[i]]['num_symptomatic'] = num_symp
        #                 school_results[schools_closure_scenarios[i]]['school_closures'] = sub_sim.school_info[
        #                     'school_closures']
        #                 school_results[schools_closure_scenarios[i]]['cum_infections'] = sub_sim.summary[
        #                     'cum_infections']
        #                 school_results[schools_closure_scenarios[i]]['num_tested'] = sub_sim.school_info['num_tested']
        #                 school_results[schools_closure_scenarios[i]]['num_traced'] = sub_sim.school_info['num_traced']
        #
        # csvfile = f'{analysis_name}_output.csv'
        # with open(csvfile, 'w') as f:
        #     for key in school_results.keys():
        #         f.write("%s,%s\n"%(key,school_results[key]))

        figname = analysis_name
        fig1 = sim_plots.plot(to_plot=['n_infectious'], do_show=False)
        for ax in fig1.axes:
            ax.set_xlim([200, 249])
            ax.set_ylim([0, 10000])
        fig1.savefig(f'infectious_{figname}_{date}.png')

        fig2 = sim_plots.plot(to_plot=['r_eff'], do_show=False)
        fig2.savefig(f'reff_{figname}_{date}.png')

        # fig3 = sim_plots.plot(to_plot=['cum_infections'], do_show=False)
        # for ax in fig3.axes:
        #     ax.set_xlim([200, 280])
        #     ax.set_ylim([60000, 100000])
        # fig3.savefig(f'cuminfections_{figname}_{date}.png')


