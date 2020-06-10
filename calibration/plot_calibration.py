import datetime as dt
import matplotlib.ticker as ticker
import sciris as sc
import pylab as pl
import numpy as np
import covasim as cv

# Set general figure options
font_size = 18
font_family = 'Proxima Nova'
pl.rcParams['font.size'] = font_size
pl.rcParams['font.family'] = font_family

def format_ax(ax, sim):
    @ticker.FuncFormatter
    def date_formatter(x, pos):
        return (sim['start_day'] + dt.timedelta(days=x)).strftime('%b-%d')
    ax.xaxis.set_major_formatter(date_formatter)
    sc.commaticks()
    # sc.boxoff()
    return


def plotter(key, sims, ax, ys=None, calib=False, label='', ylabel='', low_q=0.1, high_q=0.9):

    which = key.split('_')[1]
    try:
        color = cv.get_colors()[which]
    except:
        color = [0.5,0.5,0.5]
    if which == 'deaths':
        color = [0.5,0.0,0.0]

    if ys is None:
        ys = []
        for s in sims:
            ys.append(s.results[key].values)

    yarr = np.array(ys)
    best = pl.median(yarr, axis=0) # Changed from median to mean for smoother plots
    low  = pl.quantile(yarr, q=low_q, axis=0)
    high = pl.quantile(yarr, q=high_q, axis=0)

    sim = sims[0] # For having a sim to refer to

    # Formatting parameters
    plot_args   = sc.mergedicts({'lw': 3, 'alpha': 0.8})
    fill_args   = sc.mergedicts({'alpha': 0.2})



    tvec = np.arange(len(best))

    if calib:
        if key == 'r_eff':
            end = -2
        else:
            end = -1
    else:
        end = None

    pl.fill_between(tvec[:end], low[:end], high[:end], facecolor=color, **fill_args)
    pl.plot(tvec[:end], best[:end], c=color, label=label, **plot_args)

    if key in sim.data:
        data_t = np.array((sim.data.index-sim['start_day'])/np.timedelta64(1,'D'))
        pl.plot(data_t, sim.data[key], 'o', c=color, markersize=10, label='Data')

    if calib:
        xlims = pl.xlim()
        pl.xlim([13, xlims[1]-1])
    else:
        pl.xlim([0,94])
    sc.setylim()

    xmin,xmax = ax.get_xlim()
    if calib:
        ax.set_xticks(pl.arange(xmin+2, xmax, 7))
    else:
        ax.set_xticks(pl.arange(xmin+2, xmax, 7))

    pl.ylabel(ylabel)
    pl.legend(loc='upper left')

    return


def plot_intervs(labels=False):
    yl = pl.ylim()
    feb29 = 23
    mar12 = 35
    mar23 = 46
    pl.plot([feb29]*2, yl, 'k', alpha=0.1, lw=3)
    pl.plot([mar12]*2, yl, 'k', alpha=0.1, lw=3)
    pl.plot([mar23]*2, yl, 'k', alpha=0.1, lw=3)

    if labels:
        labely = yl[1]*1.05
        off = 0
        args = {'horizontalalignment': 'center', 'style':'italic'}
        pl.text(feb29-off, labely, 'First death', **args)
        pl.text(mar12-off, labely, 'Schools close', **args)
        pl.text(mar23-off, labely, '    Stay-at-home', **args)
    return



