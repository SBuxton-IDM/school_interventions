import covasim as cv
import pylab as pl

sdict = cv.load('sdict.obj')

print(sdict['as_normal_20_cases_re_0.9'].results['cum_infections'][-1])
print(sdict['as_normal_110_cases_re_0.9'].results['cum_infections'][-1])
print(sdict['as_normal_20_cases_re_0.9'].school_info['num_student_cases'])
print(sdict['as_normal_110_cases_re_0.9'].school_info['num_student_cases'])


fig = pl.figure(figsize=(15,10), dpi=150)

for i,scen in enumerate(['as_normal', 'all_remote']):
    ax = pl.subplot(2,1,i+1)
    for label in [f'{scen}_20_cases_re_0.9', f'{scen}_110_cases_re_0.9', f'{scen}_20_cases_re_1.1', f'{scen}_110_cases_re_1.1']:
        pl.plot(sdict[label].school_info['num_cases_by_day'], label=label, lw=3)
    pl.legend()
    pl.title('Number of cases per day (staff + students + teachers)')


print('Done.')