import os
import covasim as cv
import create_sim as cs
import sciris as sc
import matplotlib.pyplot as plt
from school_intervention import new_schools
from testing_scenarios import generate_scenarios, generate_testing

do_run = False

par_inds = (0,5) # First and last parameters to run
pop_size = 2.25e5 # 1e5 2.25e4 2.25e5
batch_size = 16

folder = 'v20201013_225k_v2'
stem = f'calib_remote_notest_{par_inds[0]}-{par_inds[1]}'
calibfile = os.path.join(folder, 'pars_cases_begin=75_cases_end=75_re=1.0_prevalence=0.002_yield=0.024_tests=225_pop_size=225000.json')

if __name__ == '__main__':
    scenarios = generate_scenarios()
    scenarios = {k:v for k,v in scenarios.items() if k in ['all_remote']}

    testing = generate_testing()
    testing = {k:v for k,v in testing.items() if k in ['None']}

    par_list = sc.loadjson(calibfile)[par_inds[0]:par_inds[1]]

    if do_run:
        sims = []
        msims = []
        tot = len(scenarios) * len(testing) * len(par_list)
        proc = 0
        for skey, scen in scenarios.items():
            for tidx, (tkey, test) in enumerate(testing.items()):
                for eidx, entry in enumerate(par_list):
                    par = sc.dcp(entry['pars'])
                    par['rand_seed'] = int(entry['index'])
                    sim = cs.create_sim(par, pop_size=pop_size, folder=folder)

                    sim.label = f'{skey} + {tkey}'
                    sim.key1 = skey
                    sim.key2 = tkey
                    sim.scen = scen
                    sim.tscen = test
                    sim.dynamic_par = par

                    # Modify scen with test
                    this_scen = sc.dcp(scen)
                    for stype, spec in this_scen.items():
                        if spec is not None:
                            spec['testing'] = sc.dcp(test) # dcp probably not needed because deep copied in new_schools

                    ns = new_schools(this_scen)
                    sim['interventions'] += [ns]
                    sims.append(sim)
                    proc += 1

                    if len(sims) == batch_size or proc == tot:# or (tidx == len(testing)-1 and eidx == len(par_list)-1):
                        print(f'Running sims {proc-len(sims)}-{proc-1} of {tot}')
                        msim = cv.MultiSim(sims)
                        msims.append(msim)
                        msim.run(reseed=False, par_args={'ncpus': 16}, noise=0.0, keep_people=False)
                        sims = []

            print(f'*** Saving after completing {skey}')
            sims_this_scenario = [s for msim in msims for s in msim.sims if s.key1 == skey]
            msim = cv.MultiSim(sims_this_scenario)

        msim = cv.MultiSim.merge(msims)
        msim.save(os.path.join(folder, 'msims', f'{stem}.msim'), keep_people=False)
    else:
        msim = cv.MultiSim.load(os.path.join(folder, 'msims', f'{stem}.msim'))

    # Calib plotting

    sims = [s for s in msim.sims if s.key1=='all_remote' and s.key2=='None']
    ms = cv.MultiSim(sims)

    ms.reduce()
    #ms.plot(to_plot='overview')

    #plt.figure()
    to_plot = sc.odict({
            'New Infections': [
                'new_infections',
            ],
            'New Diagnoses per 100k': [
                'new_diagnoses',
            ],
            'Test Yield': [
                'test_yield',
            ],
            'Effective Reproduction Number': [
                'r_eff',
            ],
            'New Tests': [
                'new_tests',
            ],
            'Prevalence': [
                'prevalence',
            ],
        })
    fig = plt.figure(figsize=(16,10))
    ms.plot(to_plot=to_plot, n_cols=2, interval=30, legend_args={'show_legend':False}, do_show=False, fig=fig) # , dateformat='%B'

    s0 = ms.sims[0]
    for i, ax in enumerate(fig.axes):
        if i < len(fig.axes)-2:
            ax.xaxis.set_visible(False)
        ax.axvline(x=s0.day('2020-11-01'), color='c', ls='--')

    # Agh, x-axis is not a datetime!
    #import matplotlib.dates as mdates
    #months = mdates.MonthLocator(interval=1)  # every month
    #fig.axes[-1].xaxis.set_major_locator(months)

    #from matplotlib.dates import DateFormatter
    #date_form = DateFormatter('%B')#"%m-%d")
    #fig.axes[-1].xaxis.set_major_formatter(date_form)

    fig.tight_layout()
    cv.savefig(os.path.join(folder, 'img', f'calibration_{int(pop_size)}.png'))

