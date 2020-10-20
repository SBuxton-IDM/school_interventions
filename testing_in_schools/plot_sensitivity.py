# Main workhorse script to generate plots from scenario simulations.  Sims are saved into the msim folder of the respective analysis folder, e.g. v20201013. Often we distribute computing by seeds, generating several *.msim files, which are combined here before plotting.

import os
import covasim as cv
import sciris as sc
import covasim.misc as cvm
import numpy as np
import pandas as pd
import matplotlib as mplt
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
from calibrate_model import evaluate_sim
from pathlib import Path

# Global plotting styles
font_size = 16
font_style = 'Roboto Condensed'
mplt.rcParams['font.size'] = font_size
mplt.rcParams['font.family'] = font_style

pop_size = 2.25e5 # 1e5 2.25e4 2.25e5

folder = 'v20201016_225k_sensitivity'
variant = '_v2'
cachefn = os.path.join(folder, 'msims', 'batch_v2_0-1.msim')
debug_plot = False

imgdir = os.path.join(folder, 'img'+variant)
Path(imgdir).mkdir(parents=True, exist_ok=True)


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
    exit()
    msim = cv.MultiSim.load(os.path.join(folder, 'msims', f'testing_not_remote_{int(pop_size)}.msim'))
    print(len(msim.sims))
    # Replace "all_remote" sims with update
    remote = cv.MultiSim.load(os.path.join(folder, 'msims', f'testing_remote_{int(pop_size)}.msim'))
    sims = [s for s in msim.sims if s.key1 != 'all_remote'] + remote.sims
    msim = cv.MultiSim(sims)
    print(len(msim.sims))
    msim.save(os.path.join(folder, 'msims', f'testing_v20201012_{int(pop_size)}.msim'))


print(f'loading {cachefn}')
#msim = load_single(cachefn)
msim = load_multi([os.path.join(folder, 'msims', fn) for fn in [
    'batch_v2_0-1_baseline.msim',
    'batch_v2_0-1_children_equally_sus.msim',
    #'batch_v2_0-1_lower_sens_spec.msim',
]], None)

results = []
byschool = []
groups = ['students', 'teachers', 'staff']

scen_names = sc.odict({ # key1
    'as_normal': 'As Normal',
    'with_countermeasures': 'Normal with\nCountermeasures',
    'all_hybrid': 'Hybrid with\nCountermeasures',
    'k5': 'K-5 In-Person\nOthers Remote',
    'all_remote': 'All Remote',
})
scen_order = scen_names.values()

test_names = sc.odict({ # key2
    'None': 'None',
    'PCR 1w prior': 'PCR one week prior, 1d delay',
    'Antigen every 1w teach&staff, PCR f/u': 'Weekly antigen for teachers & staff, PCR f/u',
    #'PCR every 2w 50%': 'Fortnightly PCR, 50% coverage',
    'PCR every 2w': 'Fortnightly PCR, 1d delay',
    'Antigen every 2w, no f/u': 'Fortnightly antigen, no f/u',
    'Antigen every 2w, PCR f/u': 'Fortnightly antigen, PCR f/u',
    'PCR every 1w': 'Weekly PCR, 1d delay',

    #'PCR every 1m 15%': 'Monthly PCR, 15% coverage',
    #'Antigen every 1w teach&staff, PCR f/u': 'Weekly antigen for teachers & staff, no delay, PCR f/u',
    #'Antigen every 1w, PCR f/u': 'Weekly antigen for all, no delay, PCR f/u',
    #'Antigen every 1w, no f/u': 'Weekly antigen for all, no delay, no f/u',
    'PCR every 1d': 'Daily PCR, no delay',
})
test_order = test_names.values()
test_hue = {
    'None':                                         'gray',
    'PCR one week prior, 1d delay':                 (0.8584083044982699, 0.9134486735870818, 0.9645674740484429, 1.0),
    'Weekly antigen for teachers & staff, PCR f/u': (0.9882352941176471, 0.732072279892349, 0.6299269511726259, 1.0),
    'Fortnightly PCR, 50% coverage':                (0.7309496347558632, 0.8394771241830065, 0.9213225682429834, 1.0),
    'Fortnightly PCR, 1d delay':                    (0.5356862745098039, 0.746082276047674, 0.8642522106881968, 1.0),
    'Fortnightly antigen, PCR f/u':                 (0.7925720876585928, 0.09328719723183392, 0.11298731257208766, 1.0),
    'Fortnightly antigen, no f/u':                  (0.9835755478662053, 0.4127950788158401, 0.28835063437139563, 1.0),
    'Weekly PCR, 1d delay':                         (0.32628988850442137, 0.6186236063052672, 0.802798923490965, 1.0),
    'Daily PCR, no delay':                          (0.16696655132641292, 0.48069204152249134, 0.7291503267973857, 1.0),
}

