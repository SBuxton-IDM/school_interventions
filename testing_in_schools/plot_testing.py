# Main script to generate plots from scenario simulations.  Sims are saved into the msim folder of the respective analysis folder, e.g. v20201013. Often we distribute computing by seeds, generating several *.msim files, which are combined here before plotting.

import os
import covasim as cv
import covasim.misc as cvm
import numpy as np
import pandas as pd
import matplotlib as mplt
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
from calibrate_model import evaluate_sim

# Global plotting styles
font_size = 16
font_style = 'Roboto Condensed'
mplt.rcParams['font.size'] = font_size
mplt.rcParams['font.family'] = font_style

pop_size = 2.25e5 # 1e5 2.25e4 2.25e5

folder = 'v20201013_225k_v2'
imgdir = os.path.join(folder, 'img')
debug_plot = False


def load_single(fn):
    return cv.MultiSim.load(fn)

def load_multi(fns, cachefn=None):
    # Load/combine *.msim objects into a single MultiSim for analysis
    msims = []
    for fn in fns:
        msims.append(cv.MultiSim.load(fn))
    msim = cv.MultiSim.merge(msims)

    if cachefn is not None:
        msim.save(cachefn)
    return msim

def load_and_replace(fn1, scenarios_to_remove, fn2):
    # TODO: WIP
    msim = cv.MultiSim.load(os.path.join(folder, 'msims', f'testing_not_remote_{int(pop_size)}.msim'))
    print(len(msim.sims))
    # Replace "all_remote" sims with update
    remote = cv.MultiSim.load(os.path.join(folder, 'msims', f'testing_remote_{int(pop_size)}.msim'))
    sims = [s for s in msim.sims if s.key1 != 'all_remote'] + remote.sims
    msim = cv.MultiSim(sims)
    print(len(msim.sims))
    msim.save(os.path.join(folder, 'msims', f'testing_v20201012_{int(pop_size)}.msim'))

cachefn = os.path.join(folder, 'msims', 'combined4.msim')
msim = load_single(cachefn)
#fns = [os.path.join(folder, 'msims', fn) for fn in ['combined3.msim', 'pars4_k5_0-20.msim']]
#msim = load_multi(fns, cachefn)

results = []
byschool = []
groups = ['students', 'teachers', 'staff']

scen_names = { # key1
    'as_normal': 'As Normal',
    'with_countermeasures': 'Normal with\nCountermeasures',
    'all_hybrid': 'Hybrid with\nCountermeasures',
    'k5': 'K-5 In-Person\nOthers Remote',
    'all_remote': 'All Remote',
}
scen_order = [
    'as_normal',
    'with_countermeasures',
    'all_hybrid',
    'k5',
    'all_remote',
]

test_names = { # key2
    'None': 'None',
    'PCR 1w prior': 'PCR one week prior, 1d delay',
    'Antigen every 1w teach&staff': 'Weekly antigen for teachers & staff, no delay',
    'PCR every 2w': 'Fortnightly PCR, 1d delay',
    'PCR every 1w': 'Weekly PCR, 1d delay',
    'PCR every 1d': 'Daily PCR, no delay',
    'PCR every 2w 50%': 'Fortnightly PCR, 50% coverage',
    'PCR every 1m 15%': 'Monthly PCR, 15% coverage',
    'Antigen every 1w': 'Weekly antigen for all, no delay',
}

for sim in msim.sims:
    sim.key2 = test_names[sim.key2]

hue_order = [test_names[x] for x in [
    'None',
    'PCR 1w prior',
    #'PCR every 1m 15%',
    'Antigen every 1w teach&staff',
    'PCR every 2w 50%',
    'PCR every 2w',
    'PCR every 1w',
    'Antigen every 1w',
    'PCR every 1d',
]]

for sim in msim.sims:
    # Note: The objective function has recently changed, so mismatch will not match!
    first_school_day = sim.day('2020-11-02')
    last_school_day = sim.day('2021-01-31')
    rdf = pd.DataFrame(sim.results)
    ret = {
        'key1': sim.key1,
        'key2': sim.key2,
    }

    stats = evaluate_sim(sim)
    ret.update(stats)

    n_schools = {'es':0, 'ms':0, 'hs':0}
    n_schools_with_inf_d1 = {'es':0, 'ms':0, 'hs':0}

    grp_dict = {'Students': ['students'], 'Teachers & Staff': ['teachers', 'staff']}
    perc_inperson_days_lost = {k:[] for k in grp_dict.keys()}
    attackrate = {k:[] for k in grp_dict.keys()}

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
            in_person_days = scheduled_person_days = num_exposed = num_people = 0
            for grp in grps:
                in_person_days += np.sum(in_person[grp])
                scheduled_person_days += num_school_days * stats['num'][grp]
                num_exposed += n_exp[grp]
                num_people += stats['num'][grp]
            perc_inperson_days_lost[gkey].append(
                100*(scheduled_person_days - in_person_days)/scheduled_person_days if scheduled_person_days > 0 else 100
            )
            attackrate[gkey].append( 100 * num_exposed / num_people)

        n_schools[stats['type']] += 1
        if inf_at_sch['students'][first_school_day] + inf_at_sch['teachers'][first_school_day] + inf_at_sch['staff'][first_school_day] > 0:
            n_schools_with_inf_d1[stats['type']] += 1

        if debug_plot and sim.key1=='as_normal' and sim.key2 == 'None':# and sum([inf_at_sch[g][first_school_day] for g in groups]) > 0:
            f = plt.figure(figsize=(16,10))
            for grp in ['students', 'teachers', 'staff']:
                #plt.plot(sim.results['date'], inf[grp], label=grp)
                plt.plot(sim.results['date'], stats['infectious_arrive_at_school'][grp], ls='-', label=f'{grp} arrived')
                plt.plot(sim.results['date'], stats['infectious_stay_at_school'][grp], ls=':', label=f'{grp} stayed')
                #plt.plot(sim.results['date'], at_home[grp], ls=':', label=f'{grp} at home')
                plt.axvline(x=dt.datetime(2020, 11, 2), color = 'r')
            plt.title(sim.label)
            plt.legend()
            plt.show()

        d1scenario = 'as_normal'
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

    for gkey in grp_dict.keys():
        ret[f'perc_inperson_days_lost_{gkey}'] = np.mean(perc_inperson_days_lost[gkey])
        ret[f'attackrate_{gkey}'] = np.mean(attackrate[gkey])

    results.append(ret)

