'''
Create the calibrated sim for the King County results. Note: this script relies
on kc_synthpops_with_ltcf_seed0.ppl, which is created by cache_sp_pop.py, as well as several
CSV files.
'''

# Standard packages
import os
import numpy as np
import pandas as pd
import sciris as sc
import covasim as cv


cv.check_save_version('1.4.7', die=True)

# Define the input files
inputs         = 'inputs'
epi_data_file  = f'{inputs}/20200605chop5_KingCounty_Covasim.csv'
age_data_file  = f'{inputs}/20200605chop5_KingCounty_AgeHist.csv'
safegraph_file = f'{inputs}/KC_weeklyinteractions_061220.csv'
popfile_stem   = f'{inputs}/kc_synthpops_with_ltcf_seed'


def make_safegraph(sim):
    ''' Create interventions representing SafeGraph data '''

    # Load data.values
    fn = safegraph_file
    df = pd.read_csv(fn)
    week = df['week']
    w = df['p.emp'].values
    c = df['p.cust'].values

    # Do processing
    npts = len(week)
    start_date = sc.readdate(week[0], dateformat='%Y-%m-%d')
    start_day = sim.day(start_date)
    sg_days = start_day + 7*np.arange(npts)

    # Create interventions
    interventions = [
        cv.clip_edges(days=sg_days, changes=w, layers='w', label='clip_w'),
        cv.clip_edges(days=sg_days, changes=c, layers='c', label='clip_c'),
        ]
    return interventions


def define_pars(which='best', kind='default', use_safegraph=True):
    ''' Define the parameter best guesses and bounds '''

    pardata = {}
    if kind in ['default', 'both']:
        if use_safegraph:
            pardata.update(dict(
                # name          best      low       high
                # pop_infected = [400.0   , 70.0    , 700.0]    ,
                beta         = [  0.012,  0.008  ,   0.014]  ,
                bc_wc1       = [  0.60  ,  0.10   ,   1.00]   ,
                bc_wc2       = [  0.50  ,  0.10   ,   1.00]   ,
                bc_wc3       = [  0.75  ,  0.10   ,   1.00]   ,
                bc_lf        = [  0.18  ,  0.05   ,   0.50]   ,
                tn1          = [ 15.0   ,  5.0    ,  50.0]    ,
                tn2          = [ 15.0   ,  5.0    ,  50.0]    ,
                tn3          = [ 30.0   ,  5.0    ,  50.0]    ,
            ))
        else:
            pardata.update(dict(
                # name          best      low       high
                # pop_infected = [250.0   , 70.0    , 700.0]    ,
                beta         = [  0.0126,  0.008  ,   0.014]  ,
                bc_wc1       = [  0.25  ,  0.10   ,   1.00]   ,
                bc_wc2       = [  0.20  ,  0.10   ,   1.00]   ,
                bc_wc3       = [  0.30  ,  0.10   ,   1.00]   ,
                bc_lf        = [  0.15  ,  0.05   ,   0.50]   ,
                tn1          = [ 15.0   ,  5.0    ,  50.0]    ,
                tn2          = [ 15.0   ,  5.0    ,  50.0]    ,
                tn3          = [ 30.0   ,  5.0    ,  50.0]    ,
            ))
    if kind in ['layers', 'both']:
        pardata.update(dict(
            # name  best    low     high
            bl_h = [7.0,    1.0,    15.0],
            bl_s = [0.7,    0.0,     3.0],
            bl_w = [0.7,    0.0,     3.0],
            bl_c = [0.14,   0.0,     3.0],
            bl_l = [2.1,    0.0,     5.0],
        ))

    output = {}
    for key,arr in pardata.items():
        if which == 'best':
            output[key] = arr[0]
        elif which == 'bounds':
            output[key] = arr[1:3]

    return output