sens_names = sc.odict({ # key3
    'baseline': 'Basline',
    'children_equally_sus': 'Children equally susceptible',
})
sens_order = sens_names.values()


for sim in msim.sims:
    sim.key2 = test_names[sim.key2] if sim.key2 in test_names else sim.key2


tests = []
for sim in msim.sims:
    first_school_day = sim.day('2020-11-02')
    last_school_day = sim.day('2021-01-31')
    ret = {
        'key1': sim.key1,
        'key2': sim.key2,
        'key3': sim.key3,
    }

    perf = evaluate_sim(sim)
    ret.update(perf)

    n_schools = {'es':0, 'ms':0, 'hs':0}
    n_schools_with_inf_d1 = {'es':0, 'ms':0, 'hs':0}

    grp_dict = {'Students': ['students'], 'Teachers & Staff': ['teachers', 'staff']}
    perc_inperson_days_lost = {k:[] for k in grp_dict.keys()}
    attackrate = {k:[] for k in grp_dict.keys()}
    count = {k:0 for k in grp_dict.keys()}
    exposed = {k:0 for k in grp_dict.keys()}
    inperson_days = {k:0 for k in grp_dict.keys()}
    possible_days = {k:0 for k in grp_dict.keys()}

    first_date = '2020-11-02'
    first = sim.day(first_date)
    last_date = '2021-01-31'
    last = sim.day(last_date)
    #tests.append([sim.key1, sim.key2, np.sum(sim.results['new_tests'][first:last])])
    #tests.append([sim.key1, sim.key2, sim.results['new_tests']]) # [first:last]

    for sid,stats in sim.school_stats.items():
        if stats['type'] not in ['es', 'ms', 'hs']:
            continue

        inf = stats['infectious']
        inf_at_sch = stats['infectious_stay_at_school'] # stats['infectious_arrive_at_school'] stats['infectious_stay_at_school']
        in_person = stats['in_person']
        exp = stats['newly_exposed']
        num_school_days = stats['num_school_days']
        possible_school_days = np.busday_count(first_date, last_date)
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

            exposed[gkey] += n_exp[grp]
            count[gkey] += stats['num'][grp]
            inperson_days[gkey] += in_person_days
            possible_days[gkey] += possible_school_days*num_people

        n_schools[stats['type']] += 1
        if inf_at_sch['students'][first_school_day] + inf_at_sch['teachers'][first_school_day] + inf_at_sch['staff'][first_school_day] > 0:
            n_schools_with_inf_d1[stats['type']] += 1

        if debug_plot and sim.key1=='as_normal' and sim.key2 == 'None':# and sum([inf_at_sch[g][first_school_day] for g in groups]) > 0:
            f = plt.figure(figsize=(12,8))
            for grp in ['students', 'teachers', 'staff']:
                #plt.plot(sim.results['date'], inf[grp], label=grp)
                plt.plot(sim.results['date'], stats['infectious_arrive_at_school'][grp], ls='-', label=f'{grp} arrived')
                plt.plot(sim.results['date'], stats['infectious_stay_at_school'][grp], ls=':', label=f'{grp} stayed')
                #plt.plot(sim.results['date'], at_home[grp], ls=':', label=f'{grp} at home')
                plt.axvline(x=dt.datetime(2020, 11, 2), color = 'r')
            plt.title(sim.label)
            plt.legend()
            plt.show()

        byschool.append({
            'sid': sid,
            'type': stats['type'],
            'key1': sim.key1, # Filtered to just one scenario (key1)
            'key2': sim.key2,
            'key3': sim.key3,
            'n_students': stats['num']['students'], #sum([stats['num'][g] for g in groups]),
            'n': sum([stats['num'][g] for g in groups]),
            'd1 infectious': sum([inf_at_sch[g][first_school_day] for g in groups]),
            'd1 bool': sum([inf_at_sch[g][first_school_day] for g in groups]) > 0,
            'PCR': stats['n_tested']['PCR'],
            'Antigen': stats['n_tested']['Antigen'],
            'Days': last_school_day - first_school_day,
            'Pop*Scale': sim.pars['pop_size']*sim.pars['pop_scale'],
        })

    for stype in ['es', 'ms', 'hs']:
        ret[f'{stype}_perc_d1'] = 100 * n_schools_with_inf_d1[stype] / n_schools[stype]

    # Deciding between district and school perspective here
    for gkey in grp_dict.keys():
        ret[f'perc_inperson_days_lost_{gkey}'] = 100*(possible_days[gkey]-inperson_days[gkey])/possible_days[gkey] #np.mean(perc_inperson_days_lost[gkey])
        ret[f'attackrate_{gkey}'] = 100*exposed[gkey] / count[gkey] #np.mean(attackrate[gkey])
        ret[f'count_{gkey}'] = np.sum(count[gkey])

    results.append(ret)

