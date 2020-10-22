'''
Main script to commission sensitivity analysis -- run this and then use to run
additional figure results.
'''

import os
import numpy as np
import pandas as pd
import sciris as sc
import covasim as cv
import synthpops as sp
import covasim_schools as cvsch
import create_sim as cs
from testing_scenarios import generate_scenarios, generate_testing
cv.check_save_version('1.7.2', comments={'SynthPops':sc.gitinfo(sp.__file__)})

par_inds = (0,3)
pop_size = 2.25e5 # 1e5 2.25e4 2.25e5
batch_size = 24

folder = 'v20201016_225k_sensitivity'
stem = f'batch_v2_{par_inds[0]}-{par_inds[1]}'
calibfile = os.path.join(folder, 'pars_cases_begin=75_cases_end=75_re=1.0_prevalence=0.002_yield=0.024_tests=225_pop_size=225000.json')


def baseline(sim, scen, test):
    # Modify scen with test
    for stype, spec in scen.items():
        if spec is not None:
            spec['testing'] = test # dcp probably not needed because deep copied in new_schools

    sm = cvsch.schools_manager(scen)
    sim['interventions'] += [sm]

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

    sm = cvsch.schools_manager(scen)
    sim['interventions'] += [sm]

def lower_sens_spec(sim, scen, test):
    if test is not None and 'is_antigen' in test[0] and test[0]['is_antigen']:
        test[0]['symp7d_sensitivity'] = 0.9
        test[0]['other_sensitivity'] = 0.6
        test[0]['specificity'] = 0.6
    elif test is not None:
        test[0]['sensitivity']: 0.995

    # Modify scen with test
    for stype, spec in scen.items():
        if spec is not None:
            spec['testing'] = test # dcp probably not needed because deep copied in new_schools

    sm = cvsch.schools_manager(scen)
    sim['interventions'] += [sm]

def no_NPI_reduction(sim, scen, test):
    # Modify scen with test
    for stype, spec in scen.items():
        if spec is not None:
            spec['testing'] = test # dcp probably not needed because deep copied in new_schools
            if spec['beta_s'] > 0:
                spec['beta_s'] = 1.5 # Restore to pre-NPI level

    sm = cvsch.schools_manager(scen)
    sim['interventions'] += [sm]

def lower_random_screening(sim, scen, test):
    # Modify scen with test
    for stype, spec in scen.items():
        if spec is not None:
            spec['testing'] = test # dcp probably not needed because deep copied in new_schools
            spec['screen_prob'] = 0.5

    sm = cvsch.schools_manager(scen)
    sim['interventions'] += [sm]

def no_screening(sim, scen, test):
    # Modify scen with test
    for stype, spec in scen.items():
        if spec is not None:
            spec['testing'] = test # dcp probably not needed because deep copied in new_schools
            spec['screen_prob'] = 0

    sm = cvsch.schools_manager(scen)
    sim['interventions'] += [sm]

def lower_coverage(sim, scen, test):
    if test is not None:
        test[0]['coverage'] = 0.5

    # Modify scen with test
    for stype, spec in scen.items():
        if spec is not None:
            spec['testing'] = test # dcp probably not needed because deep copied in new_schools

    sm = cvsch.schools_manager(scen)
    sim['interventions'] += [sm]

def parents_return_to_work(sim, scen, test):
    # Modify scen with test
    for stype, spec in scen.items():
        if spec is not None:
            spec['testing'] = test # dcp probably not needed because deep copied in new_schools

    sm = cvsch.schools_manager(scen)
    sim['interventions'] += [sm]

    # Different random path if ce not placed in the right order
    try:
        ce_idx = next(idx for idx,i in enumerate(sim['interventions']) if i.label == 'close_work_community')
    except StopIteration:
        print('Error: could not find intervetion with name "close_work_community" in list of interventions')
        exit()
    # TODO: Dig out date and changes from previous intervention instead of hard coding
    ce = cv.clip_edges(days=['2020-09-01', '2020-11-02'], changes=[0.65, 0.80], layers=['w', 'c'], label='close_and_reopen_work_community')
    sim['interventions'][ce_idx] = ce

