import numpy as np
import pandas as pd
import pylab as pl
import sciris  as sc
import seaborn as sns
import optuna as op
import covasim as cv
from reopening_scenarios import create_sim as cs

# Define parameters
name    = 'optimization_v12_safegraph_061120'
storage = f'sqlite:///{name}.db'


def pairplotpars(data, inds=None, color_column=None, bounds=None, cmap='parula', bins=None, edgecolor='w', facecolor='#F8A493', figsize=(20,16)):
    ''' Plot scatterplots, histograms, and kernel densities '''
    data = sc.odict(sc.dcp(data))

    # Create the dataframe
    df = pd.DataFrame.from_dict(data)
    if inds is not None:
        df = df.iloc[inds,:].copy()

    # Choose the colors
    if color_column:
        colors = sc.vectocolor(df[color_column].values, cmap=cmap)
    else:
        colors = [facecolor for i in range(len(df))]
    df['color_column'] = [sc.rgb2hex(rgba[:-1]) for rgba in colors]

    # Make the plot
    grid = sns.PairGrid(df)
    grid = grid.map_lower(pl.scatter, **{'facecolors':df['color_column']})
    grid = grid.map_diag(pl.hist, bins=bins, edgecolor=edgecolor, facecolor=facecolor)
    grid = grid.map_upper(sns.kdeplot)
    # grid = grid.map_upper(pl.hexbin, cmap="Blues", edgecolor="none" , gridsize=25)
    grid.fig.set_size_inches(figsize)
    grid.fig.tight_layout()

    # Set bounds
    if bounds:
        for ax in grid.axes.flatten():
            xlabel = ax.get_xlabel()
            ylabel = ax.get_ylabel()
            if xlabel in bounds:
                ax.set_xlim(bounds[xlabel])
            if ylabel in bounds:
                ax.set_ylim(bounds[ylabel])

    return grid


#%% Load and analyze the data
sc.heading('Loading data...')
best = cs.define_pars('best')
bounds = cs.define_pars('bounds')
study = op.load_study(storage=storage, study_name=name)

sc.heading('Making results structure...')
results = []
n_trials = len(study.trials)
failed_trials = []
for trial in study.trials:
    data = {'index':trial.number, 'mismatch': trial.value}
    for key,val in trial.params.items():
        data[key] = val
    if data['mismatch'] is None:
        failed_trials.append(data['index'])
    else:
        results.append(data)
print(f'Processed {len(study.trials)} trials; {len(failed_trials)} failed')

sc.heading('Making data structure...')
keys = ['index', 'mismatch'] + list(best.keys())
data = sc.objdict().make(keys=keys, vals=[])
for i,r in enumerate(results):
    for key in keys:
        if key not in r:
            print(f'Warning! Key {key} is missing from trial {i}, replacing with default')
            r[key] = best[key]
        data[key].append(r[key])
df = pd.DataFrame.from_dict(data)


#%% Plotting

if __name__ == '__main__':

    sc.heading('Plotting...')

    T = sc.tic()

    save_json   = 1
    plot_trend  = 1
    plot_best   = 1
    plot_stride = 1
    plot_all    = 0
    best_thresh = 1.5

    # Save data to JSON
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

    # Plot the trend in best mismatch over time
    if plot_trend:
        mismatch = sc.dcp(df['mismatch'].values)
        best_mismatch = np.zeros(len(mismatch))
        for i in range(len(mismatch)):
            best_mismatch[i] = mismatch[:i+1].min()
        smoothed_mismatch = sc.smooth(mismatch)
        pl.figure(figsize=(16,12), dpi=120)

        ax1 = pl.subplot(2,1,1)
        pl.plot(mismatch, alpha=0.2, label='Original')
        pl.plot(smoothed_mismatch, lw=3, label='Smoothed')
        pl.plot(best_mismatch, lw=3, label='Best')

        ax2 = pl.subplot(2,1,2)
        max_mismatch = mismatch.min()*best_thresh
        inds = cv.true(mismatch<=max_mismatch)
        pl.plot(best_mismatch, lw=3, label='Best')
        pl.scatter(inds, mismatch[inds], c=mismatch[inds], label='Usable indices')
        for ax in [ax1, ax2]:
            pl.sca(ax)
            pl.grid(True)
            pl.legend()
            sc.setylim()
            sc.setxlim()
            pl.xlabel('Trial number')
            pl.ylabel('Mismatch')

        pl.savefig("calib_trend.png")


    # Plot every point: warning, slow!
    if plot_all:
        g = pairplotpars(data, color_column='mismatch', bounds=bounds)
        g.savefig("calib_all.png")

    # Plot only the points with lowest mismatch
    if plot_best:
        max_mismatch = df['mismatch'].min()*best_thresh
        inds = cv.true(df['mismatch'].values<=max_mismatch)
        g = pairplotpars(data, inds=inds, color_column='mismatch', bounds=bounds)
        g.savefig("calib_best.png")

    # Plot a fixed number of points in order across the results
    if plot_stride:
        npts = 200
        inds = pl.linspace(0, len(df)-1, npts).round()
        g = pairplotpars(data, inds=inds, color_column='mismatch', bounds=bounds)
        g.savefig("calib_stride.png")

    sc.toc(T)
    print('Done.')




