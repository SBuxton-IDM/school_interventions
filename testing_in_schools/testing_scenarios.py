import os
import covasim as cv
import create_sim as cs
import sciris as sc
from school_intervention import new_schools

par_inds = (0,5)
pop_size = 2.25e5 # 1e5 2.25e4 2.25e5
batch_size = 16

folder = 'v20201015_225k'
stem = f'batch_sm_{par_inds[0]}-{par_inds[1]}'
calibfile = os.path.join(folder, 'pars_cases_begin=75_cases_end=75_re=1.0_prevalence=0.002_yield=0.024_tests=225_pop_size=225000.json')

def scenario(es, ms, hs):
    return {
        'pk': None,
        'es': sc.dcp(es),
        'ms': sc.dcp(ms),
        'hs': sc.dcp(hs),
        'uv': None,
    }

def generate_scenarios():
    ''' Generate scenarios (dictionaries of parameters) for the school intervention '''

    # Increase beta (multiplier) in schools from default of 0.6 to 1.5 (makes normal school R0>1, as to be expected based on global data (Israel), but with Hybrid + 2w PCR testing, R0<1, again as expected from global exemplars.
    ### Create a single sim to get parameters (make_pars is close, but not quite)
    ### sim = cs.create_sim({'rand_seed':0}, pop_size=pop_size, folder=folder)
    ### base_beta_s = sim.pars['beta_layer']['s']
    base_beta_s = 1.5 #

    scns = sc.odict()

    normal = {
        'start_day': '2020-11-02',
        'schedule': 'Full',
        'screen_prob': 0,
        'test_prob': 0, # Amongst those who screen positive
        'screen2pcr': 3, # Days from screening to receiving PCR results
        'trace_prob': 0, # Fraction of newly diagnosed index cases who are traced
        'quar_prob': 0, # Of those reached by contact tracing, this fraction will quarantine
        'ili_prob': 0.002, # Daily ili probability equates to about 10% incidence over the first 3 months of school
        'beta_s': base_beta_s, # No NPI
        'testing': None,
    }
    scns['as_normal'] = scenario(es=normal, ms=normal, hs=normal)

    full_with_countermeasures = {
        'start_day': '2020-11-02',
        'schedule': 'Full',
        'screen_prob': 0.9,
        'test_prob': 0.5, # Amongst those who screen positive
        'screen2pcr': 3, # Days from screening to receiving PCR results
        'trace_prob': 0.75, # Fraction of newly diagnosed index cases who are traced
        'quar_prob': 0.75, # Of those reached by contact tracing, this fraction will quarantine
        'ili_prob': 0.002, # Daily ili probability equates to about 10% incidence over the first 3 months of school
        'beta_s': 0.75 * base_beta_s, # 25% reduction due to NPI
        'testing': None,
    }

    # Add screening and NPI
    scns['with_countermeasures'] = scenario(es=full_with_countermeasures, ms=full_with_countermeasures, hs=full_with_countermeasures)

    # Add hybrid scheduling
    hybrid = sc.dcp(full_with_countermeasures)
    hybrid['schedule'] = 'Hybrid'
    scns['all_hybrid'] = scenario(es=hybrid, ms=hybrid, hs=hybrid)

    # All remote
    remote = {
        'start_day': '2020-11-02',
        'schedule': 'Remote',
        'screen_prob': 0,
        'test_prob': 0,
        'screen2pcr': 3, # Days from screening to receiving PCR results
        'trace_prob': 0,
        'quar_prob': 0,
        'ili_prob': 0,
        'beta_s': 0, # NOTE: No transmission in school layers
        'testing': None,
    }
    scns['all_remote'] = scenario(es=remote, ms=remote, hs=remote)

    scns['k5'] = scenario(es=full_with_countermeasures, ms=remote, hs=remote)

    return scns

