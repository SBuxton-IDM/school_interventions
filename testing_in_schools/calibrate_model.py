import os
import sciris as sc
import optuna as op
import pandas as pd
import numpy as np
import create_sim as cs
from school_intervention import new_schools

pop_size = 1e5 #2.25e4
cases_to_fit = 100 #20, 50, 110
re_to_fit = 1.0

name      = os.path.join('opt', f'optimization_school_reopening_re_{re_to_fit}_cases_{cases_to_fit}_{int(pop_size)}')
storage   = f'sqlite:///{name}.db'
n_workers = 8
n_trials  = 20 # Each worker does n_trials
save_json = True

def scenario(es, ms, hs):
    return {
        'pk': None,
        'es': es,
        'ms': ms,
        'hs': hs,
        'uv': None,
    }


def objective(trial, kind='default'):
    ''' Define the objective for Optuna '''
    pars = {}
    bounds = cs.define_pars(which='bounds', kind=kind)
    for key, bound in bounds.items():
        pars[key] = trial.suggest_uniform(key, *bound)
    pars['rand_seed'] = trial.number

    sim = cs.create_sim(pars, pop_size=pop_size)

    remote = {
        'start_day': '2020-09-01',
        'is_hybrid': False,
        'screen_prob': 0,
        'test_prob': 0,
        'trace_prob': 0,
        'ili_prob': 0,
        'beta_s': 0 # This turns off transmission in the School class
    }
    scen = scenario(es=remote, ms=remote, hs=remote)
    ns = new_schools(scen)
    sim['interventions'] += [ns]
    sim.run()

    first = sim.day('2020-09-01')
    last = sim.day('2020-12-01')

    results = pd.DataFrame(sim.results)
    '''
    re = results['r_eff'].iloc[first:last, ].mean(axis=0)
    cases = results['new_diagnoses'].iloc[first:last, ].sum(axis=0) * 100e3 / (sim.pars['pop_size'] * sim.pars['pop_scale'])
    re_mismatch = (re_to_fit - re)**2 / re_to_fit**2
    cases_mismatch = (cases_to_fit - cases)**2 / cases_to_fit**2
    mismatch = re_mismatch + cases_mismatch
    '''

    re = results['r_eff'].iloc[first:last, ].mean(axis=0)
    cases_past14 = results['new_diagnoses'].iloc[(first-14):first, ].sum(axis=0) * 100e3 / (sim.pars['pop_size'] * sim.pars['pop_scale'])
    cases_during = results['new_diagnoses'].iloc[first:last, ].mean(axis=0) * 14 * 100e3 / (sim.pars['pop_size'] * sim.pars['pop_scale'])
    re_mismatch = (re_to_fit - re)**2 / re_to_fit**2
    cases_past14_mismatch = (cases_to_fit - cases_past14)**2 / cases_to_fit**2
    cases_during_mismatch = (cases_to_fit - cases_during)**2 / cases_to_fit**2
    mismatch = re_mismatch + cases_past14_mismatch + cases_during_mismatch

    return mismatch


def worker():
    ''' Run a single worker '''
    study = op.load_study(storage=storage, study_name=name)
    output = study.optimize(objective, n_trials=n_trials)
    return output


def run_workers():
    ''' Run multiple workers in parallel '''
    output = sc.parallelize(worker, n_workers)
    return output


def make_study(restart=True):
    ''' Make a study, deleting one if it already exists '''
    try:
        if restart:
            print(f'About to delete {storage}:{name}, you have 5 seconds to intervene!')
            sc.timedsleep(5.0)
            op.delete_study(storage=storage, study_name=name)
    except:
        pass

    output = op.create_study(storage=storage, study_name=name, load_if_exists=not(restart))
    return output


if __name__ == '__main__':
    t0 = sc.tic()
    make_study()
    run_workers()
    study = op.load_study(storage=storage, study_name=name)
    best_pars = study.best_params
    T = sc.toc(t0, output=True)
    print(f'Output: {best_pars}, time: {T}')

    sc.heading('Loading data...')
    best = cs.define_pars('best')
    bounds = cs.define_pars('bounds')

    sc.heading('Making results structure...')
    results = []
    #n_trials = len(study.trials)
    failed_trials = []
    for trial in study.trials:
        data = {'index': trial.number, 'mismatch': trial.value}
        for key, val in trial.params.items():
            data[key] = val
        if data['mismatch'] is None:
            failed_trials.append(data['index'])
        else:
            results.append(data)
    print(f'Processed {len(study.trials)} trials; {len(failed_trials)} failed')

    sc.heading('Making data structure...')
    keys = ['index', 'mismatch'] + list(best.keys())
    data = sc.objdict().make(keys=keys, vals=[])
    for i, r in enumerate(results):
        for key in keys:
            if key not in r:
                print(f'Warning! Key {key} is missing from trial {i}, replacing with default')
                r[key] = best[key]
            data[key].append(r[key])
    df = pd.DataFrame.from_dict(data)

    if save_json:
        order = np.argsort(df['mismatch'])
        json = []
        for o in order:
            row = df.iloc[o,:].to_dict()
            rowdict = dict(index=row.pop('index'), mismatch=row.pop('mismatch'), pars={})
            for key,val in row.items():
                rowdict['pars'][key] = val
            json.append(rowdict)
        sc.savejson(f'{name}.json', json, indent=2)
        saveobj = False
        if saveobj: # Smaller file, but less portable
            sc.saveobj(f'{name}.obj', json)
