import os
import pandas as pd
import seaborn as sns
import covasim as cv
import create_sim as cs
import sciris as sc
import matplotlib.pyplot as plt
import matplotlib as mplt
from school_intervention import new_schools
from testing_scenarios import generate_scenarios, generate_testing

# Global plotting styles
font_size = 16
font_style = 'Roboto Condensed'
mplt.rcParams['font.size'] = font_size
mplt.rcParams['font.family'] = font_style

do_run = False

par_inds = (0,20) # First and last parameters to run
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
    for start_date in ['None', '2020-10-26', '2020-10-27', '2020-10-28', '2020-10-29', '2020-10-30', '2020-10-31', '2020-11-01', '2020-11-02']:
        t = sc.dcp(test)
        if start_date == 'None':
            t[0]['start_date'] = '2022-01-01' # Move into the deep future
        else:
            t[0]['start_date'] = start_date

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
        '''
        msim = cv.MultiSim.load(os.path.join(folder, 'msims', f'{stem}.msim'))
        msim_None1 = cv.MultiSim.load(os.path.join(folder, 'msims', 'batch_0-15_with_countermeasures.msim'))
        msim_None2 = cv.MultiSim.load(os.path.join(folder, 'msims', 'batch_15-30_with_countermeasures.msim'))
        sims = msim.sims
        sims += [s for s in msim_None1.sims if s.key2 == 'None']
        sims += [s for s in msim_None2.sims if s.key2 == 'None']
        msim = cv.MultiSim(sims)
        print('saving')
        msim.save('pcr.msim')
        '''
        msim = cv.MultiSim.load('pcr.msim')

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
    fig, ax = plt.subplots(figsize=(12,8))
    for key, dat in d.groupby('key2'):
        c = 'k' if key == 'None' else None
        sns.regplot(data=dat, x='n_students', y='d1 bool', logistic=True, y_jitter=0.03, scatter_kws={'s':5}, label=key, ax=ax, ci=None, scatter=False, color=c)
    ax.set_xlabel('School size (students)')
    ax.set_ylabel('Infection on First Day (%)')
    yt = [0.0, 0.25, 0.50, 0.75]
    ax.set_yticks(yt)
    ax.set_yticklabels([int(100*t) for t in yt])
    ax.grid(True)

    lmap = {
        'None':'No PCR testing',
        '2020-10-26': 'One week prior',
        '2020-10-27': 'Six days prior',
        '2020-10-28': 'Five days prior',
        '2020-10-29': 'Four days prior',
        '2020-10-30': 'Three days prior',
        '2020-10-31': 'Two days prior',
        '2020-11-01': 'One day prior',
        '2020-11-02': 'On the first day of school'
    }

    handles, labels = ax.get_legend_handles_labels()
    handles = [handles[-1]] + handles[:-1]
    labels = [lmap[labels[-1]]] + [lmap[l] for l in labels[:-1]]

    ax.legend(handles, labels)
    plt.tight_layout()
    cv.savefig(os.path.join(imgdir, 'PCR_Days_Sweep.png'), dpi=300)

    fig.tight_layout()

