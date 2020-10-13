import os
import covasim as cv
import create_sim as cs
import sciris as sc
from school_intervention import new_schools

par_inds = (5,10)
pop_size = 2.25e5 # 1e5 2.25e4 2.25e5
batch_size = 16

folder = 'v20201013_225k_v2'
stem = f'pars_{par_inds[0]}-{par_inds[1]}'
calibfile = os.path.join(folder, 'pars_cases_begin=75_cases_end=75_re=1.0_prevalence=0.002_yield=0.024_tests=225_v2_pop_size=225000.json')

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

    # Create a single sim to get parameters (make_pars is close, but not quite)
    sim = cs.create_sim({'rand_seed':0}, pop_size=pop_size, folder=folder)
    base_beta_s = sim.pars['beta_layer']['s']

    scns = sc.odict()

    remote = {
        'start_day': '2020-11-02',
        'schedule': 'Remote',
        'screen_prob': 0,
        'test_prob': 0,
        'trace_prob': 0,
        'quar_prob': 0,
        'ili_prob': 0,
        'beta_s': 0, # NOTE: No transmission in school layers
        'testing': None,
    }

    normal = {
        'start_day': '2020-11-02',
        'schedule': 'Full',
        'screen_prob': 0,
        'test_prob': 0, # Amongst those who screen positive
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
        'trace_prob': 0.75, # Fraction of newly diagnosed index cases who are traced
        'quar_prob': 0.75, # Of those reached by contact tracing, this fraction will quarantine
        'ili_prob': 0.002, # Daily ili probability equates to about 10% incidence over the first 3 months of school
        'beta_s': 0.75 * base_beta_s, # 25% reduction due to NPI
        'testing': None,
    }

    # Add screening and NPI
    scns['with_screening'] = scenario(es=full_with_countermeasures, ms=full_with_countermeasures, hs=full_with_countermeasures)

    # Add hybrid scheduling
    hybrid = sc.dcp(full_with_countermeasures)
    hybrid['schedule'] = 'Hybrid'
    scns['all_hybrid'] = scenario(es=hybrid, ms=hybrid, hs=hybrid)

    # All remote
    scns['all_remote'] = scenario(es=remote, ms=remote, hs=remote)

    return scns

def generate_testing():
    # Testing interventions to add
    PCR_1w_prior = [{
        'start_date': '2020-10-26',
        'repeat': None,
        'groups': ['students', 'teachers', 'staff'],
        'coverage': 1,
        'sensitivity': 1,
        'specificity': 1,
        'delay': 1,
    }]

    PCR_every_2w_starting_1wprior = [{
        'start_date': '2020-10-26',
        'repeat': 14,
        'groups': ['students', 'teachers', 'staff'],
        'coverage': 1,
        'sensitivity': 1,
        'specificity': 1,
        'delay': 1,
    }]

    PCR_every_1w_starting_1wprior = [{
        'start_date': '2020-10-26',
        'repeat': 7,
        'groups': ['students', 'teachers', 'staff'],
        'coverage': 1,
        'sensitivity': 1,
        'specificity': 1,
        'delay': 1,
    }]

    PCR_every_1m_15cov = [{
        'start_date': '2020-11-02',
        'repeat': 30,
        'groups': ['students', 'teachers', 'staff'],
        'coverage': 0.15,
        'sensitivity': 1,
        'specificity': 1,
        'delay': 1,
    }]

    PCR_every_2w_50cov = [{ # TODO
        'start_date': '2020-11-02',
        'repeat': 14,
        'groups': ['students', 'teachers', 'staff'],
        'coverage': 0.50,
        'sensitivity': 1,
        'specificity': 1,
        'delay': 1,
    }]

    # TODO: Propoer antigen testing in covasim
    Antigen_every_1w_starting_1wprior_staff = [{
        'start_date': '2020-10-26',
        'repeat': 7,
        'groups': ['teachers', 'staff'], # No students
        'coverage': 1,
        'sensitivity': 0.8, # Lower sensitiviy, 80% is a modeling assumption as the true sensitivity is unknown at this time.  Should be high when viral load is high, but unsure how low at lower viral loads.
        'specificity': 0.9, # 90% specificity is a modeling assumption
        'delay': 0,          # No delay
    }]

    PCR_every_1d_starting_1wprior = [{
        'start_date': '2020-10-26',
        'repeat': 1,
        'groups': ['students', 'teachers', 'staff'],
        'coverage': 1,
        'sensitivity': 1,
        'specificity': 1,
        'delay': 0, # NOTE: no delay!
    }]

    return {
        'None': None,
        'PCR 1w prior': PCR_1w_prior,
        'PCR every 2w': PCR_every_2w_starting_1wprior,
        'PCR every 1w': PCR_every_1w_starting_1wprior,
        'PCR every 1d': PCR_every_1d_starting_1wprior,
        #'PCR every 1m 15%': PCR_every_1m_15cov,
        #'PCR every 2w 50%': PCR_every_2w_50cov,
        'Antigen every 1w teach&staff': Antigen_every_1w_starting_1wprior_staff,
    }

if __name__ == '__main__':
    scenarios = generate_scenarios()
    #scenarios = {k:v for k,v in scenarios.items() if k in ['all_remote']}

    testing = generate_testing()
    #testing = {k:v for k,v in testing.items() if k in ['None', 'PCR every 1w', 'PCR every 1d']}

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
                        spec['beta_s'] = 1.0 # Increase beta (multiplier) in schools from default of 0.6 to 1.0 (makes normal school R0>1, as to be expected based on global data (Israel), but with Hybrid + 2w PCR testing, R0>1, again as expected from global exemplars.

                ns = new_schools(this_scen)
                sim['interventions'] += [ns]
                sims.append(sim)
                proc += 1

                if len(sims) == batch_size or proc == tot or (tidx == len(testing)-1 and eidx == len(par_list)-1):
                    print(f'Running sims {proc-len(sims)}-{proc-1} of {tot}')
                    msim = cv.MultiSim(sims)
                    msims.append(msim)
                    msim.run(reseed=False, par_args={'ncpus': 16}, noise=0.0, keep_people=False)
                    sims = []

        print(f'*** Saving after completing {skey}')
        sims_this_scenario = [s for msim in msims for s in msim.sims if s.key1 == skey]
        msim = cv.MultiSim(sims_this_scenario)
        cv.save(os.path.join(folder, 'msims', f'{stem}_{skey}.msim'), msim)

    msim = cv.MultiSim.merge(msims)
    cv.save(os.path.join(folder, 'msims', f'{stem}.msim'), msim)
