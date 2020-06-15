'''Show optimized runs'''

import sciris as sc
from reopening_scenarios import create_sim as cs
import covasim as cv

cv.check_save_version('1.4.7', die=True)

if __name__ == "__main__":

    rerun = True
    do_save = True
    n_reps = 10
    date = '06152020'

    schools_closure_scenarios = ['close_on_1', 'close_on_5', 'close_on_10']
    num_pos = [1, 5, 10]

    # schools_closure_scenarios = ['close_on_10']
    # num_pos = [10]

    if rerun:
        indices = range(n_reps)
        jsonfile = 'optimization_v12_safegraph_061120.json'
        json = sc.loadjson(jsonfile)

        for i, changes in enumerate(num_pos):
            all_sims = []
            num_school_closures = []
            for index in indices:
                entry = json[index]
                pars = entry['pars']
                pars['end_day'] = '2020-11-30'
                pars['rand_seed'] = int(entry['index'])
                # pars['n_imports'] = 100
                all_sims.append(cs.create_sim(pars=pars, num_pos=changes, label=schools_closure_scenarios[i]))

            msim = cv.MultiSim(sims=all_sims)
            msim.run(reseed=False, par_args={'maxload': 0.8}, noise=0.0, keep_people=False)
            msim.reduce()
            if do_save:
                cv.save(filename=f'calibrated_{schools_closure_scenarios[i]}.msim', obj=msim)

        msims = []
        for i in schools_closure_scenarios:
            filename = f'calibrated_{i}.msim'
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

    else:

        msims = []
        for i in schools_closure_scenarios:
            filename = f'calibrated_{i}.msim'
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
