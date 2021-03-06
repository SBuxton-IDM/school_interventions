# Main workhorse script to generate plots from scenario simulations.  Sims are saved into the msim folder of the respective analysis folder, e.g. v20201013. Often we distribute computing by seeds, generating several *.msim files, which are combined here before plotting.

import os
import covasim as cv
import sciris as sc
import covasim.misc as cvm
import numpy as np
import pandas as pd
import matplotlib as mplt
import matplotlib.pyplot as plt
#import matplotlib.gridspec as gridspec
import seaborn as sns
import datetime as dt
from calibrate_model import evaluate_sim
from pathlib import Path

# Global plotting styles
font_size = 18
font_style = 'Roboto Condensed'
mplt.rcParams['font.size'] = font_size
mplt.rcParams['font.family'] = font_style

pop_size = 2.25e5 # 1e5 2.25e4 2.25e5

folder = 'v20201019'
variant = 'final_20201026_v2_0-30'
#variant = 'final_20201026_v2_noscreening_0-30' #'final_20201026_v2_0-30'
cachefn = os.path.join(folder, 'msims', f'{variant}.sims')
debug_plot = False

imgdir = os.path.join(folder, 'img_'+variant)
Path(imgdir).mkdir(parents=True, exist_ok=True)

print(f'Loading {cachefn}')
sims = cv.load(cachefn)
#sims = cv.MultiSim.load(cachefn).sims

results = []
byschool = []
groups = ['students', 'teachers', 'staff']

scen_names = sc.odict({ # key1
    'as_normal': 'Full Schedule\nNo Countermeasures',
    'with_countermeasures': 'Full Schedule',
    'all_hybrid': 'Hybrid',
    'k5': 'K-5 In-Person\nOthers Remote',
    'all_remote': 'All Remote',
})
scen_order = scen_names.keys()

blues = plt.cm.get_cmap('Blues')
reds = plt.cm.get_cmap('Reds')
test_names = sc.odict({ # key2
    'None':                                     ('No diagnostic screening',     'gray'),
    'PCR 1w prior':                             ('PCR one week prior, 1d delay',                    blues(1/5)),
    'Antigen every 1w teach&staff, PCR f/u':    ('Weekly antigen for teachers & staff, PCR f/u',    reds(1/5)),
    'PCR every 2w':                             ('Fortnightly PCR, 1d delay',                       blues(2/5)),
    'Antigen every 2w, no f/u':                 ('Fortnightly antigen, no f/u',                     reds(2/5)),
    'Antigen every 2w, PCR f/u':                ('Fortnightly antigen, PCR f/u',                    reds(3/5)),
    'PCR every 1w':                             ('Weekly PCR, 1d delay',                            blues(3/5)),
    'Antigen every 1w, PCR f/u':                ('Weekly antigen, PCR f/u',                         reds(4/5)),
    'PCR every 1d':                             ('Daily PCR, no delay',                             blues(4/5)),

    #'PCR every 2w 50%':                        ('Fortnightly PCR, 50% coverage',                   'cyan'),
    #'PCR every 1m 15%':                        ('Monthly PCR, 15% coverage',                       'pink'),
    #'Antigen every 1w teach&staff, PCR f/u':   ('Weekly antigen for teachers & staff, no delay, PCR f/u', 'yellow'),
    #'Antigen every 1w, PCR f/u':               ('Weekly antigen for all, no delay, PCR f/u',       'green'),
    #'Antigen every 1w, no f/u':                ('Weekly antigen for all, no delay, no f/u',        'orange'),
})
test_order = [v[0] for k,v in test_names.items()] # if k in ['None', 'PCR every 2w', 'Antigen every 2w, PCR f/u', 'Antigen every 2w, no f/u']]
test_hue = {v[0]:v[1] for v in test_names.values()}

for sim in sims:
    sim.key2 = test_names[sim.key2][0] if sim.key2 in test_names else sim.key2

