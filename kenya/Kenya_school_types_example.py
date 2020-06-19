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
    pop_size=20e3,  # Population size
    pop_scale=476,
    pop_type='hybrid',
    pop_infected=10,  # Number of initial infections
    start_day='2020-03-28',
    end_day='2020-12-31',
    beta=0.0125,  # Calibrate overall transmission to this setting
    rel_severe_prob=1.5,
    rel_crit_prob=1.0,
    rel_death_prob=0.5,
    rand_seed=None,  # Random seed
    location='kenya',  # name of the country to model - this sets the correct age distribution and average household size to be used, without this the default age distribution matches the United States of America.
)

n_ICU_beds = 256
# Define the actual scenarios

# Configure the sim
#============CURRENT SCENARIO=============
beta_change_1 = {}
beta_change_1['s'] = 0.0  # schools are completely closed
beta_change_1['w'] = 0.45  # reduction by 1-0.55=0.45
beta_change_1['c'] = 0.45  # reduction by 1-0.55=0.45
beta_change_1['h'] = 1.2  #1.0  # with schools closed and many workers staying at home there is some increase in contact at home - however personal behavior at home like handwashing may be enough to keep this at 1.0

#=======================School opens in August(90)=======

beta_change_2 = {}
beta_change_2['s'] = 0.9  # Scenario 1: schools are reopened and contact there is 90%
beta_change_2['w'] = 0.5  # some increase in contact at work after schools are reopened - decide what that value should be
beta_change_2['c'] = 0.5  # some increase in contact in the community after schools are reopened - decide what that values should be
beta_change_2['h'] = 1.0  #0.8  # with schools reopened household contact may go back to previous levels or even less if people are practicing better habits at home

interventions = []

for lkey, ch in beta_change_1.items():
    interventions.append(cv.change_beta(days=['2020-03-28'], changes=beta_change_1[lkey], layers=lkey, label=f'beta_{lkey}'))

# create a list of the different age ranges in different school types
# for example, the order can be primary school ages, secondary school ages, and tertiary school ages
# each sublist will have two numbers: the youngest age in the school type, followed by the oldest age + 1 in the school type

school_type_ages = []
school_type_ages.append([6, 15])  # primary school ages range from 6 to 14 years old 
school_type_ages.append([15, 19])  # secondary school ages range from 15 to 18 years old
school_type_ages.append([19, 23])  # tertiary school ages range from 19 to 22 years old

# define a dictionary with reopening school interventions on different days by the type of school: the key is the index for the school type and value is the day to restart those schools

school_restart_dict = {}
school_restart_dict[0] = '2020-08-31'  # index 0 for primary schools
school_restart_dict[1] = '2020-08-31'  # index 1 for secondary schools
school_restart_dict[2] = '2020-08-31'  # index 2 for tertiary schools

# add school reopening interventions to the list of interventions
interventions += [cv.reopen_schools(day_schools_closed='2020-03-12', start_day=school_restart_dict)]

# # Run the scenarios -- this block is required for parallel processing on Windows
if __name__ == "__main__":

    sim = cv.Sim(pars=pars)
    sim.initialize(school_type=True, school_type_ages=school_type_ages)
    sim['interventions'] = interventions
    sim.run(verbose=verbose)
