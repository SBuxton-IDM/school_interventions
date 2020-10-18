# Script to commission sensitivity analysis

import os
import covasim as cv
import create_sim as cs
import sciris as sc
from school_intervention import new_schools
from testing_scenarios import generate_scenarios, generate_testing, scenario

par_inds = (0,20)
pop_size = 2.25e5 # 1e5 2.25e4 2.25e5
batch_size = 16

folder = 'v20201016_225k_sensitivity'
stem = f'batch_first_{par_inds[0]}-{par_inds[1]}'
calibfile = os.path.join(folder, 'pars_cases_begin=75_cases_end=75_re=1.0_prevalence=0.002_yield=0.024_tests=225_pop_size=225000.json')


def baseline(sim, scen, test):
    # Modify scen with test
    for stype, spec in scen.items():
        if spec is not None:
            spec['testing'] = test # dcp probably not needed because deep copied in new_schools

    ns = new_schools(scen)
    sim['interventions'] += [ns]

def children_equally_sus(sim, scen, test):
    # Modify scen with test
    for stype, spec in scen.items():
        if spec is not None:
            spec['testing'] = test # dcp probably not needed because deep copied in new_schools

    prog = sim.pars['prognoses']
    ages = prog['age_cutoffs']
    sus_ORs = prog['sus_ORs']
    sus_ORs[ages<=20] = 1
    prog['sus_ORs'] = sus_ORs

    sim.pars['prognoses'] = prog

    ns = new_schools(scen)
    sim['interventions'] += [ns]

def lower_sens_spec(sim, scen, test):
    if test['is_antigen']:
        test['symp7d_sensitivity'] = 0.9
        test['other_sensitivity'] = 0.6
        test['specificity'] = 0.6
    else:
        test['sensitivity']: 99.8,

    # Modify scen with test
    for stype, spec in scen.items():
        if spec is not None:
            spec['testing'] = test # dcp probably not needed because deep copied in new_schools

    ns = new_schools(scen)
    sim['interventions'] += [ns]

def no_NPI_reduction(sim, scen, test):
    # Modify scen with test
    for stype, spec in scen.items():
        if spec is not None:
            spec['testing'] = test # dcp probably not needed because deep copied in new_schools
            if spec['beta_s'] > 0:
                spec['beta_s'] = 1.5 # Restore to pre-NPI level

    ns = new_schools(scen)
    sim['interventions'] += [ns]

def lower_random_screening(sim, scen, test):
    # Modify scen with test
    for stype, spec in scen.items():
        if spec is not None:
            spec['testing'] = test # dcp probably not needed because deep copied in new_schools
            spec['screen_prob'] = 0.5

    ns = new_schools(scen)
    sim['interventions'] += [ns]

def no_screening(sim, scen, test):
    # Modify scen with test
    for stype, spec in scen.items():
        if spec is not None:
            spec['testing'] = test # dcp probably not needed because deep copied in new_schools
            spec['screen_prob'] = 0

    ns = new_schools(scen)
    sim['interventions'] += [ns]

def lower_coverage(sim, scen, test):
    test['coverage'] = 0.5

    # Modify scen with test
    for stype, spec in scen.items():
        if spec is not None:
            spec['testing'] = test # dcp probably not needed because deep copied in new_schools
            spec['screen_prob'] = 0

    ns = new_schools(scen)
    sim['interventions'] += [ns]

if __name__ == '__main__':
    scenarios = generate_scenarios()
    scenarios = {k:v for k,v in scenarios.items() if k in ['k5']}

    testing = generate_testing()
    testing = {k:v for k,v in testing.items() if k in ['Antigen every 1w teach&staff, PCR f/u', 'Antigen every 2w, PCR f/u']}

    sensitivity = {
        # Baseline
        'baseline': baseline,
        # -------- EASY --------
        # What if younger children aren't less susceptible?
        # --> Change the sensitivity parameters [Need a way to inform parameters from a scenario!]
        'children_equally_sus': children_equally_sus,

        # What if in-field antigen tests have less favorable properties?
        # --> Just change the test sensitivity & specificity
        'lower_sens_spec': lower_sens_spec,

        # For K-5 in particular, masks could be challenging - what if we remove the 25% NPI boost?
        # --> Change beta in the scenario
        'no_NPI_reduction': no_NPI_reduction,

        # Screening coverage < 90% assumed before
        # --> Lower screening coverage is easy, but what if it's non-random.  Some students don't participate? Maybe just try _without_ any screening.
        'lower_random_screening': lower_random_screening,
        'no_screening': no_screening,

        # Lower coverage
        'lower_coverage': lower_coverage,

        # -------- HARD --------
        # Parents/guardians of school children return to work
        # --> Remove and restore edges, HH+students --> work/community
        #'parents_return_to_work',

        # What if cohorting doesn't work all that well due to bussing, after-school care, recess/lunch, or friends?
        # --> Add a % of the old school network back in.  It's _more_ transmission, so would need to balance?  Match R0 (analytical?)
        #'broken_bubbles',

        # How much might it help if some (30%?) of children choose remote learning?
        # Easy enough to have in School some uids persistently at home!
        #'remote_students',
    }
    #sensitivity = {k:v for k,v in sensitivity.items() if k in ['lower_sens_spec']}


    par_list = sc.loadjson(calibfile)[par_inds[0]:par_inds[1]]

    sims = []
    msims = []
    tot = len(scenarios) * len(testing) * len(par_list) * len(scenarios)
    proc = 0

    for senskey, builder in sensitivity.items():
        for eidx, entry in enumerate(par_list):
            par = sc.dcp(entry['pars'])
            par['rand_seed'] = int(entry['index'])

            sim_base = cs.create_sim(par, pop_size=pop_size, folder=folder) # Can I make the par list exterior, create one sim, and copy it for others - faster?
            for sidx, (skey, scen) in enumerate(scenarios.items()):
                for tidx, (tkey, test) in enumerate(testing.items()):
                    sim = sc.dcp(sim_base)

                    sim.label = f'{skey} + {tkey}'
                    sim.key1 = skey
                    sim.key2 = tkey
                    sim.key3 = senskey
                    sim.eidx = eidx
                    sim.scen = scen
                    sim.tscen = test
                    sim.dynamic_par = par

                    # Call the function to build the sensitivity analysis
                    builder(sim, sc.dcp(scen), sc.dcp(test))

                    sims.append(sim)
                    proc += 1

                    if len(sims) == batch_size or proc == tot or (tidx == len(testing)-1 and sidx == len(scenarios)-1 and eidx == len(par_list)-1):
                        print(f'Running sims {proc-len(sims)}-{proc-1} of {tot}')
                        msim = cv.MultiSim(sims)
                        msims.append(msim)
                        msim.run(reseed=False, par_args={'ncpus': 32}, noise=0.0, keep_people=False)
                        sims = []

        print(f'*** Saving after completing {senskey}')
        sims_this_scenario = [s for msim in msims for s in msim.sims if s.key1 == skey]
        msim = cv.MultiSim(sims_this_scenario)
        cv.save(os.path.join(folder, 'msims', f'{stem}_{senskey}.msim'), msim)

    msim = cv.MultiSim.merge(msims)
    cv.save(os.path.join(folder, 'msims', f'{stem}.msim'), msim)
