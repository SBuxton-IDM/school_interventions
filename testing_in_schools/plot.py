import covasim as cv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

pop_size = 1e5 # 2.25e4 2.25e5
msim = cv.MultiSim.load(f'msim_{int(pop_size)}.obj')

results = []
byschool = []
for sim in msim.sims:

    first_school_day = sim.day('2020-09-01')
    last_school_day = sim.day('2020-12-01')
    rdf = pd.DataFrame(sim.results)
    ret = {
        'key': sim.label,
        'inc': sim.dynamic_par['inc'],
        're': rdf['r_eff'].iloc[first_school_day:last_school_day, ].mean(axis=0),
        'cases': rdf['new_diagnoses'].iloc[(first_school_day-14):first_school_day, ].sum(axis=0) * 100e3 / (pop_size * sim.pars['pop_scale']) #2.25e6,
    }

    re_to_fit = sim.dynamic_par['re']
    cases_to_fit = sim.dynamic_par['inc']
    re_mismatch = (re_to_fit - ret['re'])**2 / re_to_fit**2
    cases_mismatch = (cases_to_fit - ret['cases'])**2 / cases_to_fit**2
    ret['mismatch'] = re_mismatch + cases_mismatch

    #if sim.label == 'all_remote': # and sim.dynamic_par['inc'] == 110:
    #    print(sim.label, sim.dynamic_par['inc'], ret['cases'], sim.dynamic_par['re'], ret['re'], ret['mismatch'])
    #    sim.plot()

    attack_students = []
    attack_teachersstaff = []

    attack_students_legacy = []
    attack_teachersstaff_legacy = []

    n_schools = {'es':0, 'ms':0, 'hs':0}
    n_schools_with_inf_d1 = {'es':0, 'ms':0, 'hs':0}
    inf_d1 = {'es':0, 'ms':0, 'hs':0} # TEMP
    for sid,stats in sim.school_stats.items():
        if stats['type'] not in ['es', 'ms', 'hs']:
            continue

        inf = stats['infectious']
        exp = stats['newly_exposed']
        cum_exp = {}
        num = 0
        for grp in ['students', 'teachers', 'staff']:
            cum_exp[grp] = np.cumsum(exp[grp])
            num += stats['num'][grp]

        attack_students.append( 100 * cum_exp['students'] / stats['num']['students'] )
        attack_teachersstaff.append( 100 * (cum_exp['teachers'] + cum_exp['staff']) / (stats['num']['teachers'] + stats['num']['staff']) )

        n_schools[stats['type']] += 1
        if inf['students'][first_school_day] + inf['teachers'][first_school_day] + inf['staff'][first_school_day] > 0:
            n_schools_with_inf_d1[stats['type']] += 1
            inf_d1[stats['type']] += inf['students'][first_school_day] + inf['teachers'][first_school_day] + inf['staff'][first_school_day]

        '''
        f = plt.figure(figsize=(16,10))
        import datetime as dt
        for grp in ['students', 'teachers', 'staff']:
            plt.plot(sim.results['date'], inf[grp], label=grp)
            plt.axvline(x=dt.datetime(2020, 9, 1), color = 'r')
        plt.show()
        '''

        # Legacy:
        aswi = stats['at_school_while_infectious']
        attack_students_legacy.append( 100 * aswi['students'] / stats['num']['students'] )
        attack_teachersstaff_legacy.append( 100 * (aswi['teachers']+aswi['staff']) / (stats['num']['teachers'] + stats['num']['staff']) )
        '''
        'n_students_at_school_while_infectious_first_day': self.n_students_at_school_while_infectious_first_day,
        'n_teacherstaff_at_school_while_infectious_first_day': self.n_teacherstaff_at_school_while_infectious_first_day,
        '''

        groups = ['students', 'teachers', 'staff']
        if sim.label == 'all_remote':
            byschool.append({
                'type': stats['type'],
                'inc': sim.dynamic_par['inc'],
                'size': sum([stats['num'][g] for g in groups]),
                'd1 infectious': sum([stats['infectious'][g][first_school_day] for g in groups]),
            })

    for stype in ['es', 'ms', 'hs']:
        ret[f'{stype}_perc_d1'] = 100 * n_schools_with_inf_d1[stype] / n_schools[stype]
        ret[f'{stype}_inf_d1'] = inf_d1[stype]
    ret['attack_students'] = np.mean(attack_students)
    ret['attack_teachersstaff'] = np.mean(attack_teachersstaff)

    ret['attack_students_legacy'] = np.mean(attack_students_legacy)
    ret['attack_teachersstaff_legacy'] = np.mean(attack_teachersstaff_legacy)


    print('-'*80)
    print(sim.label, sim.dynamic_par['inc'], ret['cases'], sim.dynamic_par['re'], ret['re'], ret['mismatch'])
    print(n_schools_with_inf_d1, n_schools)
    print(ret)

    results.append(ret)

df = pd.DataFrame(results)

# Attack rate
d = pd.melt(df, id_vars=['key', 'inc'], value_vars=['attack_students', 'attack_teachersstaff'], var_name='Group', value_name='Cum Inc (%)')
g = sns.FacetGrid(data=d, row='Group', height=4, aspect=3, row_order=['attack_teachersstaff', 'attack_students'])
g.map_dataframe( sns.barplot, x='key', y='Cum Inc (%)', hue='inc')

# Attack rate (legacy)
d = pd.melt(df, id_vars=['key', 'inc'], value_vars=['attack_students_legacy', 'attack_teachersstaff_legacy'], var_name='Group', value_name='Cum Inc (%)')
g = sns.FacetGrid(data=d, row='Group', height=4, aspect=3, row_order=['attack_teachersstaff_legacy', 'attack_students_legacy'])
g.map_dataframe( sns.barplot, x='key', y='Cum Inc (%)', hue='inc')
plt.suptitle('Legacy')


# Re
fig = plt.figure(figsize=(16,10))
sns.barplot(data=df, x='key', y='re', hue='inc')

# Percent of schools with infections on day 1
fig = plt.figure(figsize=(16,10))
extract = df.groupby(['key', 'inc'])['es_perc_d1', 'ms_perc_d1', 'hs_perc_d1'].mean().loc['as_normal'].reset_index()
melt = pd.melt(extract, id_vars=['inc'], value_vars=['es_perc_d1', 'ms_perc_d1', 'hs_perc_d1'], var_name='School Type', value_name='Schools with First-Day Infections')
sns.barplot(data=melt, x='School Type', y='Schools with First-Day Infections', hue='inc')
plt.legend()


bs = pd.DataFrame(byschool)
print(bs)
fig = plt.figure(figsize=(16,10))
g = sns.FacetGrid(data=bs, row='inc', height=4, aspect=3)
g.map_dataframe( sns.scatterplot, x='size', y='d1 infectious', hue='type')
plt.show()


mu = df.groupby(['key', 'inc']).mean()
print(mu)

plt.show()