def broken_bubbles(sim, scen, test):
    frac_edges_to_rewire = 0.5
    np.random.seed(1)

    # Modify scen with test
    for stype, spec in scen.items():
        if spec is not None:
            spec['testing'] = test # dcp probably not needed because deep copied in new_schools

    school_contacts = []

    sdf = sim.people.contacts['s'].to_df()
    student_flag = np.array(sim.people.student_flag, dtype=bool)
    sdf['p1_student'] = student_flag[sdf['p1']]
    sdf['p2_student'] = student_flag[sdf['p1']]
    school_types = sim.people.school_types
    for school_type, scids in school_types.items():
        for school_id in scids:
            uids = sim.people.schools[school_id] # Dict with keys of school_id and values of uids in that school
            edges_this_school = sdf.loc[ ((sdf['p1'].isin(uids)) | (sdf['p2'].isin(uids))) ]
            if scen[school_type] is None:
                school_contacts.append(edges_this_school)
            else:
                student_to_student_edge_bool = ( edges_this_school['p1_student'] & edges_this_school['p2_student'] )
                student_to_student_edges = edges_this_school.loc[ student_to_student_edge_bool ]
                inds_to_rewire = np.random.choice(student_to_student_edges.index, size=int(frac_edges_to_rewire*student_to_student_edges.shape[0]), replace=False)
                inds_to_keep = np.setdiff1d(student_to_student_edges.index, inds_to_rewire)

                edges_to_rewire = student_to_student_edges.loc[inds_to_rewire]
                stublist = np.concatenate(( edges_to_rewire['p1'], edges_to_rewire['p2'] ))

                p1_inds = np.random.choice(len(stublist), size=len(stublist)//2, replace=False)
                p2_inds = np.setdiff1d(range(len(stublist)), p1_inds)
                p1 = stublist[p1_inds]
                p2 = stublist[p2_inds]
                new_edges = pd.DataFrame({'p1':p1, 'p2':p2})
                new_edges['beta'] = 1.0
                # Remove self loops
                new_edges = new_edges.loc[new_edges['p1'] != new_edges['p2']]

                rewired_student_to_student_edges = pd.concat([
                    student_to_student_edges.loc[inds_to_keep, ['p1', 'p2', 'beta']], # Keep these
                    new_edges])

                #print(f'During rewiring, the number of student-student edges went from {student_to_student_edges.shape[0]} to {rewired_student_to_student_edges.shape[0]}')

                other_edges = edges_this_school.loc[ (~edges_this_school['p1_student']) | (~edges_this_school['p2_student']) ]
                rewired_edges_this_school = pd.concat([rewired_student_to_student_edges, other_edges])
                school_contacts.append(rewired_edges_this_school)


    all_school_contacts = pd.concat(school_contacts)
    sim.people.contacts['s'] = cv.Layer().from_df(all_school_contacts)

    sm = cvsch.schools_manager(scen)
    sim['interventions'] += [sm]


if __name__ == '__main__':
    scenarios = generate_scenarios()
    #scenarios = {k:v for k,v in scenarios.items() if k in ['with_countermeasures', 'all_hybrid', 'k5', 'all_remote']}
    scenarios = {k:v for k,v in scenarios.items() if k in ['k5']}

    testing = generate_testing()
    #testing = {k:v for k,v in testing.items() if k in ['None', 'PCR every 2w', 'Antigen every 1w teach&staff, PCR f/u', 'Antigen every 2w, PCR f/u']}
    testing = {k:v for k,v in testing.items() if k in ['Antigen every 2w, PCR f/u']}

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
        'parents_return_to_work': parents_return_to_work,

        # What if cohorting doesn't work all that well due to bussing, after-school care, recess/lunch, or friends?
        # --> Add a % of the old school network back in.  It's _more_ transmission, so would need to balance?  Match R0 (analytical?)
        'broken_bubbles': broken_bubbles,

        # How much might it help if some (30%?) of children choose remote learning?
        # Easy enough to have in School some uids persistently at home!
        #'remote_students',
    }

    # Select a subset, if desired:
    sensitivity = {k:v for k,v in sensitivity.items() if k in ['baseline', 'broken_bubbles']}

    par_list = sc.loadjson(calibfile)[par_inds[0]:par_inds[1]]

    sims = []
    msims = []
    tot = len(scenarios) * len(testing) * len(par_list) * len(sensitivity)
    proc = 0

    # Save time by pre-generating the base simulations
    base_sims = []
    for eidx, entry in enumerate(par_list):
        par = sc.dcp(entry['pars'])
        par['rand_seed'] = int(entry['index'])
        base_sims.append( cs.create_sim(par, pop_size=pop_size, folder=folder) )

    for senskey, builder in sensitivity.items():
        for eidx, entry in enumerate(par_list):
            par = entry['pars']
            par['rand_seed'] = int(entry['index'])
            sim_base = base_sims[eidx]

            for sidx, (skey, scen) in enumerate(scenarios.items()):
                for tidx, (tkey, test) in enumerate(testing.items()):
                    sim = sim_base.copy()

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

        fn = os.path.join(folder, 'msims', f'{stem}_{senskey}.msim')
        print(f'*** Saving to {fn} after completing {senskey}')
        sims_this_scenario = [s for msim in msims for s in msim.sims if s.key3 == senskey]
        msim = cv.MultiSim(sims_this_scenario)
        cv.save(fn, msim)

    msim = cv.MultiSim.merge(msims)
    cv.save(os.path.join(folder, 'msims', f'{stem}.msim'), msim)
