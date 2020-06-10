'''Show optimized runs'''

import sciris as sc
from reopening_scenarios import create_sim as cs
import covasim as cv

cv.check_save_version('1.4.7', die=True)

if __name__ == "__main__":

    rerun = True
    do_save = True
    n_reps = 10

    schools_closure_scenarios = ['no_trigger', 'close_school_on_diagnosis', 'close_school_on_symptoms_10percILI']
    school_closures = [False, True, True]
    ili_prev = [None, None, 0.1]
    num_pos = 2
    condition = [None, 'diagnosed', 'symptomatic']

    # schools_closure_scenarios = ['no_trigger', 'close_school_on_diagnosis']
    # school_closures = [False, True]
    # ili_prev = [None, None]
    # num_pos = 2
    # condition = [None, 'diagnosed']

    if rerun:
        indices = range(n_reps)
        jsonfile = 'optimization_v12_safegraph_060920.json'
        json = sc.loadjson(jsonfile)

        for i, changes in enumerate(school_closures):
            all_sims = []
            for index in indices:
                entry = json[index]
                pars = entry['pars']
                pars['rand_seed'] = int(entry['index'])
                all_sims.append(cs.create_sim_scenarios(pars=pars, school_closure=changes,  num_pos=num_pos, iliprev=ili_prev[i],
                                              condition=condition[i], label=schools_closure_scenarios[i]))

            msim = cv.MultiSim(sims=all_sims)
            msim.run(reseed=False, par_args={'maxload': 0.8}, noise=0.0, keep_people=False)
            msim.reduce()
            if do_save:
                cv.save(filename=f'calibrated_{schools_closure_scenarios[i]}.msim', obj=msim)

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
        fig1.savefig(f'infectious_{figname}.png')
        fig2 = sim_plots.plot(to_plot=['r_eff'], do_show=False)
        fig2.savefig(f'reff_{figname}.png')
