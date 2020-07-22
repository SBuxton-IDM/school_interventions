'''
Create the calibrated sim for the King County results. Note: this script relies
on kc_synthpops.ppl, which is created by cache_population.py, as well as several
CSV files.
'''

# Standard packages
import os
import numpy as np
import pandas as pd
import sciris as sc

# Covasim packages and modules
import covasim as cv
from covasim.interventions import process_days, find_day

cv.check_save_version('1.5.0', die=True)

# Internal modules
from reopening_scenarios import beta_change_age


# -------------------------------------------------------------------------------
# Input files
# -------------------------------------------------------------------------------
inputs = 'inputs'
age_series_file = f'{inputs}/20200720trim5_KingCounty.csv'
epi_data_file = f'{inputs}/20200720trim5_KingCounty_Covasim.csv'
age_data_file = f'{inputs}/20200720trim5_KingCounty_AgeHist.csv'
safegraph_file = f'{inputs}/KC_weeklyinteractions_070120-rev1.csv'
popfile_stem   = f'{inputs}/kc_synthpops_normal_withstaff_seed'
popfile_stem_change = f'{inputs}/kc_synthpops_clustered_withstaff_seed'


# -------------------------------------------------------------------------------
# parameters and search intervals
# -------------------------------------------------------------------------------
def define_pars(which='best', kind='default', use_safegraph=True):
    ''' Define the parameter best guesses and bounds '''

    pardata = {}
    if kind in ['default', 'both']:
        pardata.update(dict(
            # name          best      low       high
            beta=[0.0129, 0.0126, 0.013],
            pop_infected=[314.0, 200.0, 500.0],  # 2020-02-01
            lseeds=[191.0, 0, 300],  # seed infections in LTCFs

            rsp1=[0.4, 0.1, 0.50],  # severe prob. factor;  30 < age < 79
            rsp2=[0.7, 0.3, 0.80],  # severe prob. factor;  age > 80

            tn1=[6.0, 1.0, 15.0],  # 2020-01-27 - 2020-03-23
            tn2=[16.0, 1.0, 25.0],  # 2020-03-24 - 2020-04-14
            tn3=[33.0, 20.0, 40.0],  # 2020-04-15 - 2020-05-07
            tn4=[41.0, 20.0, 50.0],  # 2020-05-08 - 2020-06-04
            tn5=[33.0, 10.0, 50.0],  # 2020-06-05 - 2020-06-18
            tn6=[45.0, 1.0, 100.0],  # 2020-06-19 - end

            bc_lf=[0.24, 0.01, 0.30],  # 2020-03-02 --> 2020-03-12
            bc_s=[0.32, 0.2, 0.35],  # 2020-03-12 - end

            bc_age_u10_a=[10.0, 6.0, 25.0],  # 2020-05-08 - 2020-06-04
            bc_age_10_20_a=[5.0, 4.0, 15.0],  # 2020-05-08 - 2020-06-04
            bc_age_20_30_a=[23.0, 15.0, 25.0],  # 2020-05-08 - 2020-06-04
            bc_age_30_40_a=[0.74, 0.5, 1.1],  # 2020-05-08 - 2020-06-04
            bc_age_65u_a=[0.72, 0.5, 0.9],  # 2020-05-08 - 2020-06-04

            bc_age_u10_b=[22.0, 5.0, 30.0],  # 2020-06-05 - 2020-06-18
            bc_age_10_20_b=[23.0, 5.0, 30.0],  # 2020-06-05 - 2020-06-18
            bc_age_20_30_b=[19.0, 5.0, 30.0],  # 2020-06-05 - 2020-06-18
            bc_age_30_40_b=[15.0, 0.1, 3.0],  # 2020-06-05 - 2020-06-18
            bc_age_65u_b=[0.68, 0.1, 0.9],  # 2020-06-05 - 2020-06-18

            bc_age_u10_c=[22.0, 5.0, 40.0],  # 2020-06-19 - end
            bc_age_10_20_c=[23.0, 5.0, 40.0],  # 2020-06-19 - end
            bc_age_20_30_c=[19.0, 5.0, 40.0],  # 2020-06-19 - end
            bc_age_30_40_c=[8.0, 0.1, 8.0],  # 2020-06-19 - end
            bc_age_65u_c=[0.68, 0.1, 0.9],  # 2020-06-19 - end
        ))
        if use_safegraph:
            pardata.update(dict(
                bc_wc1=[0.96, 0.90, 1.00],  # (1.0) 2020-03-02 --> 2020-03-12 - 2020-03-22
                bc_wc2=[0.88, 0.85, 0.90],  # 2020-03-23 - 2020-04-14
                bc_wc3=[0.71, 0.60, 0.80],  # 2020-04-15 - 2020-05-07
                bc_wc4=[0.10, 0.05, 0.40],  # 2020-05-08 - 2020-06-04
                bc_wc5=[0.24, 0.05, 0.50],  # 2020-06-05 - 2020-06-18
                bc_wc6=[0.20, 0.01, 1.00],  # 2020-06-19 - end
            ))
        else:
            pardata.update(dict(
                bc_wc1=[0.35, 0.10, 0.60],
                bc_wc2=[0.30, 0.10, 0.60],
                bc_wc3=[0.30, 0.10, 0.60],
            ))
    if kind in ['layers', 'both']:
        pardata.update(dict(
            # name  best    low     high
            bl_h=[3.0, 1.0, 15.0],
            bl_s=[0.6, 0.0, 3.0],
            bl_w=[0.6, 0.0, 3.0],
            bl_c=[0.3, 0.0, 3.0],
            bl_l=[1.5, 0.0, 5.0],
        ))

    output = {}
    for key, arr in pardata.items():
        if which == 'best':
            output[key] = arr[0]
        elif which == 'bounds':
            output[key] = arr[1:3]

    return output


