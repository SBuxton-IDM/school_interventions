import os
import numpy as np
import pandas as pd
import covasim as cv
import create_sim as cs
import sciris as sc
import matplotlib.pyplot as plt
from school_intervention import new_schools
from testing_scenarios import generate_scenarios, generate_testing

do_run = True

par_inds = (5,10) # First and last parameters to run
pop_size = 2.25e5 # 1e5 2.25e4 2.25e5
batch_size = 16

folder = 'v20201013_225k_v2'
stem = f'transtree_{par_inds[0]}-{par_inds[1]}_betaS=1.2_hybrid2w'
calibfile = os.path.join(folder, 'pars_cases_begin=75_cases_end=75_re=1.0_prevalence=0.002_yield=0.024_tests=225_pop_size=225000.json')

scenarios = generate_scenarios()
scenarios = {k:v for k,v in scenarios.items() if k in ['as_normal']} # as_normal, all_hybrid

testing = generate_testing()
testing = {k:v for k,v in testing.items() if k in ['None']} # None, PCR every 2w

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

                for st, cfg in scen.items():
                    if cfg is not None:
                        cfg['beta_s'] = 1.5 # Increase beta (multiplier) in schools from default of 0.6

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
                    msim.run(reseed=False, par_args={'ncpus': 16}, noise=0.0, keep_people=True)
                    sims = []

        for sim in msim.sims:
            sim.make_transtree(output=False)

    msim = cv.MultiSim.merge(msims)
    msim.save(os.path.join(folder, 'msims', f'{stem}.msim'), keep_people=True)
else:
    msim = cv.MultiSim.load(os.path.join(folder, 'msims', f'{stem}.msim'))


downstream_targets = {'es':0, 'ms':0, 'hs':0}
infected_schools = {'es':0, 'ms':0, 'hs':0}
for sim in msim.sims:
    tt = sim.results.transtree

    first = sim.day('2020-11-02')
    last = sim.day('2021-01-31')

    print(tt)
    df = pd.DataFrame(tt.infection_log)
    df['S.Student'] = [sim.people.student_flag[int(t)] if not np.isnan(t) else False for t in df['source']]
    df['T.Student'] = [sim.people.student_flag[t] for t in df['target']]
    print(dir(sim.people))
    pop = sim.people
    print(f'Pop has {sum(pop.student_flag)} students, {sum(pop.teacher_flag)} teachers, and {sum(pop.staff_flag)} staff')

    for st, sids in pop.school_types.items():
        if st in ['pk', 'uv']:
            continue

        for sid in sids:
            print(st, sid, '-'*80)
            uids = pop.schools[sid]
            # hs 54 [nan, nan, nan, nan, nan, nan, nan, 54.0, nan, 139.0, nan, nan, nan, nan, nan, 140.0, nan, nan, nan, 135.0, nan, nan, nan]

            #exp_date = [sim.people.date_exposed[u] for u in uids]
            df_sch = df.loc[
                (df['layer'].isin(['h', 's', 'w', 'c', sid])) & \
                (df['target'].isin(uids)) & \
                (df['date'] >= first)
            ]
            if df_sch.shape[0] > 0:
                print(df_sch)

                first_infected_in_sch = df_sch.iloc[0]['target']
                targets = df_sch.loc[df_sch['source'] == first_infected_in_sch]
                print(f'Individual {first_infected_in_sch} infected {len(targets)} others.')
                downstream_targets[st] += len(targets)
                infected_schools[st] +=1
            else:
                print(f'No individuals were infected after this school opened:', np.sum([sim.people.date_exposed[u] for u in uids if not sim.people.susceptible[u]]))


print(f'{infected_schools} schools had at least one infected individual after opening.')
dst = ifs = 0
for st in ['es', 'ms', 'hs']:
    print(f'R0 in {st} school: {downstream_targets[st]/infected_schools[st]}')
    dst += downstream_targets[st]
    ifs += infected_schools[st]
print(f'R0 overall: {dst/ifs}')

#sim.results.transtree.plot()