tests = []
for sim in sims:
    first_school_day = sim.day('2020-11-02')
    last_school_day = sim.day('2021-01-31')
    ret = {
        'key1': sim.key1,
        'key2': sim.key2,
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



# Attack rate - two axes in one plot
d = pd.melt(df, id_vars=['key1', 'key2'], value_vars=[f'attackrate_{gkey}' for gkey in grp_dict.keys()], var_name='Group', value_name='Cum Inc (%)')
d.replace( {'Group': {f'attackrate_{gkey}':gkey for gkey in grp_dict.keys()}}, inplace=True)
d.replace( {'key1': scen_names}, inplace=True)
so = [scen_names[x] for x in scen_order]

for figsize in [(12,8), (12,9.5)]:
    fig = plt.figure(constrained_layout=True, figsize=figsize)
    gs = fig.add_gridspec(20, 50)

    ts = d.loc[(d['Group']=='Teachers & Staff')]

    # Teachers and Staff
    ax = fig.add_subplot(gs[0, :])
    ax.axis('off')
    ax.text(0.5, 0, 'Teachers & Staff', horizontalalignment='center')

    # Top left
    ax = fig.add_subplot(gs[1:8, 0:10])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.set_tick_params(length=0)
    sns.barplot(data=ts, x='key1', y='Cum Inc (%)', hue='key2', hue_order=test_order, order=so, palette=test_hue)
    ax.get_legend().remove()
    ax.set_xlim([-0.5,0.5])
    ax.set_ylim([0,50])
    ax.set_xlabel('')
    ax.set_xticklabels([])
    ax.set_ylabel('3-Month Attack Rate (%)')
    p = ax.get_position()

    # Top right
    ax = fig.add_subplot(gs[1:8, 10:])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.set_tick_params(length=0)
    sns.barplot(data=ts, x='key1', y='Cum Inc (%)', hue='key2', hue_order=test_order, order=so, palette=test_hue)
    ax.get_legend().remove()
    ax.set_xlim([0.5,4.5])
    ym = ts.loc[(ts['key1']==scen_names['with_countermeasures']) & (ts['key2']==test_names['None'][0]), 'Cum Inc (%)'].mean()
    ax.set_ylim([0,1.25*ym])
    ax.set_ylabel('')
    ax.set_xlabel('')
    ax.set_xticklabels([])

    stu = d.loc[(d['Group']=='Students')]

    # Students
    ax = fig.add_subplot(gs[8, :])
    ax.axis('off')
    ax.text(0.5, 0, 'Students', horizontalalignment='center')

    # Bottom left
    ax = fig.add_subplot(gs[9:16, 0:10])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.set_tick_params(length=0)
    sns.barplot(data=stu, x='key1', y='Cum Inc (%)', hue='key2', hue_order=test_order, order=so, palette=test_hue)
    ax.get_legend().remove()
    ax.set_xlim([-0.5,0.5])
    ax.set_ylim([0,35])
    ax.set_xlabel('')
    ax.set_ylabel('3-Month Attack Rate (%)')

    # Bottom right
    ax = fig.add_subplot(gs[9:16, 10:])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.set_tick_params(length=0)
    sns.barplot(data=stu, x='key1', y='Cum Inc (%)', hue='key2', hue_order=test_order, order=so, palette=test_hue)
    hnd, lbl = ax.get_legend_handles_labels()
    ax.get_legend().remove()
    ax.set_xlim([0.5,4.5])
    ym = stu.loc[(stu['key1']==scen_names['with_countermeasures']) & (stu['key2']==test_names['None'][0]), 'Cum Inc (%)'].mean()
    ax.set_ylim([0, 1.25*ym])
    ax.set_ylabel('')
    ax.set_xlabel('')

    ax = fig.add_subplot(gs[16:, :])
    ax.axis('off')
    ax.legend(hnd, lbl, ncol=3, loc='center', fontsize=16)

    cv.savefig(os.path.join(imgdir, f'3mAttackRate_combined_{figsize}.png'), dpi=300)



# Attack rate
for name in ['all', 'no_normal']:
    d = pd.melt(df, id_vars=['key1', 'key2'], value_vars=[f'attackrate_{gkey}' for gkey in grp_dict.keys()], var_name='Group', value_name='Cum Inc (%)')
    d.replace( {'Group': {f'attackrate_{gkey}':gkey for gkey in grp_dict.keys()}}, inplace=True)

    so = scen_order
    if name == 'no_normal':
        d = d.loc[d['key1']!='as_normal'] # Remove normal
        so = so[1:]

    g = sns.FacetGrid(data=d, row='Group', height=4, aspect=3, row_order=['Teachers & Staff', 'Students'], legend_out=False)

    g.map_dataframe( sns.barplot, x='key1', y='Cum Inc (%)', hue='key2', hue_order=test_order, order=so, palette=test_hue)
    if name == 'all':
        g.add_legend(fontsize=14)

    g.set_titles(row_template="{row_name}")
    xtl = g.axes[1,0].get_xticklabels()
    xtl = [l.get_text() for l in xtl]
    g.set(xticklabels=[scen_names[k] if k in scen_names else k for k in xtl])
    g.set_axis_labels(y_var="3-Month Attack Rate (%)")
    plt.tight_layout()
    cv.savefig(os.path.join(imgdir, f'3mAttackRate_{name}.png'), dpi=300)

# Frac in-person days lost
for aspect in [2.5, 3]:
    d = pd.melt(df, id_vars=['key1', 'key2'], value_vars=[f'perc_inperson_days_lost_{gkey}' for gkey in grp_dict.keys()], var_name='Group', value_name='Days lost (%)')
    d.replace( {'Group': {f'perc_inperson_days_lost_{gkey}':gkey for gkey in grp_dict.keys()}}, inplace=True)
    g = sns.FacetGrid(data=d, row='Group', height=4, aspect=aspect, row_order=['Teachers & Staff', 'Students'], legend_out=False)
    g.map_dataframe( sns.barplot, x='key1', y='Days lost (%)', hue='key2', hue_order=test_order, order=scen_order, palette=test_hue) #'Reds'
    g.add_legend(fontsize=14)
    g.set_titles(row_template="{row_name}", fontsize=24)
    xtl = g.axes[1,0].get_xticklabels()
    xtl = [l.get_text() for l in xtl]
    g.set(xticklabels=[scen_names[k] if k in scen_names else k for k in xtl])
    g.set_axis_labels(y_var="Remote learning days (%)")
    plt.tight_layout()
    cv.savefig(os.path.join(imgdir, f'InPersonDaysLost_{aspect}.png'), dpi=300)

# Re
for figsize in [(12,8), (12,9.5)]:
    fig, ax = plt.subplots(figsize=figsize)
    sns.barplot(data=df, x='key1', y='re', hue='key2', hue_order=test_order, order=scen_order, palette=test_hue)
    ax.set_ylim([0.8, 1.45])
    ax.set_ylabel(r'Population-wide reproduction number ($R_e$)')
    ax.set_xlabel('')
    xtl = ax.get_xticklabels()
    xtl = [l.get_text() for l in xtl]
    ax.set_xticklabels([scen_names[k] if k in scen_names else k for k in xtl])
    ax.axhline(y=1, color='k', ls=':', lw=2)
    plt.legend().set_title('')
    plt.tight_layout()
    cv.savefig(os.path.join(imgdir, f'Re_3mAverage_{figsize}.png'), dpi=300)

# Percent of schools with infections on day 1
'''
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
'''

# Number of diagnostic tests required
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
print(d)
ax.barh(d['key2'], d['Total'], color='r', label='Antigen')
ax.barh(d['key2'], d['PCR'], color='b', label='PCR')
ax.grid(axis='x')
ax.set_xlabel('Additional tests required (daily per 100k population)')
fig.tight_layout()
plt.legend()
cv.savefig(os.path.join(imgdir, f'NumTests.png'), dpi=300)



# Save mean to CSV
df.groupby(['key1', 'key2']).mean().to_csv(os.path.join(imgdir, 'Mean.csv'))