class seed_ltcf(cv.Intervention):
    '''Add importations to LTCF layer'''

    def __init__(self, days, seeds, **kwargs):
        super().__init__(**kwargs)
        self._store_args()  # Store the input arguments so the intervention can be recreated
        self.days = sc.dcp(days)
        self.seeds = sc.promotetolist(seeds)

    def initialize(self, sim):
        self.days = process_days(sim, self.days)
        self.initialized = True

    def apply(self, sim):
        # If this day is found in the list, apply the intervention
        for ind in find_day(self.days, sim.t):
            # find people associated with LTCF
            layer = sim.people.contacts['l']
            inds = np.unique(np.ravel([layer[p] for p in ['p1', 'p2']]))
            inds = inds[cv.choose(max_n=len(inds), n=self.seeds[ind])]
            sim.people.infect(inds)


def make_safegraph(sim, use_interp=True):
    ''' Create interventions representing SafeGraph data '''

    # Load data.values
    fn = safegraph_file
    df = pd.read_csv(fn)
    week = df['week']
    w = df["p.emp.no.schools"].values
    c = df["p.cust.no.schools"].values
    s = df["p.tot.schools"].values

    # Do processing
    npts = len(week)
    start_date = sc.readdate(week[0], dateformat='%Y-%m-%d')
    start_day = sim.day(start_date)
    sg_days = start_day + 7 * np.arange(npts)

    # Create interventions
    interventions = [
        cv.clip_edges(days=sg_days, changes=w, layers='w', label='clip_w'),
        cv.clip_edges(days=sg_days, changes=c, layers='c', label='clip_c'),
        cv.clip_edges(days=sg_days, changes=s, layers='s', label='clip_s'),
    ]
    return interventions


def remove_ltcf_community(sim, debug=False):
    ''' Ensure LTCF residents don't have community contacts '''
    over_65 = sc.findinds(sim.people.age > 65)
    llayer = sim.people.contacts['l']
    clayer = sim.people.contacts['c']
    in_ltcf = np.union1d(llayer['p1'], llayer['p2'])
    over_65_in_ltcf = np.intersect1d(over_65, in_ltcf)
    p1inds = sc.findinds(np.isin(clayer['p1'], over_65_in_ltcf))
    p2inds = sc.findinds(np.isin(clayer['p2'], over_65_in_ltcf))
    popinds = np.union1d(p1inds, p2inds)
    if debug:
        print(f'Over 65: {len(over_65)}')
        print(f'Over 65 LTCF: {len(over_65_in_ltcf)}')
        print(f'Pop inds: {len(popinds)}')
        print(f'Orig len: {len(clayer)}')
    clayer.pop_inds(popinds)
    if debug:
        print(f'New len: {len(clayer)}')
    return clayer


