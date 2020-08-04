import covasim as cv
import pylab as pl

sdict = cv.load('sdict.obj')

print(sdict['as_normal_20_cases_re_0.9'].results['cum_infections'][-1])
print(sdict['as_normal_110_cases_re_0.9'].results['cum_infections'][-1])
print(sdict['as_normal_20_cases_re_0.9'].school_info['num_student_cases'])
print(sdict['as_normal_110_cases_re_0.9'].school_info['num_student_cases'])


fig = pl.figure(figsize=(20,12), dpi=150)

schools_reopening_scenarios = [
    'as_normal',
    'with_screening',
    'with_hybrid_scheduling',
    'ES_MS_inperson_HS_remote',
    'ES_inperson_MS_HS_remote',
    'ES_hybrid',
    'all_remote',
]

for i,scen in enumerate(schools_reopening_scenarios):
    ax = pl.subplot(4,2,i+1)
    colors = [
        [0.1,0.1,0.9],
        [0.9,0.1,0.1],
        [0.1,0.6,0.9],
        [0.9,0.6,0.1],
        ]
    factor = 1
    last = (i == len(schools_reopening_scenarios)-1)
    for l,l2 in enumerate([f'20_cases_re_0.9', f'110_cases_re_0.9', f'20_cases_re_1.1', f'110_cases_re_1.1']):
        l1 = f'{scen}_'
        label = l1 + l2
        pl.plot(sdict[label].school_info['num_cases_by_day'], label=f'School cases, {l2}', lw=3, c=colors[l])
        pl.plot(sdict[label].results['n_infectious'].values/factor, '--', c=colors[l], lw=2, label=f'Total cases, {l2}')
    if last:
        pl.legend(bbox_to_anchor=(1.1, 1.0))
    pl.title(f'Number of cases per day (staff + students + teachers) for {scen}')


print('Done.')