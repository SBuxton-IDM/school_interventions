'''
Simple script for running the Covid-19 agent-based model
'''

print('Importing...')
import sciris as sc
import covasim as cv

print('Configuring...')

# Run options
do_plot = 1
do_save = 1
do_show = 1
verbose = 1
interv  = 1
run_multi = 1

# Set filename if saving
version  = 'v0'
date     = '2020may15'
folder   = 'results'
basename = f'{folder}/kenya_covasim_{date}'

# Configure the sim
#============CURRENT SCENARIO=============
s_beta_change = 0.0
w_beta_change = 0.45 #reduction by 1-0.55=0.45
c_beta_change = 0.45 #reduction by 1-0.55=0.45
h_beta_change = 1.0
#=======================School opens in June and August(90)=======

s_beta_change2 = 0.9#0.20
w_beta_change2 = 0.50#0.54
c_beta_change2 = 0.50#0.54
h_beta_change2 = 0.80#0.78

#=======================School opens in June and August(50)=======

s_beta_change2b = 0.5#0.20
w_beta_change2b = 0.50#0.54
c_beta_change2b = 0.50#0.54
h_beta_change2b = 0.80#0.78

#=====================School opening candidate class===========
s_beta_change3 = 0.20#0.20
w_beta_change3 = 0.50#0.54
c_beta_change3 = 0.50#0.54
h_beta_change3 = 0.90#0.78

#=====================Candidate then the rest===========
s_beta_change4 = 0.90#0.20
w_beta_change4 = 0.50#0.54
c_beta_change4 = 0.50#0.54
h_beta_change4 = 0.80#0.78


symp_prob = 0.014

which = ['lockdown', 'nolockdown'][0]

basepars = dict(
    pop_size     = 5e3, # Population size
    pop_scale    = 476,
    pop_type     = 'hybrid',
    pop_infected = 10,     # Number of initial infections
    start_day    = '2020-03-28',
    end_day      = '2020-12-31',
    beta         = 0.0125 , # Calibrate overall transmission to this setting
    rel_severe_prob= 1.5,
    rel_crit_prob=1.0,
    rel_death_prob=0.5,
    location='Kenya',
)

# Scenario metaparameters
metapars = dict(
    n_runs    = 1, # Number of parallel runs; change to 3 for quick, 11 for real
    noise     = 0.1, # Use noise, optionally
    noisepar  = 'beta',
    rand_seed    = 1,     # Random seed
    quantiles = {'low':0.1, 'high':0.9},
)

