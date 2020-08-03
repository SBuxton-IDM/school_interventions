import sciris as sc
import optuna as op
import pandas as pd
import numpy as np
from hypothetical_schools import create_sim as cs

re_to_fit = 0.9
cases_to_fit = 20
name      = f'optimization_school_reopening_re_{re_to_fit}_cases_{cases_to_fit}'
storage   = f'sqlite:///{name}.db'
n_trials  = 30
n_workers = 32
save_json = True


def objective(trial, kind='default'):
    ''' Define the objective for Optuna '''
    pars = {}
    bounds = cs.define_pars(which='bounds', kind=kind)
    for key, bound in bounds.items():
        pars[key] = trial.suggest_uniform(key, *bound)
    pars['rand_seed'] = trial.number
    sim = cs.run_sim(pars)
    results = pd.DataFrame(sim.results)
    re = results['r_eff'].iloc[49:63, ].mean(axis=0)
    cases = results['new_diagnoses'].iloc[49:63, ].sum(axis=0) * 100e3 / 2.25e6
    re_mismatch = (re_to_fit - re)**2
    cases_mismatch = (cases_to_fit - cases)**2
    mismatch = re_mismatch + cases_mismatch
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
    n_trials = len(study.trials)
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