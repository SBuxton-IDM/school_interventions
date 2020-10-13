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

imgdir = 'img_v20201013_v1_filterseeds'
#msim = cv.MultiSim.load(os.path.join('msims', f'testing_v20201013_v1_{int(pop_size)}.msim'))
msim = cv.MultiSim.load(os.path.join('msims', f'testing_v20201013_v1_filterseeds_{int(pop_size)}.msim'))

'''
msim = cv.MultiSim.merge([
    cv.MultiSim.load(os.path.join('msims', f'testing_v20201013_v1a_{int(pop_size)}.msim')),
    cv.MultiSim.load(os.path.join('msims', f'testing_v20201013_v1b_{int(pop_size)}.msim')),
    cv.MultiSim.load(os.path.join('msims', f'testing_v20201013_v1c_{int(pop_size)}.msim')),
    cv.MultiSim.load(os.path.join('msims', f'testing_v20201013_v1d_{int(pop_size)}.msim')),
    cv.MultiSim.load(os.path.join('msims', f'testing_v20201013_v1e_{int(pop_size)}.msim')),
])
msim.save(os.path.join('msims', f'testing_v20201013_v1_{int(pop_size)}.msim'))
'''

'''
msim = cv.MultiSim.load(os.path.join('msims', f'testing_not_remote_{int(pop_size)}.msim'))
print(len(msim.sims))
# Replace "all_remote" sims with update
remote = cv.MultiSim.load(os.path.join('msims', f'testing_remote_{int(pop_size)}.msim'))
sims = [s for s in msim.sims if s.key1 != 'all_remote'] + remote.sims
msim = cv.MultiSim(sims)
print(len(msim.sims))
msim.save(os.path.join('msims', f'testing_v20201012_{int(pop_size)}.msim'))
'''


re_to_fit = 1.0
cases_to_fit = 75
debug_plot = False

results = []
byschool = []
groups = ['students', 'teachers', 'staff']

scen_names = {
    'as_normal': 'As Normal',
    'all_remote': 'All Remote',
    'with_screening': 'Normal with\nNPI & Screening',
    'all_hybrid': 'All Hybrid',
}