df = pd.DataFrame(results)
'''
d = pd.DataFrame(byschool)
print( d.groupby('key2')[['PCR', 'Antigen']].mean() )
tests = pd.DataFrame(tests, columns=['Scen', 'Testing', 'Tests'])
col = {
    'Antigen every 2w, PCR f/u': 'r',
    'Weekly PCR, 1d delay': 'b',
    'None': 'k',
}

f,ax = plt.subplots()
for i,t in tests.iterrows():
    ax.plot(t['Tests'], color=col[t['Testing']], marker='.', lw=0)
plt.show()
'''


# Attack rate
d = pd.melt(df, id_vars=['key1', 'key2', 'key3'], value_vars=[f'attackrate_{gkey}' for gkey in grp_dict.keys()], var_name='Group', value_name='Cum Inc (%)')
d.replace( {'Group': {f'attackrate_{gkey}':gkey for gkey in grp_dict.keys()}}, inplace=True)
print(d)
g = sns.FacetGrid(data=d, row='Group', col='key1', height=4, aspect=3, row_order=['Teachers & Staff', 'Students'], legend_out=False)

g.map_dataframe( sns.barplot, x='key2', y='Cum Inc (%)', hue='key3')#, hue_order=test_order, order=sens_order, palette=test_hue)
g.add_legend(fontsize=14)

g.set_titles(row_template="{row_name}")
#xtl = g.axes[1,0].get_xticklabels()
#xtl = [l.get_text() for l in xtl]
#g.set(xticklabels=[scen_names[k] if k in scen_names else k for k in xtl])
g.set_axis_labels(y_var="3-Month Attack Rate (%)")
plt.tight_layout()
cv.savefig(os.path.join(imgdir, f'3mAttackRate.png'), dpi=300)

plt.show()
exit()

# Frac in-person days lost
d = pd.melt(df, id_vars=['key1', 'key2'], value_vars=[f'perc_inperson_days_lost_{gkey}' for gkey in grp_dict.keys()], var_name='Group', value_name='Days lost (%)')
d.replace( {'Group': {f'perc_inperson_days_lost_{gkey}':gkey for gkey in grp_dict.keys()}}, inplace=True)
g = sns.FacetGrid(data=d, row='Group', height=4, aspect=3, row_order=['Teachers & Staff', 'Students'], legend_out=False)
g.map_dataframe( sns.barplot, x='key1', y='Days lost (%)', hue='key2', hue_order=test_order, order=scen_order, palette=test_hue) #'Reds'
g.add_legend(fontsize=14)
g.set_titles(row_template="{row_name}", fontsize=24)
xtl = g.axes[1,0].get_xticklabels()
xtl = [l.get_text() for l in xtl]
g.set(xticklabels=[scen_names[k] if k in scen_names else k for k in xtl])
g.set_axis_labels(y_var="Days lost (%)")
plt.tight_layout()
cv.savefig(os.path.join(imgdir, '3mInPersonDaysLost.png'), dpi=300)

# Re
fig, ax = plt.subplots(figsize=(12,8))
sns.barplot(data=df, x='key1', y='re', hue='key2', hue_order=test_order, order=scen_order, palette=test_hue)
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
extract = df.groupby(['key1', 'key2'])[['es_perc_d1', 'ms_perc_d1', 'hs_perc_d1']].mean().loc['as_normal'].reset_index()
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
g.add_legend(fontsize=14)
plt.tight_layout()
cv.savefig(os.path.join(imgdir, 'FirstDayInfectionsReg.png'), dpi=300)

# Tests required
fig, ax = plt.subplots(figsize=(12,8))
d = pd.DataFrame(byschool)
# Additional tests per 100,000 population
print(d.groupby('type').sum())
d['PCR'] *= 100000 / d['Days'] / d['Pop*Scale']
d['Antigen'] *= 100000 / d['Days'] / d['Pop*Scale']
test_order.reverse()

d['Total'] = d['PCR'] + d['Antigen']
d = d.loc[d['key1'] == 'with_countermeasures']
d = d.groupby('key2').mean().loc[test_order][['n', 'PCR', 'Antigen', 'Total']].reset_index()
ax.barh(d['key2'], d['Total'], color='r', label='Antigen')
ax.barh(d['key2'], d['PCR'], color='b', label='PCR')
ax.grid(axis='x')
ax.set_xlabel('Additional tests required (daily per 100k population)')
fig.tight_layout()
plt.legend()
cv.savefig(os.path.join(imgdir, f'NumTests.png'), dpi=300)



# Save mean to CSV
df.groupby(['key1', 'key2']).mean().to_csv(os.path.join(imgdir, 'Mean.csv'))
