import os
import covasim as cv
import numpy as np
import matplotlib as mplt
import matplotlib.pyplot as plt
import sciris as sc

do_filter = True

# Global plotting styles
font_size = 16
font_style = 'Roboto Condensed'
mplt.rcParams['font.size'] = font_size
mplt.rcParams['font.family'] = font_style

pop_size = 1e5 # 2.25e4 2.25e5

if do_filter:
    '''
    msim = cv.MultiSim.merge([
        cv.MultiSim.load(os.path.join('msims', f'testing_v20201013_v1a_{int(pop_size)}.msim')),
        cv.MultiSim.load(os.path.join('msims', f'testing_v20201013_v1b_{int(pop_size)}.msim')),
        cv.MultiSim.load(os.path.join('msims', f'testing_v20201013_v1c_{int(pop_size)}.msim')),
        cv.MultiSim.load(os.path.join('msims', f'testing_v20201013_v1d_{int(pop_size)}.msim')),
        cv.MultiSim.load(os.path.join('msims', f'testing_v20201013_v1e_{int(pop_size)}.msim')),
    ])
    '''
    msim = cv.MultiSim.load(os.path.join('msims', f'testing_v20201013_v1_{int(pop_size)}.msim'))

    remote_none = [s for s in msim.sims if s.key1=='all_remote' and s.key2=='None']

    t1 = remote_none[0].day('2020-10-25') # Before testing mixes up random numbers

    keep = [s for s in remote_none if np.abs(s.results.prevalence[t1]-0.002) < 0.001] # Corresponds to RAINIER CI

    print(f'Keeping {len(keep)} of {len(remote_none)} seeds')
    print('Prevalence:', [s.results.prevalence[t1] for s in keep])

    seeds = [s.pars['rand_seed'] for s in keep]
    sims = [s for s in msim.sims if s['rand_seed'] in seeds] # Keep good sims

    print(f'Kept {len(sims)} of {len(msim.sims)} simulations')

    msim_keep = cv.MultiSim(sims)
    msim_keep.save(os.path.join('msims', f'testing_v20201013_v1_filterseeds_{int(pop_size)}.msim'))
else:
    print('Loading filtered simulations from file')
    msim_keep = cv.MultiSim.load(os.path.join('msims', f'testing_v20201013_v1_filterseeds_{int(pop_size)}.msim'))

# Plotting
msim_keep.reduce()

to_plot = sc.odict({
        'New Infections per 100k': [
            'new_infections',
        ],
        'New Diagnoses per 100k': [
            'new_diagnoses',
        ],
        'Test Yield': [
            'test_yield',
        ],
        'Effective Reproduction Number': [
            'r_eff',
        ],
        'New Tests per 100k': [
            'new_tests',
        ],
        'Prevalence': [
            'prevalence',
        ],
    })
fig = plt.figure(figsize=(16,10))
msim_keep.plot(to_plot=to_plot, n_cols=2, interval=30, legend_args={'show_legend':False}, do_show=False, fig=fig) # , dateformat='%B'

s0 = msim_keep.sims[0]
for i, ax in enumerate(fig.axes):
    if i < len(fig.axes)-2:
        ax.xaxis.set_visible(False)
    ax.axvline(x=s0.day('2020-11-01'), color='c', ls='--')

fig.tight_layout()
cv.savefig(os.path.join('img', 'calibration_filterseeds.png'))
