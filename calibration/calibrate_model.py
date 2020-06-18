import sciris as sc
import covasim as cv
import optuna as op
from calibration import create_sim as cs

cv.check_save_version('1.4.7', die=True)

restart   = 0
do_plot   = 0
use_safegraph = 1
name      = 'optimization_v12_safegraph_061720'
storage   = f'sqlite:///{name}.db'
n_trials  = 200
n_workers = 32


def objective(trial, kind='default'):
    ''' Define the objective for Optuna '''
    pars = {}
    bounds = cs.define_pars(which='bounds', kind=kind, use_safegraph=use_safegraph)
    for key, bound in bounds.items():
        pars[key] = trial.suggest_uniform(key, *bound)
    pars['rand_seed'] = trial.number
    mismatch = cs.run_sim(pars, use_safegraph=use_safegraph)
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
    make_study(restart=restart)
    run_workers()
    study = op.load_study(storage=storage, study_name=name)
    best_pars = study.best_params
    T = sc.toc(t0, output=True)
    print(f'Output: {best_pars}, time: {T}')

    if do_plot:
        cs.run_sim(best_pars, use_safegraph=use_safegraph, interactive=True)