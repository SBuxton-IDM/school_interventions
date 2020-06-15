'''Show optimized runs'''

import sciris as sc
from reopening_scenarios import create_sim as cs
from calibration import plot_calibration as pltcal
import covasim as cv

cv.check_save_version('1.4.7', die=True)

if __name__ == "__main__":

    rerun = False
    do_save = True
    do_plot = True
    n_reps = 20
    date = '2020-06-12'

    if rerun:
        indices = range(n_reps)
        jsonfile = 'optimization_v12_safegraph_060920.json'
        json = sc.loadjson(jsonfile)

        all_sims = []
        for index in indices:
            entry = json[index]
            pars = entry['pars']
            pars['rand_seed'] = int(entry['index'])
            all_sims.append(cs.create_sim(pars=pars))

        msim = cv.MultiSim(sims=all_sims)
        msim.run(reseed=False, par_args={'maxload': 0.8}, noise=0.0, keep_people=False)
        msim.reduce()
        if do_save:
            cv.save(filename='../calibration/calibrated.msim', obj=msim)

    else:
        msim = cv.load('calibrated.msim')

    if do_plot:

        for interv in msim.base_sim['interventions']:
            interv.do_plot = False

        sim_plots = cv.MultiSim.merge(msim, base=True)
        fig1 = sim_plots.plot(to_plot=['new_infections', 'new_diagnoses'], do_show=False)
        fig1.savefig(f'infectious_{date}.png')
        # sim_plots.plot(do_show=True)

        pltcal.plot_calibration(msim.sims, 'jun11-optuna', do_save=True)