def plot_calibration(sims, date, do_save=0):

    sim = sims[0] # For having a sim to refer to

    # Draw plots
    fig1_path = f'calibration_{date}_fig1.png'
    fig2_path = f'calibration_{date}_fig2.png'
    fig_args    = sc.mergedicts({'figsize': (16, 14)})
    axis_args   = sc.mergedicts({'left': 0.10, 'bottom': 0.05, 'right': 0.95, 'top': 0.93, 'wspace': 0.25, 'hspace': 0.40})

    # Handle input arguments -- merge user input with defaults
    low_q = 0.1
    high_q = 0.9

    # Figure 1: Calibration
    pl.figure(**fig_args)
    pl.subplots_adjust(**axis_args)
    pl.figtext(0.42, 0.95, 'Model calibration', fontsize=30)


    #%% Figure 1, panel 1
    ax = pl.subplot(4,1,1)
    format_ax(ax, sim)
    plotter('new_tests', sims, ax, calib=True, label='Number of tests per day', ylabel='Tests')
    plotter('new_diagnoses', sims, ax, calib=True, label='Number of diagnoses per day', ylabel='Tests')


    #%% Figure 1, panel 2
    ax = pl.subplot(4,1,2)
    format_ax(ax, sim)
    plotter('cum_diagnoses', sims, ax, calib=True, label='Cumulative diagnoses', ylabel='People')


    #%% Figure 1, panel 3
    ax = pl.subplot(4,1,3)
    format_ax(ax, sim)
    plotter('cum_deaths', sims, ax, calib=True, label='Cumulative deaths', ylabel='Deaths')


    #%% Figure 1, panels 4A and 4B

    agehists = []

    for s,sim in enumerate(sims):
        agehist = sim['analyzers'][0]
        if s == 0:
            age_data = agehist.data
        agehists.append(agehist.hists[-1])

    x = age_data['age'].values
    pos = age_data['cum_diagnoses'].values
    death = age_data['cum_deaths'].values

    # From the model
    mposlist = []
    mdeathlist = []
    for hists in agehists:
        mposlist.append(hists['diagnosed'])
        mdeathlist.append(hists['dead'])
    mposarr = np.array(mposlist)
    mdeatharr = np.array(mdeathlist)

    mpbest = pl.median(mposarr, axis=0)
    mplow  = pl.quantile(mposarr, q=low_q, axis=0)
    mphigh = pl.quantile(mposarr, q=high_q, axis=0)
    mdbest = pl.median(mdeatharr, axis=0)
    mdlow  = pl.quantile(mdeatharr, q=low_q, axis=0)
    mdhigh = pl.quantile(mdeatharr, q=high_q, axis=0)

    # Plotting
    w = 4
    off = 2
    bins = x.tolist() + [100]

    ax = pl.subplot(4,2,7)
    c1 = [0.3,0.3,0.6]
    c2 = [0.6,0.7,0.9]
    xx = x+w-off
    pl.bar(x-off,pos, width=w, label='Data', facecolor=c1)
    pl.bar(xx, mpbest, width=w, label='Model', facecolor=c2)
    for i,ix in enumerate(xx):
        pl.plot([ix,ix], [mplow[i], mphigh[i]], c='k')
    ax.set_xticks(bins[:-1])
    pl.title('Diagnosed cases by age')
    pl.xlabel('Age')
    pl.ylabel('Cases')
    pl.legend()

    ax = pl.subplot(4,2,8)
    c1 = [0.5,0.0,0.0]
    c2 = [0.9,0.4,0.3]
    pl.bar(x-off,death, width=w, label='Data', facecolor=c1)
    pl.bar(x+w-off, mdbest, width=w, label='Model', facecolor=c2)
    for i,ix in enumerate(xx):
        pl.plot([ix,ix], [mdlow[i], mdhigh[i]], c='k')
    ax.set_xticks(bins[:-1])
    pl.title('Deaths by age')
    pl.xlabel('Age')
    pl.ylabel('Deaths')
    pl.legend()

    # Tidy up
    if do_save:
        cv.savefig(fig1_path)


    # Figure 2: Projections
    pl.figure(**fig_args)
    pl.subplots_adjust(**axis_args)
    pl.figtext(0.42, 0.95, 'Model estimates', fontsize=30)

    #%% Figure 2, panel 1
    ax = pl.subplot(4,1,1)
    format_ax(ax, sim)
    plotter('cum_infections', sims, ax,calib=True, label='Cumulative infections', ylabel='People')
    plotter('cum_recoveries', sims, ax,calib=True, label='Cumulative recoveries', ylabel='People')

    #%% Figure 2, panel 2
    ax = pl.subplot(4,1,2)
    format_ax(ax, sim)
    plotter('n_infectious', sims, ax,calib=True, label='Number of active infections', ylabel='People')
    plot_intervs(labels=True)

    #%% Figure 2, panel 3
    ax = pl.subplot(4,1,3)
    format_ax(ax, sim)
    plotter('new_infections', sims, ax,calib=True, label='Infections per day', ylabel='People')
    plotter('new_recoveries', sims, ax,calib=True, label='Recoveries per day', ylabel='People')
    plot_intervs()

    #%% Figure 2, panels 4
    ax = pl.subplot(4,1,4)
    format_ax(ax, sim)
    plotter('r_eff', sims, ax, calib=True, label='Effective reproductive number', ylabel=r'$R_{eff}$')

    ylims = [0,4]
    pl.ylim(ylims)
    xlims = pl.xlim()
    pl.plot(xlims, [1, 1], 'k')
    plot_intervs()

    # Tidy up
    if do_save:
        cv.savefig(fig2_path)

    return