df = pd.DataFrame(results)

# Attack rate
for name in ['all', 'no_normal']:
    d = pd.melt(df, id_vars=['key1', 'key2'], value_vars=[f'attackrate_{gkey}' for gkey in grp_dict.keys()], var_name='Group', value_name='Cum Inc (%)')
    d.replace( {'Group': {f'attackrate_{gkey}':gkey for gkey in grp_dict.keys()}}, inplace=True)

    so = scen_order
    if name == 'no_normal':
        d = d.loc[d['key1']!='as_normal'] # Remove normal
        so = so[1:]

    g = sns.FacetGrid(data=d, row='Group', height=4, aspect=3, row_order=['Teachers & Staff', 'Students'], legend_out=False)

    g.map_dataframe( sns.barplot, x='key1', y='Cum Inc (%)', hue='key2', hue_order=hue_order, order=so)
    if name == 'all':
        g.add_legend()
    g.set_titles(row_template="{row_name}")
    xtl = g.axes[1,0].get_xticklabels()
    xtl = [l.get_text() for l in xtl]
    g.set(xticklabels=[scen_names[k] if k in scen_names else k for k in xtl])
    g.set_axis_labels(y_var="3-Month Attack Rate (%)")
    plt.tight_layout()
    cv.savefig(os.path.join(imgdir, f'3mAttackRate_{name}.png'), dpi=300)

# Frac in-person days lost
d = pd.melt(df, id_vars=['key1', 'key2'], value_vars=[f'perc_inperson_days_lost_{gkey}' for gkey in grp_dict.keys()], var_name='Group', value_name='Days lost (%)')
d.replace( {'Group': {f'perc_inperson_days_lost_{gkey}':gkey for gkey in grp_dict.keys()}}, inplace=True)
g = sns.FacetGrid(data=d, row='Group', height=4, aspect=3, row_order=['Teachers & Staff', 'Students'], legend_out=False)
g.map_dataframe( sns.barplot, x='key1', y='Days lost (%)', hue='key2', hue_order=hue_order, order=scen_order, palette='Reds')
g.add_legend()
g.set_titles(row_template="{row_name}", fontsize=24)
xtl = g.axes[1,0].get_xticklabels()
xtl = [l.get_text() for l in xtl]
g.set(xticklabels=[scen_names[k] if k in scen_names else k for k in xtl])
g.set_axis_labels(y_var="Days lost (%)")
plt.tight_layout()
cv.savefig(os.path.join(imgdir, '3mInPersonDaysLost.png'), dpi=300)

# Re
fig, ax = plt.subplots(figsize=(12,8))
sns.barplot(data=df, x='key1', y='re', hue='key2', hue_order=hue_order, order=scen_order)
ax.set_ylim([0.8, 1.45])
ax.set_ylabel(r'Average $R_e$')
ax.set_xlabel('')
xtl = ax.get_xticklabels()
xtl = [l.get_text() for l in xtl]
ax.set_xticklabels([scen_names[k] if k in scen_names else k for k in xtl])
ax.axhline(y=1, color='k', ls=':', lw=2)
plt.legend().set_title('')
plt.tight_layout()
cv.savefig(os.path.join(imgdir, '3mAverageRe.png'), dpi=300)

# Percent of schools with infections on day 1
fig = plt.figure(figsize=(12,8))
extract = df.groupby(['key1', 'key2'])[['es_perc_d1', 'ms_perc_d1', 'hs_perc_d1']].mean().loc[d1scenario].reset_index()
melt = pd.melt(extract, id_vars=['key2'], value_vars=['es_perc_d1', 'ms_perc_d1', 'hs_perc_d1'], var_name='School Type', value_name='Schools with First-Day Infections')
sns.barplot(data=melt, x='School Type', y='Schools with First-Day Infections', hue='key2')
plt.legend()
plt.tight_layout()
cv.savefig(os.path.join(imgdir, 'SchoolsWithFirstDayInfections.png'), dpi=300)

# Infections on first day as function on school type and testing - regression
d = pd.DataFrame(byschool)
d.replace( {'type': {'es':'Elementary', 'ms':'Middle', 'hs':'High'}}, inplace=True)
d.replace( {'key2': {'PCR one week prior, 1d delay':'PCR one week prior', 'Daily PCR, no delay':'PCR one day prior'}}, inplace=True)
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

# Save mean to CSV
df.groupby(['key1', 'key2']).mean().to_csv(os.path.join(imgdir, 'Mean.csv'))

#plt.show()