def ftest_num_subtarg1(sim, sev=5.0):
    ''' Subtarget '''
    drop_inds = sc.findinds(sim.people.age > 19)
    sev_inds = np.intersect1d(sim.people.true('severe'), sc.findinds(sim.people.age < 20))
    symp_inds = np.intersect1d(sim.people.true('symptomatic'), sc.findinds(sim.people.age < 20))

    drop_vals = np.zeros(len(drop_inds))
    sev_vals = sev * np.ones(len(sev_inds))
    symp_vals = 2 * np.ones(len(symp_inds))

    inds = np.concatenate([drop_inds, sev_inds, symp_inds])
    vals = np.concatenate([drop_vals, sev_vals, symp_vals])
    return {'inds': inds, 'vals': vals}


def ftest_num_subtarg2(sim, sev=5.0):
    ''' Subtarget '''
    drop_inds = sc.findinds(np.logical_or(sim.people.age < 20, sim.people.age > 39))
    sev_inds = np.intersect1d(sim.people.true('severe'),
                              sc.findinds(np.logical_and(sim.people.age > 19, sim.people.age < 40)))

    drop_vals = np.zeros(len(drop_inds))
    sev_vals = sev * np.ones(len(sev_inds))

    inds = np.concatenate([drop_inds, sev_inds])
    vals = np.concatenate([drop_vals, sev_vals])
    return {'inds': inds, 'vals': vals}

    return {'inds': drop_inds, 'vals': np.zeros(len(drop_inds))}


def ftest_num_subtarg3(sim, sev=5.0):
    ''' Subtarget '''
    drop_inds = sc.findinds(np.logical_or(sim.people.age < 40, sim.people.age > 59))
    sev_inds = np.intersect1d(sim.people.true('severe'),
                              sc.findinds(np.logical_and(sim.people.age > 39, sim.people.age < 60)))

    drop_vals = np.zeros(len(drop_inds))
    sev_vals = sev * np.ones(len(sev_inds))

    inds = np.concatenate([drop_inds, sev_inds])
    vals = np.concatenate([drop_vals, sev_vals])
    return {'inds': inds, 'vals': vals}


def ftest_num_subtarg4(sim, sev=5.0):
    ''' Subtarget '''
    drop_inds = sc.findinds(np.logical_or(sim.people.age < 60, sim.people.age > 79))
    sev_inds = np.intersect1d(sim.people.true('severe'),
                              sc.findinds(np.logical_and(sim.people.age > 59, sim.people.age < 80)))

    drop_vals = np.zeros(len(drop_inds))
    sev_vals = sev * np.ones(len(sev_inds))

    inds = np.concatenate([drop_inds, sev_inds])
    vals = np.concatenate([drop_vals, sev_vals])
    return {'inds': inds, 'vals': vals}


def ftest_num_subtarg5(sim, sev=5.0):
    ''' Subtarget '''
    drop_inds = sc.findinds(sim.people.age < 80)
    sev_inds = np.intersect1d(sim.people.true('severe'),
                              sc.findinds(sim.people.age > 79))

    drop_vals = np.zeros(len(drop_inds))
    sev_vals = sev * np.ones(len(sev_inds))

    inds = np.concatenate([drop_inds, sev_inds])
    vals = np.concatenate([drop_vals, sev_vals])
    return {'inds': inds, 'vals': vals}


