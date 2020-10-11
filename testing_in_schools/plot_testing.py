import os
import covasim as cv
import covasim.misc as cvm
import numpy as np
import pandas as pd
import matplotlib as mplt
import matplotlib.pyplot as plt
import seaborn as sns

# Global plotting styles
font_size = 16
font_style = 'Roboto Condensed'
# font_style = 'Barlow Condensed'
# font_style = 'Source Sans Pro'
mplt.rcParams['font.size'] = font_size
mplt.rcParams['font.family'] = font_style

pop_size = 1e5 # 2.25e4 2.25e5
msim = cv.MultiSim.load(os.path.join('msims', f'testing_{int(pop_size)}.msim'))

re_to_fit = 1.0
cases_to_fit = 75
debug_plot = False

results = []
byschool = []
groups = ['students', 'teachers', 'staff']

scen_names = {
    'as_normal': 'As Normal',
    'all_remote': 'All Remote',
    'with_screening': 'Normal\nwith Screening',
    'all_hybrid': 'All Hybrid',
}

for sim in msim.sims:
    first_school_day = sim.day('2020-09-01')
    last_school_day = sim.day('2020-12-01')
    rdf = pd.DataFrame(sim.results)
    ret = {
        'key1': sim.key1,
        #'label1': scen_names[sim.key1] if sim.key1 in scen_names else sim.key1,
        'key2': sim.key2,
        're': rdf['r_eff'].iloc[first_school_day:last_school_day, ].mean(axis=0),
        'cases': rdf['new_diagnoses'].iloc[(first_school_day-14):first_school_day, ].sum(axis=0) * 100e3 / (pop_size * sim.pars['pop_scale']) #2.25e6,
    }

    re_mismatch = (re_to_fit - ret['re'])**2 / re_to_fit**2
    cases_mismatch = (cases_to_fit - ret['cases'])**2 / cases_to_fit**2
    ret['mismatch'] = re_mismatch + cases_mismatch


    #if sim.label == 'all_remote': # and sim.dynamic_par['inc'] == 110:
    #    print(sim.label, sim.dynamic_par['inc'], ret['cases'], sim.dynamic_par['re'], ret['re'], ret['mismatch'])
    #    sim.plot()

    attackrate_students = []
    attackrate_teachersstaff = []

    attackrate_students_legacy = []
    attackrate_teachersstaff_legacy = []

    n_schools = {'es':0, 'ms':0, 'hs':0}
    n_schools_with_inf_d1 = {'es':0, 'ms':0, 'hs':0}
    inf_d1 = {'es':0, 'ms':0, 'hs':0} # TEMP

    perc_inperson_days_lost = {g:[] for g in groups}
    for sid,stats in sim.school_stats.items():
        if stats['type'] not in ['es', 'ms', 'hs']:
            continue

        inf = stats['infectious']
        inf_at_sch = stats['infectious_at_school']
        in_person = stats['in_person']
        exp = stats['newly_exposed']
        num_school_days = stats['num_school_days']
        n_exp = {}
        for grp in groups:
            n_exp[grp] = np.sum(exp[grp])
            in_person_days = np.sum(in_person[grp])
            scheduled_person_days = num_school_days * stats['num'][grp]
            perc_inperson_days_lost[grp].append(
                100*(scheduled_person_days - in_person_days)/scheduled_person_days if scheduled_person_days > 0 else 100
            )

        attackrate_students.append( 100 * n_exp['students'] / stats['num']['students'] )
        attackrate_teachersstaff.append( 100 * (n_exp['teachers'] + n_exp['staff']) / (stats['num']['teachers'] + stats['num']['staff']) )

        n_schools[stats['type']] += 1
        if inf_at_sch['students'][first_school_day] + inf_at_sch['teachers'][first_school_day] + inf_at_sch['staff'][first_school_day] > 0:
            n_schools_with_inf_d1[stats['type']] += 1
            inf_d1[stats['type']] += inf_at_sch['students'][first_school_day] + inf_at_sch['teachers'][first_school_day] + inf_at_sch['staff'][first_school_day]

        if debug_plot and sim.key2 != 'None' and sum([inf_at_sch[g][first_school_day] for g in groups]) > 0:
            f = plt.figure(figsize=(16,10))
            import datetime as dt
            for grp in ['students', 'teachers', 'staff']:
                #plt.plot(sim.results['date'], inf[grp], label=grp)
                plt.plot(sim.results['date'], inf_at_sch[grp], ls='-', label=f'{grp} at sch')
                plt.plot(sim.results['date'], at_home[grp], ls=':', label=f'{grp} at home')
                plt.axvline(x=dt.datetime(2020, 9, 1), color = 'r')
            plt.title(sim.label)
            plt.legend()
            plt.show()

        # Legacy:
        aswi = stats['at_school_while_infectious']
        attackrate_students_legacy.append( 100 * aswi['students'] / stats['num']['students'] )
        attackrate_teachersstaff_legacy.append( 100 * (aswi['teachers']+aswi['staff']) / (stats['num']['teachers'] + stats['num']['staff']) )

        if sim.key1 == 'as_normal':
            byschool.append({
                'type': stats['type'],
                'key1': sim.key1,
                'key2': sim.key2,
                'size': sum([stats['num'][g] for g in groups]),
                'd1 infectious': sum([inf_at_sch[g][first_school_day] for g in groups]),
            })

    #ret['Days at Home'] = sum(

    for stype in ['es', 'ms', 'hs']:
        ret[f'{stype}_perc_d1'] = 100 * n_schools_with_inf_d1[stype] / n_schools[stype]
        ret[f'{stype}_inf_d1'] = inf_d1[stype]

    ret['attackrate_students'] = np.mean(attackrate_students)
    ret['attackrate_teachersstaff'] = np.mean(attackrate_teachersstaff)

    ret['attackrate_students_legacy'] = np.mean(attackrate_students_legacy)
    ret['attackrate_teachersstaff_legacy'] = np.mean(attackrate_teachersstaff_legacy)

    for g in groups:
        ret[f'perc_inperson_days_lost_{g}'] = np.mean(perc_inperson_days_lost[g])

    results.append(ret)

