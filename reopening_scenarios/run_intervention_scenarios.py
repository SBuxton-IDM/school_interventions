'''Show optimized runs'''

import sciris as sc
from reopening_scenarios import create_sim as cs
import covasim as cv

cv.check_save_version('1.4.7', die=True)

if __name__ == "__main__":

    rerun = True
    do_save = True
    n_reps = 4
    date = '06192020'

    # analysis_name = 'closeon10_varytestprob_atschool'
    # analysis_name = 'closeon10_varytestprob_athome'
    # analysis_name = 'closeon10_varytraceprob_atschool'
    # analysis_name = 'closeon10_varytraceprob_athome'
    # analysis_name = 'varyclosenum_test20percSP_test10home_trace20percSP_trace10home'
    analysis_name = 'varyclosenum_test20percSP_test10home_trace10percSP_trace10home'

    schools_closure_scenarios = ['closeon100_test20percSP_test10home_trace10percSP_trace10home',
                                 'closeon10_test20percSP_test10home_trace10percSP_trace10home',
                                 'closeon2_test20percSP_test10home_trace10percSP_trace10home']
    num_pos = [100, 10, 2]
    test_prob = [.2, .1] #screenpos, athome
    trace_prob = [.1, .1]  # screenpos, athome

    # schools_closure_scenarios = ['closeon10_test50percSP_test25home_trace100percSP_trace25home',
    #                              'closeon10_test50percSP_test25home_trace50percSP_trace25home',
    #                              'closeon10_test50percSP_test25home_trace25percSP_trace25home']
    # num_pos = 10
    # test_prob = [.5, .25]
    # trace_prob = [[1, .25], [.5, .25], [.25, .25]]


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
                pars['end_day'] = '2020-11-01'
                pars['rand_seed'] = int(entry['index'])
                all_sims.append(cs.create_sim(pars=pars, num_pos=changes, test_prob=test_prob, trace_prob=trace_prob,
                                              label=schools_closure_scenarios[i]))

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

        school_results = dict()
        for i, sim in enumerate(msims):
            school_results[schools_closure_scenarios[i]] = dict()
            if len(sim.sims)> 1: # if running multiple param sets, print all of them
                school_results[schools_closure_scenarios[i]]['school_closures'] = []
                school_results[schools_closure_scenarios[i]]['cum_infections'] = []
                school_results[schools_closure_scenarios[i]]['num_tested'] = []
                school_results[schools_closure_scenarios[i]]['num_traced'] = []
                for j, sub_sim in enumerate(sim.sims):
                    school_results[schools_closure_scenarios[i]]['school_closures'].append(sub_sim.school_info['school_closures'])
                    school_results[schools_closure_scenarios[i]]['cum_infections'].append(sub_sim.summary['cum_infections'])
                    school_results[schools_closure_scenarios[i]]['num_tested'].append(sub_sim.school_info['num_tested'])
                    school_results[schools_closure_scenarios[i]]['num_traced'].append(sub_sim.school_info['num_traced'])

            else:
                for sub_sim in sim.sims:
                    school_results[schools_closure_scenarios[i]]['school_closures'] = sub_sim.school_info['school_closures']
                    school_results[schools_closure_scenarios[i]]['cum_infections'] = sub_sim.summary['cum_infections']
                    school_results[schools_closure_scenarios[i]]['num_tested'] = sub_sim.school_info['num_tested']
                    school_results[schools_closure_scenarios[i]]['num_traced'] = sub_sim.school_info['num_traced']

        csvfile = f'{analysis_name}_output.csv'
        with open(csvfile, 'w') as f:
            for key in school_results.keys():
                f.write("%s,%s\n" % (key, school_results[key]))

        figname = analysis_name
        fig1 = sim_plots.plot(to_plot=['n_infectious'], do_show=False)
        for ax in fig1.axes:
            ax.set_xlim([200, 280])
            ax.set_ylim([0, 6000])
        fig1.savefig(f'infectious_{figname}_{date}.png')
        # fig2 = sim_plots.plot(to_plot=['r_eff'], do_show=False)
        # fig2.savefig(f'reff_{figname}_{date}.png')
        # fig3 = sim_plots.plot(to_plot=['cum_infections'], do_show=False)
        # for ax in fig3.axes:
        #     ax.set_xlim([200, 280])
        #     ax.set_ylim([60000, 100000])
        # fig3.savefig(f'cuminfections_{figname}_{date}.png')

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
                for j, sub_sim in enumerate(sim.sims):
                    school_results[schools_closure_scenarios[i]]['school_closures'].append(
                        sub_sim.school_info['school_closures'])
                    school_results[schools_closure_scenarios[i]]['cum_infections'].append(
                        sub_sim.summary['cum_infections'])
                    school_results[schools_closure_scenarios[i]]['num_tested'].append(sub_sim.school_info['num_tested'])
                    school_results[schools_closure_scenarios[i]]['num_traced'].append(sub_sim.school_info['num_traced'])

            else:
                for sub_sim in sim.sims:
                    school_results[schools_closure_scenarios[i]]['school_closures'] = sub_sim.school_info[
                        'school_closures']
                    school_results[schools_closure_scenarios[i]]['cum_infections'] = sub_sim.summary['cum_infections']
                    school_results[schools_closure_scenarios[i]]['num_tested'] = sub_sim.school_info['num_tested']
                    school_results[schools_closure_scenarios[i]]['num_traced'] = sub_sim.school_info['num_traced']

        csvfile = f'{analysis_name}_output.csv'
        with open(csvfile, 'w') as f:
            for key in school_results.keys():
                f.write("%s,%s\n"%(key,school_results[key]))

        figname = analysis_name
        fig1 = sim_plots.plot(to_plot=['n_infectious'], do_show=False)
        for ax in fig1.axes:
            ax.set_xlim([200, 280])
            ax.set_ylim([0, 6000])
        fig1.savefig(f'infectious_{figname}_{date}.png')

        # fig2 = sim_plots.plot(to_plot=['r_eff'], do_show=False)
        # fig2.savefig(f'reff_{figname}_{date}.png')
        #
        # fig3 = sim_plots.plot(to_plot=['cum_infections'], do_show=False)
        # for ax in fig3.axes:
        #     ax.set_xlim([200, 280])
        #     ax.set_ylim([60000, 100000])
        # fig3.savefig(f'cuminfections_{figname}_{date}.png')
