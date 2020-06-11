'''Show optimized runs'''

import sciris as sc
from . import create_sim as cs
import covasim as cv

cv.check_save_version('1.4.7', die=True)

if __name__ == "__main__":

    rerun = True
    do_save = True
    n_reps = 10
    date = '06102020'

    schools_closure_scenarios = ['no_trigger', 'close_on_diagnosis_trace', 'close_on_diagnosis_notrace',
                                 'close_on_symptoms_or_diagnosis_trace', 'close_on_symptoms_or_diagnosis_notrace']
    school_closures = [False, True, True, True, True]
    ili_prev = [None, None, None, 0.1, 0.1]
    num_pos = 2
    trace = [False, True, False, True, False]
    condition = [None, 'diagnosed', 'diagnosed', 'symptomatic', 'symptomatic']

    # schools_closure_scenarios = ['close_on_symptoms_or_diagnosis_notrace']
    # school_closures = [True]
    # ili_prev = [ 0.1]
    # num_pos = 1
    # trace = [False]
    # condition = ['symptomatic']

    if rerun:
        indices = range(n_reps)
        jsonfile = 'optimization_v12_safegraph_060920.json'
        json = sc.loadjson(jsonfile)

        for i, changes in enumerate(school_closures):
            all_sims = []
            num_school_closures = []
            for index in indices:
                entry = json[index]
                pars = entry['pars']
                pars['end_day'] = '2020-10-30'
                pars['rand_seed'] = int(entry['index'])
                pars['n_imports'] = 10
                all_sims.append(cs.create_sim(pars=pars, school_closure=changes,  num_pos=num_pos, trace=trace[i], iliprev=ili_prev[i],
                                              condition=condition[i], label=schools_closure_scenarios[i]))

            msim = cv.MultiSim(sims=all_sims)
            msim.run(reseed=False, par_args={'maxload': 0.8}, noise=0.0, keep_people=False)
            num_school_closures.append(msim.base_sim.school_closures)
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