n_ICU_beds   = 256
# Define the actual scenarios
start_day = '2020-03-28'
scenarios = {'June': {
              'name':'Open School June & August(90)',
              'pars': {
                  'interventions': [
                    cv.change_beta(days=['2020-03-28'], changes=[s_beta_change],  layers=['s'], do_plot=s_beta_change<1.0),
                    # cv.change_beta(days=['2020-06-02'], changes=[s_beta_change2], layers=['s'], do_plot=s_beta_change2<1.0),
                    # cv.change_beta(days=['2020-08-14'], changes=[s_beta_change], layers=['s'], do_plot=s_beta_change<1.0),
                    cv.change_beta(days=['2020-08-31'], changes=[s_beta_change2], layers=['s'], do_plot=s_beta_change2<1.0),
                    # cv.change_beta(days=['2020-10-23'], changes=[s_beta_change], layers=['s'], do_plot=s_beta_change<1.0),

                    cv.change_beta(days=['2020-03-28'], changes=[h_beta_change],  layers=['h'], do_plot=h_beta_change<1.0),
                    # cv.change_beta(days=['2020-06-02'], changes=[h_beta_change2], layers=['h'], do_plot=h_beta_change2<1.0),
                    # cv.change_beta(days=['2020-08-14'], changes=[h_beta_change], layers=['h'], do_plot=h_beta_change<1.0),
                    cv.change_beta(days=['2020-08-31'], changes=[h_beta_change2], layers=['h'], do_plot=h_beta_change2<1.0),
                    # cv.change_beta(days=['2020-10-23'], changes=[h_beta_change], layers=['h'], do_plot=h_beta_change<1.0),

                    cv.change_beta(days=['2020-03-28'], changes=[w_beta_change],  layers=['w'], do_plot=w_beta_change<1.0),
                    # cv.change_beta(days=['2020-06-02'], changes=[w_beta_change2], layers=['w'], do_plot=w_beta_change2<1.0),
                    # cv.change_beta(days=['2020-08-14'], changes=[w_beta_change], layers=['w'], do_plot=w_beta_change<1.0),
                    cv.change_beta(days=['2020-08-31'], changes=[w_beta_change2], layers=['w'], do_plot=w_beta_change2<1.0),
                    # cv.change_beta(days=['2020-10-23'], changes=[w_beta_change], layers=['w'], do_plot=w_beta_change<1.0),

                    cv.change_beta(days=['2020-03-28'], changes=[c_beta_change],  layers=['c'], do_plot=c_beta_change<1.0),
                    # cv.change_beta(days=['2020-06-02'], changes=[c_beta_change2], layers=['c'], do_plot=c_beta_change2<1.0),
                    # cv.change_beta(days=['2020-08-14'], changes=[c_beta_change], layers=['c'], do_plot=c_beta_change<1.0),
                    cv.change_beta(days=['2020-08-31'], changes=[c_beta_change2], layers=['c'], do_plot=c_beta_change2<1.0),
                    # cv.change_beta(days=['2020-10-23'], changes=[c_beta_change], layers=['c'], do_plot=c_beta_change<1.0)
                    ],
                  }
              },
              'Progressive': {
              'name':'Candidate then the rest',
              'pars': {
                  'interventions': [
                    cv.change_beta(days=['2020-03-28'], changes=[s_beta_change],  layers=['s'], do_plot=s_beta_change<1.0),
                    # cv.change_beta(days=['2020-06-02'], changes=[s_beta_change3], layers=['s'], do_plot=s_beta_change3<1.0),
                    # cv.change_beta(days=['2020-08-14'], changes=[s_beta_change], layers=['s'], do_plot=s_beta_change<1.0),
                    cv.change_beta(days=['2020-08-31'], changes=[s_beta_change4], layers=['s'], do_plot=s_beta_change4<1.0),
                    # cv.change_beta(days=['2020-10-23'], changes=[s_beta_change], layers=['s'], do_plot=s_beta_change<1.0),

                    cv.change_beta(days=['2020-03-28'], changes=[h_beta_change],  layers=['h'], do_plot=h_beta_change<1.0),
                    # cv.change_beta(days=['2020-06-02'], changes=[h_beta_change3], layers=['h'], do_plot=h_beta_change3<1.0),
                    # cv.change_beta(days=['2020-08-14'], changes=[h_beta_change], layers=['h'], do_plot=h_beta_change<1.0),
                    cv.change_beta(days=['2020-08-31'], changes=[h_beta_change4], layers=['h'], do_plot=h_beta_change4<1.0),
                    # cv.change_beta(days=['2020-10-23'], changes=[h_beta_change], layers=['h'], do_plot=h_beta_change<1.0),

                    cv.change_beta(days=['2020-03-28'], changes=[w_beta_change],  layers=['w'], do_plot=w_beta_change<1.0),
                    # cv.change_beta(days=['2020-06-02'], changes=[w_beta_change3], layers=['w'], do_plot=w_beta_change3<1.0),
                    # cv.change_beta(days=['2020-08-14'], changes=[w_beta_change], layers=['w'], do_plot=w_beta_change<1.0),
                    cv.change_beta(days=['2020-08-31'], changes=[w_beta_change4], layers=['w'], do_plot=w_beta_change4<1.0),
                    # cv.change_beta(days=['2020-10-23'], changes=[w_beta_change], layers=['w'], do_plot=w_beta_change<1.0),

                    cv.change_beta(days=['2020-03-28'], changes=[c_beta_change],  layers=['c'], do_plot=c_beta_change<1.0),
                    # cv.change_beta(days=['2020-06-02'], changes=[c_beta_change3], layers=['c'], do_plot=c_beta_change3<1.0),
                    # cv.change_beta(days=['2020-08-14'], changes=[c_beta_change], layers=['c'], do_plot=c_beta_change<1.0),
                    cv.change_beta(days=['2020-08-31'], changes=[c_beta_change4], layers=['c'], do_plot=c_beta_change4<1.0),
                    # cv.change_beta(days=['2020-10-23'], changes=[c_beta_change], layers=['c'], do_plot=c_beta_change<1.0)
                    ],
                  }
              },
              'Juneb': {
              'name':'Open School June & August(50)',
              'pars': {
                  'interventions': [
                    cv.change_beta(days=['2020-03-28'], changes=[s_beta_change],  layers=['s'], do_plot=s_beta_change<1.0),
                    # cv.change_beta(days=['2020-06-02'], changes=[s_beta_change2b], layers=['s'], do_plot=s_beta_change2b<1.0),
                    # cv.change_beta(days=['2020-08-14'], changes=[s_beta_change], layers=['s'], do_plot=s_beta_change<1.0),
                    cv.change_beta(days=['2020-08-31'], changes=[s_beta_change2b], layers=['s'], do_plot=s_beta_change2b<1.0),
                    # cv.change_beta(days=['2020-10-23'], changes=[s_beta_change], layers=['s'], do_plot=s_beta_change<1.0),

                    cv.change_beta(days=['2020-03-28'], changes=[h_beta_change],  layers=['h'], do_plot=h_beta_change<1.0),
                    # cv.change_beta(days=['2020-06-02'], changes=[h_beta_change2b], layers=['h'], do_plot=h_beta_change2b<1.0),
                    # cv.change_beta(days=['2020-08-14'], changes=[h_beta_change], layers=['h'], do_plot=h_beta_change<1.0),
                    cv.change_beta(days=['2020-08-31'], changes=[h_beta_change2b], layers=['h'], do_plot=h_beta_change2b<1.0),
                    # cv.change_beta(days=['2020-10-23'], changes=[h_beta_change], layers=['h'], do_plot=h_beta_change<1.0),

                    cv.change_beta(days=['2020-03-28'], changes=[w_beta_change],  layers=['w'], do_plot=w_beta_change<1.0),
                    # cv.change_beta(days=['2020-06-02'], changes=[w_beta_change2b], layers=['w'], do_plot=w_beta_change2b<1.0),
                    # cv.change_beta(days=['2020-08-14'], changes=[w_beta_change], layers=['w'], do_plot=w_beta_change<1.0),
                    cv.change_beta(days=['2020-08-31'], changes=[w_beta_change2b], layers=['w'], do_plot=w_beta_change2b<1.0),
                    # cv.change_beta(days=['2020-10-23'], changes=[w_beta_change], layers=['w'], do_plot=w_beta_change<1.0),

                    cv.change_beta(days=['2020-03-28'], changes=[c_beta_change],  layers=['c'], do_plot=c_beta_change<1.0),
                    # cv.change_beta(days=['2020-06-02'], changes=[c_beta_change2b], layers=['c'], do_plot=c_beta_change2b<1.0),
                    # cv.change_beta(days=['2020-08-14'], changes=[c_beta_change], layers=['c'], do_plot=c_beta_change<1.0),
                    cv.change_beta(days=['2020-08-31'], changes=[c_beta_change2b], layers=['c'], do_plot=c_beta_change2b<1.0),
                    # cv.change_beta(days=['2020-10-23'], changes=[c_beta_change], layers=['c'], do_plot=c_beta_change<1.0)
                    ],
                  }
              },
            'Candidate': {
              'name':'Candidate Only',
              'pars': {
                  'interventions': [
                    cv.change_beta(days=['2020-03-28'], changes=[s_beta_change],  layers=['s'], do_plot=s_beta_change<1.0),
                    # cv.change_beta(days=['2020-06-02'], changes=[s_beta_change3], layers=['s'], do_plot=s_beta_change3<1.0),
                    # cv.change_beta(days=['2020-08-14'], changes=[s_beta_change], layers=['s'], do_plot=s_beta_change<1.0),
                    cv.change_beta(days=['2020-08-31'], changes=[s_beta_change3], layers=['s'], do_plot=s_beta_change3<1.0),
                    # cv.change_beta(days=['2020-10-23'], changes=[s_beta_change], layers=['s'], do_plot=s_beta_change<1.0),

                    cv.change_beta(days=['2020-03-28'], changes=[h_beta_change],  layers=['h'], do_plot=h_beta_change<1.0),
                    # cv.change_beta(days=['2020-06-02'], changes=[h_beta_change3], layers=['h'], do_plot=h_beta_change3<1.0),
                    # cv.change_beta(days=['2020-08-14'], changes=[h_beta_change], layers=['h'], do_plot=h_beta_change<1.0),
                    cv.change_beta(days=['2020-08-31'], changes=[h_beta_change3], layers=['h'], do_plot=h_beta_change3<1.0),
                    # cv.change_beta(days=['2020-10-23'], changes=[h_beta_change], layers=['h'], do_plot=h_beta_change<1.0),

                    cv.change_beta(days=['2020-03-28'], changes=[w_beta_change],  layers=['w'], do_plot=w_beta_change<1.0),
                    # cv.change_beta(days=['2020-06-02'], changes=[w_beta_change3], layers=['w'], do_plot=w_beta_change3<1.0),
                    # cv.change_beta(days=['2020-08-14'], changes=[w_beta_change], layers=['w'], do_plot=w_beta_change<1.0),
                    cv.change_beta(days=['2020-08-31'], changes=[w_beta_change3], layers=['w'], do_plot=w_beta_change3<1.0),
                    # cv.change_beta(days=['2020-10-23'], changes=[w_beta_change], layers=['w'], do_plot=w_beta_change<1.0),

                    cv.change_beta(days=['2020-03-28'], changes=[c_beta_change],  layers=['c'], do_plot=c_beta_change<1.0),
                    # cv.change_beta(days=['2020-06-02'], changes=[c_beta_change3], layers=['c'], do_plot=c_beta_change3<1.0),
                    # cv.change_beta(days=['2020-08-14'], changes=[c_beta_change], layers=['c'], do_plot=c_beta_change<1.0),
                    cv.change_beta(days=['2020-08-31'], changes=[c_beta_change3], layers=['c'], do_plot=c_beta_change3<1.0),
                    # cv.change_beta(days=['2020-10-23'], changes=[c_beta_change], layers=['c'], do_plot=c_beta_change<1.0)
                    ],
                  }
              },
              
              'Current': {
              'name':'Current Scenario',
              'pars': {
                  'interventions':  [
                    cv.change_beta(days=['2020-03-28'], changes=[s_beta_change], layers=['s'], do_plot=s_beta_change<1.0),
                    cv.change_beta(days=['2020-03-28'], changes=[c_beta_change], layers=['c'], do_plot=c_beta_change<1.0),
                    cv.change_beta(days=['2020-03-28'], changes=[h_beta_change], layers=['h'], do_plot=h_beta_change<1.0),
                    cv.change_beta(days=['2020-03-28'], changes=[w_beta_change], layers=['w'], do_plot=w_beta_change<1.0)],
                  }
              },
            
             }