def generate_testing():
    # Testing interventions to add
    PCR_1w_prior = [{
        'start_date': '2020-10-26',
        'repeat': None,
        'groups': ['students', 'teachers', 'staff'],
        'coverage': 1,
        'sensitivity': 1,
        'delay': 1,
    }]

    PCR_every_2w_starting_1wprior = [{
        'start_date': '2020-10-26',
        'repeat': 14,
        'groups': ['students', 'teachers', 'staff'],
        'coverage': 1,
        'sensitivity': 1,
        'delay': 1,
    }]

    PCR_every_1w_starting_1wprior = [{
        'start_date': '2020-10-26',
        'repeat': 7,
        'groups': ['students', 'teachers', 'staff'],
        'coverage': 1,
        'sensitivity': 1,
        'delay': 1,
    }]

    PCR_every_1d_starting_1wprior = [{
        'start_date': '2020-10-26',
        'repeat': 1,
        'groups': ['students', 'teachers', 'staff'],
        'coverage': 1,
        'sensitivity': 1,
        'delay': 0, # NOTE: no delay!
    }]

    # pars3_newscenarios ----------------- 
    PCR_every_2w_50cov = [{ # TODO
        'start_date': '2020-11-02',
        'repeat': 14,
        'groups': ['students', 'teachers', 'staff'],
        'coverage': 0.50,
        'sensitivity': 1,
        'delay': 1,
    }]

    PCR_every_1m_15cov = [{
        'start_date': '2020-11-02',
        'repeat': 30,
        'groups': ['students', 'teachers', 'staff'],
        'coverage': 0.15,
        'sensitivity': 1,
        'delay': 1,
    }]

    Antigen_every_1w_starting_1wprior_teachersstaff_PCR_followup = [{
        'start_date': '2020-10-26',
        'repeat': 7,
        'groups': ['teachers', 'staff'], # No students
        'coverage': 1,
        'is_antigen': True,
        'symp7d_sensitivity': 0.971, # https://www.fda.gov/media/141570/download
        'other_sensitivity': 0.90, # Modeling assumption
        'specificity': 0.985, # https://www.fda.gov/media/141570/download
        'PCR_followup_perc': 1,
        'PCR_followup_delay': 3,
    }]


    Antigen_every_2w_starting_1wprior_all_PCR_followup = [{
        'start_date': '2020-10-26',
        'repeat': 14,
        'groups': ['students', 'teachers', 'staff'], # No students
        'coverage': 1,
        'is_antigen': True,
        'symp7d_sensitivity': 0.971, # https://www.fda.gov/media/141570/download
        'other_sensitivity': 0.90, # Modeling assumption
        'specificity': 0.985, # https://www.fda.gov/media/141570/download
        'PCR_followup_perc': 1,
        'PCR_followup_delay': 3,
    }]

    Antigen_every_2w_starting_1wprior_all_no_followup = [{
        'start_date': '2020-10-26',
        'repeat': 14,
        'groups': ['students', 'teachers', 'staff'], # No students
        'coverage': 1,
        'is_antigen': True,
        'symp7d_sensitivity': 0.971, # https://www.fda.gov/media/141570/download
        'other_sensitivity': 0.90, # Modeling assumption
        'specificity': 0.985, # https://www.fda.gov/media/141570/download
        'PCR_followup_perc': 0,
        'PCR_followup_delay': 0, # Does not matter with no PCR follow-up
    }]


    return {
        'None': None,
        'PCR 1w prior': PCR_1w_prior,
        'PCR every 2w': PCR_every_2w_starting_1wprior,
        'PCR every 1w': PCR_every_1w_starting_1wprior,
        'PCR every 1d': PCR_every_1d_starting_1wprior,
        'PCR every 2w 50%': PCR_every_2w_50cov,
        #'PCR every 1m 15%': PCR_every_1m_15cov,
        'Antigen every 1w teach&staff, PCR f/u': Antigen_every_1w_starting_1wprior_teachersstaff_PCR_followup,
        'Antigen every 2w, PCR f/u': Antigen_every_2w_starting_1wprior_all_PCR_followup,
        'Antigen every 2w, no f/u': Antigen_every_2w_starting_1wprior_all_no_followup,
    }

if __name__ == '__main__':
    scenarios = generate_scenarios()
    scenarios = {k:v for k,v in scenarios.items() if k in ['with_countermeasures']}

    testing = generate_testing()
    testing = {k:v for k,v in testing.items() if k in ['None', 'PCR every 1w', 'Antigen every 2w, PCR f/u']}

    # Hand tuned and replicates instead of optuna pars - testing will perturb the rand seed before schools open anyway
    pars_v1 = { # 100k pop
        'pop_infected': 160,
        'clip_edges': 0.65,
        'change_beta': 0.525,
    }

    pars_v2 = { # Updated v2 pars achieve lower prevalence (0.2% as opposed to closer to 0.5% with v1) (100kpop)
        'pop_infected': 90,
        'clip_edges': 0.65,
        'change_beta': 0.62,
    }

    # Now ignoring pars_v1 an pars_v2, using calibrated values instead:
    par_list = sc.loadjson(calibfile)[par_inds[0]:par_inds[1]]

    sims = []
    msims = []
    tot = len(scenarios) * len(testing) * len(par_list)
    proc = 0
    for skey, scen in scenarios.items():
        for tidx, (tkey, test) in enumerate(testing.items()):
            for eidx, entry in enumerate(par_list):
                par = sc.dcp(entry['pars'])
                par['rand_seed'] = int(entry['index'])

                sim = cs.create_sim(par, pop_size=pop_size, folder=folder)

                sim.label = f'{skey} + {tkey}'
                sim.key1 = skey
                sim.key2 = tkey
                sim.scen = scen
                sim.tscen = test
                sim.dynamic_par = par

                # Modify scen with test
                this_scen = sc.dcp(scen)
                for stype, spec in this_scen.items():
                    if spec is not None:
                        spec['testing'] = sc.dcp(test) # dcp probably not needed because deep copied in new_schools

                ns = new_schools(this_scen)
                sim['interventions'] += [ns]
                sims.append(sim)
                proc += 1

                if len(sims) == batch_size or proc == tot or (tidx == len(testing)-1 and eidx == len(par_list)-1):
                    print(f'Running sims {proc-len(sims)}-{proc-1} of {tot}')
                    msim = cv.MultiSim(sims)
                    msims.append(msim)
                    msim.run(reseed=False, par_args={'ncpus': 32}, noise=0.0, keep_people=False)
                    sims = []

        print(f'*** Saving after completing {skey}')
        sims_this_scenario = [s for msim in msims for s in msim.sims if s.key1 == skey]
        msim = cv.MultiSim(sims_this_scenario)
        cv.save(os.path.join(folder, 'msims', f'{stem}_{skey}.msim'), msim)

    msim = cv.MultiSim.merge(msims)
    cv.save(os.path.join(folder, 'msims', f'{stem}.msim'), msim)