df = pd.DataFrame(results)

# Attack rate
d = pd.melt(df, id_vars=['key1', 'key2'], value_vars=['attackrate_students', 'attackrate_teachersstaff'], var_name='Group', value_name='Cum Inc (%)')
d.replace( {'Group': {'attackrate_students': 'Students', 'attackrate_teachersstaff': 'Teachers & Staff'}}, inplace=True)
g = sns.FacetGrid(data=d, row='Group', height=4, aspect=3, row_order=['Teachers & Staff', 'Students'], legend_out=False)
g.map_dataframe( sns.barplot, x='key1', y='Cum Inc (%)', hue='key2')
g.add_legend()
g.set_titles(row_template="{row_name}")
xtl = g.axes[1,0].get_xticklabels()
xtl = [l.get_text() for l in xtl]
g.set(xticklabels=[scen_names[k] if k in scen_names else k for k in xtl])
g.set_axis_labels(y_var="Attack Rate")
plt.tight_layout()

# Attack rate (legacy)
d = pd.melt(df, id_vars=['key1', 'key2'], value_vars=['attackrate_students_legacy', 'attackrate_teachersstaff_legacy'], var_name='Group', value_name='Cum Inc (%)')
g = sns.FacetGrid(data=d, row='Group', height=4, aspect=3, row_order=['attackrate_teachersstaff_legacy', 'attackrate_students_legacy'])
g.map_dataframe( sns.barplot, x='key1', y='Cum Inc (%)', hue='key2')
plt.suptitle('Legacy')
g.add_legend()


# Frac days in-person
d = pd.melt(df, id_vars=['key1', 'key2'], value_vars=[f'perc_inperson_days_lost_{g}' for g in groups], var_name='Group', value_name='Days lost (%)')
d.replace( {'Group': {f'perc_inperson_days_lost_{g}':g.capitalize() for g in groups}}, inplace=True)
g = sns.FacetGrid(data=d, row='Group', height=4, aspect=3, row_order=['Teachers', 'Staff', 'Students'], legend_out=False)
g.map_dataframe( sns.barplot, x='key1', y='Days lost (%)', hue='key2')
g.add_legend()
g.set_titles(row_template="{row_name}")
xtl = g.axes[2,0].get_xticklabels()
xtl = [l.get_text() for l in xtl]
#g.set(xticklabels=[scen_names[k] if k in scen_names else k for k in xtl])
g.set_axis_labels(y_var="Days lost (%)")
plt.tight_layout()


# Re
fig, ax = plt.subplots(figsize=(16,10))
sns.barplot(data=df, x='key1', y='re', hue='key2')
ax.set_ylim([0.9, 1.2])
ax.set_ylabel(r'$R_e$')

# Percent of schools with infections on day 1
fig = plt.figure(figsize=(16,10))
extract = df.groupby(['key1', 'key2'])['es_perc_d1', 'ms_perc_d1', 'hs_perc_d1'].mean().loc['as_normal'].reset_index()
melt = pd.melt(extract, id_vars=['key2'], value_vars=['es_perc_d1', 'ms_perc_d1', 'hs_perc_d1'], var_name='School Type', value_name='Schools with First-Day Infections')
sns.barplot(data=melt, x='School Type', y='Schools with First-Day Infections', hue='key2')
plt.legend()

'''
bs = pd.DataFrame(byschool)
g = sns.FacetGrid(data=bs, row='key2', height=4, aspect=3)
g.map_dataframe( sns.scatterplot, x='size', y='d1 infectious', hue='type')
g.add_legend()
'''

mu = df.groupby(['key1', 'key2']).mean()
print(mu)

plt.show()