# Run the scenarios -- this block is required for parallel processing on Windows
if __name__ == "__main__":

    scens = cv.Scenarios(basepars=basepars, metapars=metapars, scenarios=scenarios)
    scens.run(verbose=verbose)
    #to_plot = cv.get_scen_plots()
    ##to_plot['Effective reproductive number'] = ['r_eff']
    if do_plot:
        print('Plotting...')

    # Plotting
    to_plot = sc.objdict({
        #'Diagnoses': ['cum_diagnoses'],
        #'Cumulative infections': ['cum_infections'],
        #'Hospital Beds Utilization': ['new_severe'],
        #'ICU Beds Utilization': ['new_critical'],
        #'Cumulative Deaths': ['cum_deaths'],
        #'Daily Deaths': ['new_deaths'],
        #'New infections per day': ['new_infections'],
        'Effective reproduction number': ['r_eff'],
        #'New infections per day ': ['new_diagnoses'],
    })
    fig = scens.plot(to_plot=to_plot, do_save=do_save, grid=True, do_show=do_show, fig_path=f'{basename}_{which}.png',
             legend_args={'loc': 'upper left'}, axis_args={'hspace': 0.4, 'left': 0.11, 'top': 0.90})
    #if do_plot:
        ##fig1 = scens.plot(do_show=do_show, to_plot=to_plot)
        #fig1 = scens.plot(to_plot=to_plot, do_save=do_save, do_show=do_show, fig_path=f'{basename}_{which}.png',
             #legend_args={'loc': 'upper left'}, axis_args={'hspace': 0.4})