for sim in msim.sims:
    first_school_day = sim.day('2020-11-02')
    last_school_day = sim.day('2021-01-31')
    rdf = pd.DataFrame(sim.results)
    ret = {
        'key1': sim.key1,
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

    n_schools = {'es':0, 'ms':0, 'hs':0}
    n_schools_with_inf_d1 = {'es':0, 'ms':0, 'hs':0}
    inf_d1 = {'es':0, 'ms':0, 'hs':0} # TEMP

    grp_dict = {'Students': ['students'], 'Teachers & Staff': ['teachers', 'staff']}
    perc_inperson_days_lost = {k:[] for k in grp_dict.keys()}

    for sid,stats in sim.school_stats.items():
        if stats['type'] not in ['es', 'ms', 'hs']:
            continue

        inf = stats['infectious']
        inf_at_sch = stats['infectious_stay_at_school'] # stats['infectious_arrive_at_school'] stats['infectious_stay_at_school']
        in_person = stats['in_person']
        exp = stats['newly_exposed']
        num_school_days = stats['num_school_days']
        n_exp = {}
        for grp in groups:
            n_exp[grp] = np.sum(exp[grp])

        for gkey, grps in grp_dict.items():
            in_person_days = scheduled_person_days = 0
            for grp in grps:
                in_person_days += np.sum(in_person[grp])
                scheduled_person_days += num_school_days * stats['num'][grp]
            perc_inperson_days_lost[gkey].append(
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
                plt.axvline(x=dt.datetime(2020, 11, 2), color = 'r')
            plt.title(sim.label)
            plt.legend()
            plt.show()

        d1scenario = 'all_remote'
        if sim.key1 == d1scenario:
            byschool.append({
                'type': stats['type'],
                'key1': sim.key1, # Filtered to just one scenario (key1)
                'key2': sim.key2,
                'n_students': stats['num']['students'], #sum([stats['num'][g] for g in groups]),
                'd1 infectious': sum([inf_at_sch[g][first_school_day] for g in groups]),
                'd1 bool': sum([inf_at_sch[g][first_school_day] for g in groups]) > 0,
            })

    for stype in ['es', 'ms', 'hs']:
        ret[f'{stype}_perc_d1'] = 100 * n_schools_with_inf_d1[stype] / n_schools[stype]
        ret[f'{stype}_inf_d1'] = inf_d1[stype]

    ret['attackrate_students'] = np.mean(attackrate_students)
    ret['attackrate_teachersstaff'] = np.mean(attackrate_teachersstaff)

    for gkey in grp_dict.keys():
        ret[f'perc_inperson_days_lost_{gkey}'] = np.mean(perc_inperson_days_lost[gkey])

    results.append(ret)

df = pd.DataFrame(results)

# Attack rate
d = pd.melt(df, id_vars=['key1', 'key2'], value_vars=['attackrate_students', 'attackrate_teachersstaff'], var_name='Group', value_name='Cum Inc (%)')
d.replace( {'Group': {'attackrate_students': 'Students', 'attackrate_teachersstaff': 'Teachers & Staff'}}, inplace=True)
g = sns.FacetGrid(data=d, row='Group', height=4, aspect=3, row_order=['Teachers & Staff', 'Students'], legend_out=False)
g.map_dataframe( sns.barplot, x='key1', y='Cum Inc (%)', hue='key2', hue_order=['None', 'PCR 1w prior', 'PCR every 1m 15%', 'Antigen every 1w teach&staff', 'PCR every 2w', 'PCR every 1w', 'PCR every 1d'])
g.add_legend()
g.set_titles(row_template="{row_name}")
xtl = g.axes[1,0].get_xticklabels()
xtl = [l.get_text() for l in xtl]
g.set(xticklabels=[scen_names[k] if k in scen_names else k for k in xtl])
g.set_axis_labels(y_var="3-Month Attack Rate (%)")
plt.tight_layout()
cv.savefig(os.path.join(imgdir, '3mAttackRate.png'))

# Frac in-person days lost
d = pd.melt(df, id_vars=['key1', 'key2'], value_vars=[f'perc_inperson_days_lost_{gkey}' for gkey in grp_dict.keys()], var_name='Group', value_name='Days lost (%)')
print(d)
d.replace( {'Group': {f'perc_inperson_days_lost_{gkey}':gkey for gkey in grp_dict.keys()}}, inplace=True)
g = sns.FacetGrid(data=d, row='Group', height=4, aspect=3, row_order=['Teachers & Staff', 'Students'], legend_out=False)
g.map_dataframe( sns.barplot, x='key1', y='Days lost (%)', hue='key2', hue_order=['None', 'PCR 1w prior', 'PCR every 1m 15%', 'Antigen every 1w teach&staff', 'PCR every 2w', 'PCR every 1w', 'PCR every 1d'], palette='Reds')
g.add_legend()
g.set_titles(row_template="{row_name}", fontsize=24)
xtl = g.axes[1,0].get_xticklabels()
xtl = [l.get_text() for l in xtl]
g.set(xticklabels=[scen_names[k] if k in scen_names else k for k in xtl])
g.set_axis_labels(y_var="Days lost (%)")
plt.tight_layout()
cv.savefig(os.path.join(imgdir, '3mInPersonDaysLost.png'))


# Re
fig, ax = plt.subplots(figsize=(16,10))
sns.barplot(data=df, x='key1', y='re', hue='key2', hue_order=['None', 'PCR 1w prior', 'PCR every 1m 15%', 'Antigen every 1w teach&staff', 'PCR every 2w', 'PCR every 1w', 'PCR every 1d'])
ax.set_ylim([0.8, 1.2])
ax.set_ylabel(r'Average $R_e$')
ax.set_xlabel('')
xtl = ax.get_xticklabels()
xtl = [l.get_text() for l in xtl]
ax.set_xticklabels([scen_names[k] if k in scen_names else k for k in xtl])
ax.axhline(y=1, color='k', ls=':', lw=2)
plt.legend().set_title('')
plt.tight_layout()
cv.savefig(os.path.join(imgdir, '3mAverageRe.png'))

# Percent of schools with infections on day 1
fig = plt.figure(figsize=(16,10))
extract = df.groupby(['key1', 'key2'])[['es_perc_d1', 'ms_perc_d1', 'hs_perc_d1']].mean().loc[d1scenario].reset_index()
melt = pd.melt(extract, id_vars=['key2'], value_vars=['es_perc_d1', 'ms_perc_d1', 'hs_perc_d1'], var_name='School Type', value_name='Schools with First-Day Infections')
sns.barplot(data=melt, x='School Type', y='Schools with First-Day Infections', hue='key2')
plt.legend()
plt.tight_layout()
cv.savefig(os.path.join(imgdir, 'SchoolsWithFirstDayInfections.png'))

# Infections on first day as function on school type and testing - regression
d = pd.DataFrame(byschool)
d.replace( {'type': {'es':'Elementary', 'ms':'Middle', 'hs':'High'}}, inplace=True)
d.replace( {'key2': {'PCR every 1w':'PCR one week prior', 'PCR every 1d':'PCR one day prior'}}, inplace=True)
g = sns.FacetGrid(data=d, row='key2', height=3, aspect=3.5, margin_titles=False, row_order=['None', 'PCR one week prior', 'PCR one day prior']) # row='type'
g.map_dataframe( sns.regplot, x='n_students', y='d1 bool', logistic=True, y_jitter=0.03, scatter_kws={'color':'black', 's':5})
g.set_titles(col_template="{col_name}", row_template="{row_name}")
g.set_axis_labels(x_var='School size (students)', y_var='Infection on First Day (%)')
for ax in g.axes.flat:
    yt = [0.0, 0.25, 0.50, 0.75, 1.0]
    ax.set_yticks(yt)
    ax.set_yticklabels([int(100*t) for t in yt])
    ax.grid(True)
g.add_legend()
plt.tight_layout()
cv.savefig(os.path.join(imgdir, 'FirstDayInfectionsReg.png'), dpi=300)


mu = df.groupby(['key1', 'key2']).mean()
print(mu)

plt.show()