def create_sim(pars=None, use_safegraph=True, label=None, show_intervs=False, people=None, adjust_ORs=False,
               num_pos=None, test_prob=None,
               trace_prob=None, NPI_schools=None, test_freq=None, network_change=False, schedule=None,
               school_start_day=None,
               intervention_start_day=None, ttq_scen=None
               ):
    ''' Create a single simulation for further use '''

    p = sc.objdict(sc.mergedicts(define_pars(which='best', kind='both', use_safegraph=use_safegraph), pars))
    if 'rand_seed' not in p:
        seed = 1
        print(f'Note, could not find random seed in {pars}! Setting to {seed}')
        p['rand_seed'] = seed  # Ensure this exists

    # Basic parameters and sim creation
    pars = {'pop_size': 225e3,
            'pop_scale': 10,
            'pop_type': 'synthpops',
            'pop_infected': p.pop_infected,
            'beta': p.beta,
            'start_day': '2020-02-01',
            'end_day': p['end_day'],
            'rescale': True,
            'rescale_factor': 1.1,
            'verbose': 0.1,
            'rand_seed': p.rand_seed,
            'analyzers': [cv.age_histogram(datafile=age_data_file,
                                           states=['exposed', 'dead', 'tested', 'diagnosed', 'severe'])],
            'beta_layer': dict(h=p.bl_h, s=p.bl_s, w=p.bl_w, c=p.bl_c, l=p.bl_l),
            }

    # If supplied, use an existing people object
    if people:
        popfile = people
    else:
        # Generate the population filename
        n_popfiles = 5
        popfile = popfile_stem + str(pars['rand_seed'] % n_popfiles) + '.ppl'
        popfile_change = popfile_stem_change + str(pars['rand_seed'] % n_popfiles) + '.ppl'

        # Check that the population file exists
        if not os.path.exists(popfile):
            errormsg = f'WARNING: could not find population file {popfile}! Please regenerate first'
            raise FileNotFoundError(errormsg)

    # Create and initialize the sim
    print(f'Creating sim! safegraph={use_safegraph}, seed={p.rand_seed}')
    sim = cv.Sim(pars, label=label, popfile=popfile, load_pop=True,
                 datafile=epi_data_file)  # Create this here so can be used for test numbers etc.

    interventions = []

    # Testing bins
    df = pd.read_csv(age_series_file)
    age_bins = [0, 20, 40, 60, 80, np.inf]
    test_num_subtargs = [ftest_num_subtarg1, ftest_num_subtarg2, ftest_num_subtarg3, ftest_num_subtarg4,
                         ftest_num_subtarg5]
    for ia in range(len(age_bins) - 1):
        label = '{}-{}'.format(age_bins[ia], age_bins[ia + 1] - 1)
        df_ = df[(df['age'] >= age_bins[ia]) & (df['age'] < age_bins[ia + 1])]
        # sum for the dates
        df_ = df_.groupby('date').sum()
        df_['age'] = age_bins[ia]
        df_['datetime'] = [sc.readdate(d) for d in df_.index.values]
        df_ = df_.set_index('datetime')
        # make sure we have all the days we care about
        new_index = pd.date_range(df_.index[0], df_.index[-1], freq='1d')

        df_ = df_.reindex(new_index, fill_value=0.0, method='nearest')
        test_kwargs = dict(daily_tests=df_['new_tests'], quar_test=1.0, test_delay=2, subtarget=test_num_subtargs[ia])
        interventions += [cv.test_num(symp_test=p.tn1, start_day='2020-01-27', end_day='2020-03-23', **test_kwargs,
                                      label='tn1 ' + label)]
        interventions += [cv.test_num(symp_test=p.tn2, start_day='2020-03-24', end_day='2020-04-14', **test_kwargs,
                                      label='tn2 ' + label)]
        interventions += [cv.test_num(symp_test=p.tn3, start_day='2020-04-15', end_day='2020-05-07', **test_kwargs,
                                      label='tn3 ' + label)]
        interventions += [cv.test_num(symp_test=p.tn4, start_day='2020-05-08', end_day='2020-06-04', **test_kwargs,
                                      label='tn4 ' + label)]
        interventions += [cv.test_num(symp_test=p.tn5, start_day='2020-06-17', end_day='2020-06-18', **test_kwargs,
                                      label='tn5 ' + label)]
        interventions += [cv.test_num(symp_test=p.tn6, start_day='2020-06-19', end_day=None, **test_kwargs,
                                      label='tn6 ' + label)]

    # Seed in LTCF
    interventions += [seed_ltcf(days=[15], seeds=[p.lseeds])]

    # Define beta interventions
    b_days = ['2020-03-02',
              '2020-03-12',
              '2020-03-23',
              '2020-04-15',
              '2020-05-08',
              '2020-06-05',
              '2020-06-19'
              ]

    # Home and school beta changes
    interventions += [
        cv.change_beta(days=b_days[1], changes=p.bc_s, layers='s', label="beta_s")
    ]

    # Work and community beta changes
    b_days_wc = np.arange(sim.day(b_days[0]), sim.day(b_days[1]) + 1).tolist() + b_days[2:]
    b_ch_wc = np.linspace(1.0, p.bc_wc1, len(b_days_wc) - 5).tolist() + [p.bc_wc2, p.bc_wc3, p.bc_wc4, p.bc_wc5,
                                                                         p.bc_wc6]

    for lkey in ['w', 'c']:
        interventions += [cv.change_beta(days=b_days_wc, changes=b_ch_wc, layers=lkey, label=f'beta_{lkey}')]

    # LTCF beta change
    b_days_l = np.arange(sim.day(b_days[0]), sim.day(b_days[2]) + 1)
    b_ch_l = np.linspace(1.0, p.bc_lf, len(b_days_l))
    interventions += [cv.change_beta(days=b_days_l, changes=b_ch_l, layers='l', label='beta_l')]
    # sim.people.contacts['c'] = remove_ltcf_community(sim) # Remove community contacts from LTCF

    # Age-based beta changes
    b_age_days = ["2020-05-08", "2020-06-05", "2020-06-19"]
    b_age_changes = [[p.bc_age_u10_a,  # 0
                      p.bc_age_10_20_a,  # 10
                      p.bc_age_20_30_a,  # 20
                      p.bc_age_30_40_a,  # 30
                      1.0,  # 40
                      1.0,  # 50
                      p.bc_age_65u_a,  # 65
                      p.bc_age_65u_a,  # 70
                      p.bc_age_65u_a,  # 80
                      p.bc_age_65u_a,  # 90
                      ],
                     [p.bc_age_u10_b,  # 0
                      p.bc_age_10_20_b,  # 10
                      p.bc_age_20_30_b,  # 20
                      p.bc_age_30_40_b,  # 30
                      1.0,  # 40
                      1.0,  # 50
                      p.bc_age_65u_b,  # 65
                      p.bc_age_65u_b,  # 70
                      p.bc_age_65u_b,  # 80
                      p.bc_age_65u_b,  # 90
                      ],
                     [p.bc_age_u10_c,  # 0
                      p.bc_age_10_20_c,  # 10
                      p.bc_age_20_30_c,  # 20
                      p.bc_age_30_40_c,  # 30
                      1.0,  # 40
                      1.0,  # 50
                      p.bc_age_65u_c,  # 65
                      p.bc_age_65u_c,  # 70
                      p.bc_age_65u_c,  # 80
                      p.bc_age_65u_c,  # 90
                      ]
                     ]
    interventions += [beta_change_age.change_beta_age(b_age_days, b_age_changes)]

    # SafeGraph intervention & tidy up
    if use_safegraph:
        interventions += make_safegraph(sim)

    if ttq_scen == 'lower':
        tp = sc.objdict(
            symp_prob=0.08,
            asymp_prob=0.001,
            symp_quar_prob=0.8,
            asymp_quar_prob=0.1,
            test_delay=2.0,
        )
        ct = sc.objdict(
            trace_probs=0.01,
            trace_time=3.0,
        )
    elif ttq_scen == 'medium':
        tp = sc.objdict(
            symp_prob=0.12,
            asymp_prob=0.0015,
            symp_quar_prob=0.8,
            asymp_quar_prob=0.1,
            test_delay=2.0,
        )
        ct = sc.objdict(
            trace_probs=0.25,
            trace_time=3.0,
        )
    elif ttq_scen == 'upper':
        tp = sc.objdict(
            symp_prob=0.24,
            asymp_prob=0.003,
            symp_quar_prob=0.8,
            asymp_quar_prob=0.1,
            test_delay=2.0,
        )
        ct = sc.objdict(
            trace_probs=0.5,
            trace_time=3.0,
        )

    if ttq_scen is not None:
        interventions += [cv.test_prob(start_day='2020-07-10', **tp), cv.contact_tracing(start_day='2020-07-10', **ct)]

    if network_change:
        popfile_new = popfile_change
    else:
        popfile_new = None

    if NPI_schools is not None:
        interventions += [cv.change_beta(days=sim.day('2020-09-01'), changes=NPI_schools, layers='s')]

    interventions += [cv.close_schools(day_schools_closed='2020-03-12', start_day=school_start_day,
                                        pop_file=popfile_new)]

    interventions += [cv.reopen_schools(start_day=intervention_start_day, num_pos=num_pos, test=test_prob,
                                       trace=trace_prob, ili_prev=0.002, test_freq=test_freq, schedule=schedule)]

    sim['interventions'] = interventions

    # Don't show interventions in plots, there are too many
    for interv in sim['interventions']:
        interv.do_plot = False

    # Prognoses (particularly to severe/hospitalizations) need attention
    prognoses = sc.dcp(cv.get_prognoses())
    prognoses['severe_probs'] *= prognoses[
        'symp_probs']  # Conditional probability of symptoms becoming severe, given symptomatic
    prognoses['crit_probs'] *= prognoses[
        'severe_probs']  # Conditional probability of symptoms becoming critical, given severe
    prognoses['death_probs'] *= prognoses['crit_probs']  # Conditional probability of dying, given critical symptoms
    prognoses.update({'age_cutoff': np.array([0, 10, 20, 30, 40, 50, 65, 70, 80, 90])})
    prognoses.update({'severe_probs': np.array([1, 1, 1, p.rsp1, p.rsp1, p.rsp1, p.rsp1, p.rsp1, p.rsp2, p.rsp2]) *
                                      prognoses['severe_probs']})
    prognoses['death_probs'] /= prognoses['crit_probs']  # Conditional probability of dying, given critical symptoms
    prognoses['crit_probs'] /= prognoses[
        'severe_probs']  # Conditional probability of symptoms becoming critical, given severe
    prognoses['severe_probs'] /= prognoses[
        'symp_probs']  # Conditional probability of symptoms becoming severe, given symptomatic
    sim.pars.update({'prognoses': prognoses})

    return sim


