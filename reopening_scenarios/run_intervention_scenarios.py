'''Show optimized runs'''

import sciris as sc
from reopening_scenarios import create_sim as cs
import covasim as cv

cv.check_save_version('1.4.7', die=True)

if __name__ == "__main__":

    rerun = True
    do_save = True
    n_reps = 1
    date = '06172020'

    schools_closure_scenarios = ['closeon100_test75percSP_test50home', 'closeon100_test50percSP_test25home', 'closeon100_test20percSP_test10home',
                                 'closeon5_test75percSP_test50home', 'closeon5_test50percSP_test25home', 'closeon5_test20percSP_test10home']
    num_pos = [100, 100, 100, 5, 5, 5]
    test_prob = [[.75, .5], [.5, .25], [.2, .1], [.75, .5], [.5, .25], [.2, .1],] #screenpos, athome

    # schools_closure_scenarios = ['closeon100_test25percSP_test10home']
    # num_pos = [100]
    # test_prob = [[.25, .1]]  # screenpos, athome


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
                all_sims.append(cs.create_sim(pars=pars, num_pos=changes, test_prob=test_prob[i],
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


        figname = 'school_closure'
        fig1 = sim_plots.plot(to_plot=['n_infectious'], do_show=False)
        # for ax in fig1.axes:
        #     ax.set_xlim([200, 305])
        #     ax.set_ylim([0, 4000])
        fig1.savefig(f'infectious_{figname}_{date}.png')
        fig2 = sim_plots.plot(to_plot=['r_eff'], do_show=False)
        fig2.savefig(f'reff_{figname}_{date}.png')
        fig3 = sim_plots.plot(to_plot=['cum_infections'], do_show=False)
        fig3.savefig(f'cuminfections_{figname}_{date}.png')

        school_results = dict()
        for i, sim in enumerate(msims):
            school_results[schools_closure_scenarios[i]] = dict()
            for j, sub_sim in enumerate(sim.sims):
                school_results[schools_closure_scenarios[i]]['school_closures'] = sub_sim.school_info['school_closures']
                school_results[schools_closure_scenarios[i]]['cum_infections'] = sub_sim.summary['cum_infections']
                school_results[schools_closure_scenarios[i]]['total_schools'] = sub_sim.school_info['num_schools']
                school_results[schools_closure_scenarios[i]]['school_closures'] = sub_sim.school_info['school_closures'] * 14

        csvfile = 'school_closure_output.csv'
        with open(csvfile, 'w') as f:
            for key in school_results.keys():
                f.write("%s,%s\n" % (key, school_results[key]))

    else:
        msims = []
        for i in schools_closure_scenarios:
            filename = f'msims/calibrated_{i}.msim'
            msims.append(cv.load(filename))
        sim_plots = cv.MultiSim.merge(msims, base=True)
        school_results = dict()
        for i, sim in enumerate(msims):
            school_results[schools_closure_scenarios[i]] = dict()
            for j, sub_sim in enumerate(sim.sims):
                school_results[schools_closure_scenarios[i]]['school_closures'] = sub_sim.school_info['school_closures']
                school_results[schools_closure_scenarios[i]]['cum_infections'] = sub_sim.summary['cum_infections']
                school_results[schools_closure_scenarios[i]]['total_schools'] = sub_sim.school_info['num_schools']
                school_results[schools_closure_scenarios[i]]['days_closed'] = sub_sim.school_info['num_schools']*14

        csvfile = 'school_closure_output.csv'
        with open(csvfile, 'w') as f:
            for key in school_results.keys():
                f.write("%s,%s\n"%(key,school_results[key]))


        figname = 'school_closure'
        fig1 = sim_plots.plot(to_plot=['n_infectious'], do_show=True)
        fig1.show()
        # for ax in fig1.axes:
        #     ax.set_xlim([200, 305])
        #     ax.set_ylim([0, 4000])
        fig1.savefig(f'infectious_{figname}_{date}.png')
        fig2 = sim_plots.plot(to_plot=['r_eff'], do_show=False)
        fig2.savefig(f'reff_{figname}_{date}.png')

        fig3 = sim_plots.plot(to_plot=['cum_infections'], do_show=False)
        fig3.savefig(f'cuminfections_{figname}_{date}.png')
