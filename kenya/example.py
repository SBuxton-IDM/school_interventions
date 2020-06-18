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
interv = 1
run_multi = 1

# Set filename if saving
version = 'v0'
date = '2020may15'
folder = 'results'
basename = f'{folder}/kenya_covasim_{date}'

# Configure the sim
# ============CURRENT SCENARIO=============
s_beta_change = 0.0
w_beta_change = 0.45  # reduction by 1-0.55=0.45
c_beta_change = 0.45  # reduction by 1-0.55=0.45
h_beta_change = 1.0

symp_prob = 0.014

which = ['lockdown', 'nolockdown'][0]

pars = dict(
    pop_size=5e3,  # Population size
    pop_scale=476,
    pop_type='hybrid',
    pop_infected=10,  # Number of initial infections
    start_day='2020-03-28',
    end_day='2020-12-31',
    beta=0.0125,  # Calibrate overall transmission to this setting
    rel_severe_prob=1.5,
    rel_crit_prob=1.0,
    rel_death_prob=0.5,
    rand_seed=1,  # Random seed
    location='Kenya',
)

n_ICU_beds = 256
# Define the actual scenarios
start_day = '2020-03-28'


# Define beta interventions
b_ch = sc.objdict()
b_days = ['2020-03-28']
b_ch.s = [0]
b_ch.h = [1]
b_ch.w = [1]
b_ch.c = [.45]

for lkey,ch in b_ch.items():
    interventions = [cv.change_beta(days=b_days, changes=b_ch[lkey], layers=lkey, label=f'beta_{lkey}')]

school_restart_dict = {0: '2020-08-10', 1: '2020-08-10', 2: '2020-08-10', 3: '2020-08-10'}

interventions += [cv.reopen_schools(day_schools_closed='2020-03-12', start_day=school_restart_dict)]
# Run the scenarios -- this block is required for parallel processing on Windows
if __name__ == "__main__":

    sim = cv.Sim(pars=pars)
    sim.initialize(school_type=True, school_type_ages=[[6, 11], [11, 14], [14, 18], [18, 22]])
    sim['interventions'] = interventions
    sim.run(verbose=verbose)