def create_sim(pars=None, label=None, use_safegraph=True, show_intervs=False, people=None):
    ''' Create a single simulation for further use '''

    p = sc.objdict(sc.mergedicts(define_pars(which='best', kind='both', use_safegraph=use_safegraph), pars))
    if 'rand_seed' not in p:
        seed = 1
        print(f'Note, could not find random seed in {pars}! Setting to {seed}')
        p['rand_seed'] = seed # Ensure this exists
    if 'end_day' not in p:
        end_day = '2020-06-12'
        p['end_day'] = end_day


    # Basic parameters and sim creation
    pars = {  'pop_size'      : 225e3,
              'pop_scale'     : 10,
              'pop_type'      : 'synthpops',
              'pop_infected'  : 400,
              'beta'          : p.beta,
              'start_day'     : '2020-01-27',
              'end_day'       : '2020-06-05',
              'rescale'       : True,
              'rescale_factor': 1.1,
              'verbose'       : 0.1,
              'rand_seed'     : p.rand_seed,
              'analyzers'     : cv.age_histogram(datafile=age_data_file),
              'beta_layer'    : dict(h=p.bl_h, s=p.bl_s, w=p.bl_w, c=p.bl_c, l=p.bl_l),
            }
    pars.update({'n_days': cv.daydiff(pars['start_day'], pars['end_day'])})

    # If supplied, use an existing people object
    if people:
        popfile = people
    else:
        # Generate the population filename
        n_popfiles = 5
        popfile = popfile_stem + str(pars['rand_seed']%n_popfiles) + '.ppl'

        # Check that the population file exists
        if not os.path.exists(popfile):
            errormsg = f'WARNING: could not find population file {popfile}! Please regenerate first'
            raise FileNotFoundError(errormsg)

    # Create and initialize the sim
    sim = cv.Sim(pars, label=label, popfile=popfile, load_pop=True, datafile=epi_data_file) # Create this here so can be used for test numbers etc.
    # Define testing interventions
    test_kwargs = dict(daily_tests=sim.data['new_tests'], quar_test=1.0, test_delay=2)
    tn1 = cv.test_num(symp_test=p.tn1, start_day='2020-01-27', end_day='2020-03-23', **test_kwargs, label='tn1')
    tn2 = cv.test_num(symp_test=p.tn2, start_day='2020-03-24', end_day='2020-04-14', **test_kwargs, label='tn2')
    tn3 = cv.test_num(symp_test=p.tn3, start_day='2020-04-15', end_day=None,         **test_kwargs, label='tn3')
    interventions = [tn1, tn2, tn3]

    # Define beta interventions (for calibration)
    b_ch = sc.objdict()
    b_days = ['2020-03-04', '2020-03-12', '2020-03-23', '2020-04-25']
    b_ch.s = [1.00, 0.00, 0.00, 0.00]
    b_ch.h = [1.00, 1.10, 1.20, 1.20]
    b_ch.w = [1.00, p.bc_wc1, p.bc_wc2, p.bc_wc3]
    b_ch.c = [1.00, p.bc_wc1, p.bc_wc2, p.bc_wc3]

    for lkey,ch in b_ch.items():
        interventions += [cv.change_beta(days=b_days, changes=b_ch[lkey], layers=lkey, label=f'beta_{lkey}')]

    # LTCF intervention
    b_days_l = np.arange(sim.day(b_days[0]), sim.day(b_days[2]) + 1)
    b_ch_l = np.linspace(1.0, p.bc_lf, len(b_days_l))
    interventions += [cv.change_beta(days=b_days_l, changes=b_ch_l, layers='l', label=f'beta_l')]

    # SafeGraph intervention & tidy up
    interventions += make_safegraph(sim)
    sim['interventions'] = interventions

    # Don't show interventions in plots, there are too many
    if show_intervs == False:
        for interv in sim['interventions']:
            interv.do_plot = False

    # These are copied from parameters.py -- needed to get younger and 60-65 groups right
    sim['prognoses']['age_cutoffs'] = np.array([0,      15,      20,      30,      40,      50,      65,      70,      80,      90]) # Age cutoffs (upper limits)
    # sim['prognoses']['sus_ORs'] = np.array([0.34, 0.67, 1.00, 1.00, 1.00, 1.00, 1.24, 1.47, 1.47, 10])

    return sim


def run_sim(pars=None, interactive=False, sim=None, use_safegraph=True):
    ''' Create and run a simulation from a given set of parameters '''

    # Create and run the sim
    if sim is None:
        sim = create_sim(pars=pars, use_safegraph=use_safegraph)
    if not sim.results_ready:
        sim.run()

    # Get the age histogram and compute the fit
    ageh = sim['analyzers'][0]
    age_fit = dict(
        age_tests     = dict(data=ageh.data['cum_tests'].values,     sim=ageh.hists[-1]['tested'],    weight=0.0),
        age_diagnoses = dict(data=ageh.data['cum_diagnoses'].values, sim=ageh.hists[-1]['diagnosed'], weight=0.2),
        age_deaths    = dict(data=ageh.data['cum_deaths'].values,    sim=ageh.hists[-1]['dead'],      weight=1),
    )
    fit = sim.compute_fit(custom=age_fit, keys=['cum_diagnoses', 'cum_deaths', 'new_diagnoses', 'new_deaths'], weights={'cum_diagnoses':1, 'cum_deaths':1, 'new_diagnoses':0.01, 'new_deaths':0.01})

    # Handle output
    if interactive:
        sim.plot()
        fit.plot()
        return sim, fit
    else:
        return fit.mismatch


if __name__ == '__main__':

    T = sc.tic()

    plot_fit      = 1
    use_multisim  = 1
    use_safegraph = 1

    # Settings
    reps = 5 # Set multiple runs to average over likelihood
    base_sim = create_sim(use_safegraph=use_safegraph)

    # Plot calibration -- NB, needs refactor
    if use_multisim:
        msim = cv.MultiSim(base_sim, n_runs=reps)
        msim.run(reseed=True, noise=0.0, keep_people=True, par_args={'ncpus':5})
        sims = msim.sims
        msim.reduce()
        sim = msim.base_sim
    else:
        sim = base_sim
        sim.run()
        sims = [sim]

    # Do plotting
    sim, fit = run_sim(sim=sim, use_safegraph=use_safegraph, interactive=True)

    sc.toc(T)
