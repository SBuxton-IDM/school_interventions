import covasim as cv
import numpy as np
import create_sim as cs
import sciris as sc
from school_intervention import new_schools

re_to_fit = 1.0
cases_to_fit = 75
debug = True

def scenario(es, ms, hs):
    return {
        'pk': None,
        'es': sc.dcp(es),
        'ms': sc.dcp(ms),
        'hs': sc.dcp(hs),
        'uv': None,
    }


if __name__ == '__main__':
    params = {
        'rand_seed': 0,
        'pop_infected': 160,
        'clip_edges': 0.65,
        'change_beta': 0.525,
    }
    sim = cs.create_sim(params, pop_size=1e5) # 2.25e4
    base_beta_s = sim.pars['beta_layer']['s']

    PCR_every_1d_starting_1wprior = [{
        'start_date': '2020-10-26',
        'repeat': 1,
        'groups': ['students', 'teachers', 'staff'],
        'coverage': 1,
        'sensitivity': 1,
        'delay': 0 # NOTE: no delay!
        #'specificity': 1,
    }]

    Antigen_every_1w_starting_1wprior_staff = [{
        'start_date': '2020-10-26',
        'repeat': 7,
        'groups': ['teachers', 'staff'], # No students
        'coverage': 1,
        'sensitivity': 0.8, # Lower sensitiviy, 0.8 is a modeling assumption as the true sensitivity is unknown at this time  - TODO: Propoer antigen testing in covasim
        'specificity': 0.8,
        'delay': 0,          # No delay
    }]

    remote = { # <-- used in calibration
        'start_day': '2020-11-02',
        'schedule': 'Remote',
        'screen_prob': 0,
        'test_prob': 0, # Amongst those screened positive
        'trace_prob': 0, # Tracing prob from newly diagnosed index cases
        'quar_prob': 0,
        'ili_prob': 0,
        'beta_s': 0, # This turns off transmission in the School class
        'testing': None,
    }

    base = {
        'start_day': '2020-11-02',
        'schedule': 'Full',
        'screen_prob': 0.9,
        'test_prob': 0.5,
        'trace_prob': 0.75,
        'quar_prob': 0.75,
        'ili_prob': 0.002, # Daily ili probability equates to about 10% incidence over the first 3 months of school
        'beta_s': 0.75 * base_beta_s,
        'testing': Antigen_every_1w_starting_1wprior_staff,
    }


    s = scenario(es=base, ms=base, hs=base)

    ns = new_schools(s)
    sim['interventions'] += [ns]

    sim.run(keep_people=debug)

    first_school_day = sim.day('2020-11-02')
    last_school_day = sim.day('2021-01-31')

    re = np.mean(sim.results['r_eff'][first_school_day:last_school_day])
    cases_past14 = np.sum(sim.results['new_diagnoses'][(first_school_day-14):first_school_day]) * 100e3 / (sim.pars['pop_size'] * sim.pars['pop_scale'])
    cases_during = np.mean(sim.results['new_diagnoses'][first_school_day:last_school_day]) * 14 * 100e3 / (sim.pars['pop_size'] * sim.pars['pop_scale'])

    re_mismatch = (re_to_fit - re)**2 / re_to_fit**2
    cases_past14_mismatch = (cases_to_fit - cases_past14)**2 / cases_to_fit**2
    cases_during_mismatch = (cases_to_fit - cases_during)**2 / cases_to_fit**2
    mismatch = re_mismatch + cases_past14_mismatch + cases_during_mismatch

    print(re, cases_past14, cases_during, mismatch)


    if debug:
        sim.plot(to_plot='overview')
        #t = sim.make_transtree()
    else:
        sim.plot()

    cv.savefig('sim.png')


    '''
    ms.reduce()
    #ms.save(msim_nopeople_fn, keep_people=False)
    #ms.plot(to_plot='overview')

    #plt.figure()
    to_plot = sc.odict({
            'New Infections': [
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
            'New Tests': [
                'new_tests',
            ],
            'Prevalence': [
                'prevalence',
            ],
        })
    fig = plt.figure(figsize=(16,10))
    ms.plot(to_plot=to_plot, n_cols=2, interval=30, legend_args={'show_legend':False}, do_show=False, fig=fig) # , dateformat='%B'

    s0 = ms.sims[0]
    for i, ax in enumerate(fig.axes):
        if i < len(fig.axes)-2:
            ax.xaxis.set_visible(False)
        ax.axvline(x=s0.day('2020-11-01'), color='c', ls='--')

    # Agh, x-axis is not a datetime!
    #import matplotlib.dates as mdates
    #months = mdates.MonthLocator(interval=1)  # every month
    #fig.axes[-1].xaxis.set_major_locator(months)

    #from matplotlib.dates import DateFormatter
    #date_form = DateFormatter('%B')#"%m-%d")
    #fig.axes[-1].xaxis.set_major_formatter(date_form)

    fig.tight_layout()
    cv.savefig(os.path.join('img', f'calibration_{int(pop_size)}.png'))
    '''