# -------------------------------------------------------------------------------
#  sim execution
# -------------------------------------------------------------------------------
def run_sim(pars=None, interactive=False, sim=None, use_safegraph=True):
    ''' Create and run a simulation from a given set of parameters '''

    # Create and run the sim
    if sim is None:
        sim = create_sim(pars=pars, use_safegraph=use_safegraph)
    if not sim.results_ready:
        sim.run()

    # Get the age histogram and compute the fit
    ageh = sim['analyzers'][0]
    agehd = ageh.data
    agehh = ageh.hists[-1]
    age_fit = dict(
        age_tests=dict(data=agehd['cum_tests'][:], sim=agehh['tested'], weight=0.0),
        age_diagnoses=dict(data=agehd['cum_diagnoses'][:], sim=agehh['diagnosed'], weight=0.2),
        age_severe=dict(data=agehd['cum_severe'][:], sim=agehh['severe'], weight=0.2),
        age_deaths=dict(data=agehd['cum_deaths'][:], sim=agehh['dead'], weight=1),
        age_yield=dict(data=agehd['cum_diagnoses'][:] / agehd['cum_tests'].values,
                       sim=agehh['diagnosed'] / agehh['tested'], weight=1.0),
    )
    weights = {'cum_diagnoses': 1,
               'cum_deaths': 1,
               'cum_severe': 1,
               'new_diagnoses': 0.01,
               'new_deaths': 0.01,
               'new_severe': 0.01
               }
    fit = sim.compute_fit(custom=age_fit,
                          keys=['cum_diagnoses',
                                'cum_deaths',
                                'cum_severe',
                                'new_diagnoses',
                                'new_deaths',
                                'new_severe'
                                ],
                          weights=weights
                          )

    # Handle output
    if interactive:
        sim.plot()
        fit.plot()
        return sim, fit
    else:
        return fit.mismatch
        # return objective.cost_timeseries_by_age( sim )


if __name__ == '__main__':

    T = sc.tic()

    plot_fit = 1
    use_multisim = 0
    use_safegraph = 1

    # Settings
    reps = 10  # Set multiple runs to average over likelihood
    base_sim = create_sim(use_safegraph=use_safegraph)

    # Plot calibration -- NB, needs refactor
    if use_multisim:
        msim = cv.MultiSim(base_sim, n_runs=reps)
        msim.run(reseed=True, noise=0.0, keep_people=True, par_args={'ncpus': 15})
        sims = msim.sims
        msim.reduce()
        sim = msim.base_sim

        # util_figures.plot_timeseries_by_age(msim)
    else:
        sim = base_sim
        sim.run()
        sims = [sim]
        sim.plot(do_show=True)

    # Do plotting
    # sim, fit = run_sim(sim=sim, use_safegraph=use_safegraph, interactive=True)

    sc.toc(T)
