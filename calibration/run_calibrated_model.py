'''Show optimized runs'''

import sciris as sc
from reopening_scenarios import create_sim as cs
from calibration import plot_calibration as pltcal
import covasim as cv

cv.check_save_version('1.4.7', die=True)

if __name__ == "__main__":

    rerun = True
    do_save = True
    do_plot = True
    n_reps = 20

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
            cv.save(filename='../reopening_scenarios/calibrated.msim', obj=msim)

    else:
        msim = cv.load('calibrated.msim')

    if do_plot:
        pltcal.plot_calibration(msim.sims, 'jun09-optuna', do_save=True)
