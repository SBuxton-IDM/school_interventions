import os
import pandas as pd
import seaborn as sns
import covasim as cv
import create_sim as cs
import sciris as sc
import matplotlib.pyplot as plt
from school_intervention import new_schools
from testing_scenarios import generate_scenarios, generate_testing

do_run = True

par_inds = (0,10) # First and last parameters to run
pop_size = 2.25e5 # 1e5 2.25e4 2.25e5
batch_size = 24

folder = 'v20201015_225k'
imgdir = os.path.join(folder, 'img')
stem = f'pcr_days_sweep_{par_inds[0]}-{par_inds[1]}'
calibfile = os.path.join(folder, 'pars_cases_begin=75_cases_end=75_re=1.0_prevalence=0.002_yield=0.024_tests=225_pop_size=225000.json')

if __name__ == '__main__':
    scenarios = generate_scenarios()
    scenarios = {k:v for k,v in scenarios.items() if k in ['with_countermeasures']}

    test = generate_testing()['PCR 1w prior']

    testing = {}
    for start_date in ['2020-10-26', '2020-10-27', '2020-10-28', '2020-10-29', '2020-10-30', '2020-10-31', '2020-11-01', '2020-11-02']:
        t = sc.dcp(test)
        t[0]['start_date'] = start_date
        t[0]['delay'] = 0

        testing[start_date] = t

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
                            #spec['beta_s'] = 1.5 # Shouldn't matter considering schools are closed in the 'all_remote' scenario

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

    byschool = []
    groups = ['students', 'teachers', 'staff']
    for sim in msim.sims:
        # Note: The objective function has recently changed, so mismatch will not match!
        first_school_day = sim.day('2020-11-02')
        last_school_day = sim.day('2021-01-31')
        for sid,stats in sim.school_stats.items():
            if stats['type'] not in ['es', 'ms', 'hs']:
                continue

            inf_at_sch = stats['infectious_stay_at_school'] # stats['infectious_arrive_at_school'] stats['infectious_stay_at_school']

            byschool.append({
                'type': stats['type'],
                'key1': sim.key1, # Filtered to just one scenario (key1)
                'key2': sim.key2,
                'n_students': stats['num']['students'], #sum([stats['num'][g] for g in groups]),
                'd1 infectious': sum([inf_at_sch[g][first_school_day] for g in groups]),
                'd1 bool': sum([inf_at_sch[g][first_school_day] for g in groups]) > 0,
            })


    d = pd.DataFrame(byschool)
    #d.replace( {'type': {'es':'Elementary', 'ms':'Middle', 'hs':'High'}}, inplace=True)
    #d.replace( {'key2': {'PCR one week prior, 1d delay':'PCR one week prior', 'Daily PCR, no delay':'PCR one day prior'}}, inplace=True)
    ###g = sns.FacetGrid(data=d, row='key2', height=3, aspect=3.5, margin_titles=False)#, row_order=['None', 'PCR one week prior', 'PCR one day prior']) # row='type'
    ###g.map_dataframe( sns.regplot, x='n_students', y='d1 bool', logistic=True, y_jitter=0.03, scatter_kws={'color':'black', 's':5}, ax=ax)
    fig, ax = plt.subplots(figsize=(12,8))
    for key, dat in d.groupby('key2'):
        sns.regplot(data=dat, x='n_students', y='d1 bool', logistic=True, y_jitter=0.03, scatter_kws={'s':5}, label=key, ax=ax)
    plt.legend()
    #g.set_titles(col_template="{col_name}", row_template="{row_name}")
    #g.set_axis_labels(x_var='School size (students)', y_var='Infection on First Day (%)')
    #for ax in g.axes.flat:
    #    yt = [0.0, 0.25, 0.50, 0.75, 1.0]
    #    ax.set_yticks(yt)
    #    ax.set_yticklabels([int(100*t) for t in yt])
    #    ax.grid(True)
    #g.add_legend(fontsize=14)
    plt.tight_layout()
    cv.savefig(os.path.join(imgdir, 'PCR_Days_Sweep.png'), dpi=300)

    fig.tight_layout()

