"""
Example of plotting different dimensions of school reopening results to
look at tradeoffs.
"""

import numpy as np
import pandas as pd
import sciris as sc
import matplotlib as mplt
import matplotlib.pyplot as plt
import math
import os
import datetime as dt


strats = ['No School',
          'School As Normal',
          'School with NPI',
          'School with NPI + Cohorting',
          'School with NPI, Cohorting, Screening',
          'School with NPI, Cohorting, Screening, 25% Follow-Up Testing',
          'School with NPI, Cohorting, Screening, 50% Follow-Up Testing, 25% Follow-Up Tracing',
          'School with NPI, Cohorting, Screening, 100% Follow-Up Testing, 100% Follow-Up Tracing',
          ]


strategies = ['withmasks_No School',
              'withmasks_School As Normal',
              'withmasks_School with NPI',
              'withmasks_School with NPI + Cohorting',
              'withmasks_School with NPI, Cohorting, Screening',
              'withmasks_School with NPI, Cohorting, Screening, 25% Follow-Up Testing',
              'withmasks_School with NPI, Cohorting, Screening, 50% Follow-Up Testing, 25% Follow-Up Tracing',
              'withmasks_School with NPI, Cohorting, Screening, 100% Follow-Up Testing, 100% Follow-Up Tracing',
]

strategies_2 = ['no_school',
                'as_normal',
                'with_NPI',
                'with_cohorting',
                'with_screening_notesting',
                'with_25perctest_notracing',
                'with_50perctest_25tracing',
                'with_100perctest_100tracing',
]

strategy_labels = {
    'no_school': 'No School',
    'as_normal': 'As Normal',
    'with_NPI': 'With NPI',
    'with_cohorting': 'With NPI and Cohorting',
    'with_screening_notesting': 'With NPI, Cohorting, Screening, \nand No Testing',
    'with_25perctest_notracing': 'With NPI, Cohorting, Screening, \nand 25% Testing',
    'with_50perctest_25tracing': 'With NPI, Cohorting, Screening, \n50% Testing and 25% Tracing',
    'with_100perctest_100tracing': 'With NPI, Cohorting, Screening, \n100% Testing and 100% Tracing',
}

measure_labels = {
    'school_closures': 'School Closures',
    'cum_infections': 'Cumulative Infections',
    'num_tested': 'Number Tested',
    'num_traced': 'Number Traced',
    'test_pos': 'Test Positive',
    'school_days_lost (%)': 'School Days Lost (%)',
    'school_days_lost': 'School Days Lost',
    'num_students': 'Number of Students',
    'total_cases': 'Total Cases',
    'student_cases': 'Student Cases',
    'teacher_cases': 'Teacher Cases',
    'cases_in_pk': 'Cases in Preschools',
    'cases_in_es': 'Cases in Elementary Schools',
    'cases_in_ms': 'Cases in Middle Schools',
    'cases_in_hs': 'Cases in High Schools',
    'cases_in_uv': 'Cases in Universities and Colleges',
    'pk_with_a_case': 'Preschools with a case',
    'es_with_a_case': 'Elementary Schools with a case',
    'ms_with_a_case': 'Middle Schools with a case',
    'hs_with_a_case': 'High Schools with a case',
    'uv_with_a_case': 'Universities and Colleges with a case',
}


# scaled_up_measures = ['school_closures', 'cum_infections', 'num_tested', 'num_traced', 'school_days_lost',
#                       'num_students', 'total_cases']

# Global plotting styles
font_size = 30
font_style = 'Roboto Condensed'
# font_style = 'Barlow Condensed'
# font_style = 'Source Sans Pro'
mplt.rcParams['font.family'] = font_style

colors = []
colors.append('tab:blue')
# colors.append('tab:red')
colors.append('red')
colors.append('tab:green')
colors.append('tab:purple')
colors.append('tab:orange')
colors.append('gold')
colors.append('tab:brown')
colors.append('deeppink')
colors.append('deepskyblue')


def get_scenario_name(mobility_rate, strategy):
    return '%i' % mobility_rate + '_mobility_' + strategy


def outputs_df(mobility_rate, main_strategy, param_set):

    file_path = os.path.join('results', 'school_reopening_analysis_' + '%i' % mobility_rate + 'perc_mobility_' + main_strategy + 'param' + '%i' % param_set + '_output.csv')
    return pd.read_csv(file_path)


def results_df(mobility_rate, main_strategy, strat, param_set):

    file_path = os.path.join('results', 'school_reopening_analysis_' + '%i' % mobility_rate + 'perc_mobility_' + main_strategy + strat + '_param' + '%i' % param_set + '_results.csv')
    return pd.read_csv(file_path)


def combine_dfs(mobility_rate, main_strategy, num_param_set):
    df_list = []
    for i in range(num_param_set):
        dfi = outputs_df(mobility_rate, main_strategy, i)
        df_list.append(dfi)

    df = pd.concat(df_list)
    return df


def combine_results_dfs(mobility_rate, main_strategy, strat, num_param_set, measure, mean):
    df_list = []
    for i in range(num_param_set):
        dfi = results_df(mobility_rate, main_strategy, strat, i)
        dfi = dfi[measure]
        df_list.append(dfi)

    df = pd.concat(df_list, axis=1)
    if mean:
        df = df.mean(axis=1)
    else:
        df = df.std(axis=1)

    return np.array(df)


def mean_output(combined_df, strategy, measure):
    d = combined_df[combined_df['Unnamed: 0'] == measure][strategy]
    values = d.values
    try:
        values = np.array([float(v) for v in values])

    except:
        values_list = []
        if ',' in values[0]:
            values = [v.replace('[', '').replace(']', '') for v in values]
            values = [v.split(',') for v in values]

            values = [item for subvalue in values for item in subvalue]
            values = [v for v in values if v not in ['[', ']']]
        else:
            # print(values[0])
            values = [v.replace('[', '').replace(']', '') for v in values]
            # print(values)
        # print(values)
        values = [float(v) for v in values]
        values = np.array(values)
        # print(measure, values)

    return np.mean(values)


def transform_x(x, xmax, xmin, ymax, ymin):
    slope = (ymax - ymin) / (xmax - xmin)
    intercept = ymin - (ymax - ymin) / (xmax - xmin) * xmin
    return slope * x + intercept


def plot_dimensions(mobility_rate, main_strategy, num_param_set, dim1, dim2, dim3):

    df = combine_dfs(mobility_rate, main_strategy, num_param_set)

    scenario_strategies = df.columns[1:]
    n_strategies = len(scenario_strategies)

    # colors = sc.gridcolors(n_strategies)

    x = []
    y = []
    z = []

    for n, strategy in enumerate(scenario_strategies):
        xi = mean_output(df, strategy, dim1)
        yi = mean_output(df, strategy, dim2)
        zi = mean_output(df, strategy, dim3)

        if dim1 == 'school_days_lost':
            # if strategy == 'no_school':
            #     xi = 2992626
            # nsi = mean_output(df, strategy, 'num_students')
            # xi = xi / nsi
            xi = xi / 2992626. * 100

        elif dim2 == 'school_days_lost':
            # if strategy == 'no_school':
            #     yi = 2992626
            # nsi = mean_output(df, strategy, 'num_students')
            # yi = yi / nsi
            yi = yi / 2992626. * 100

        elif dim3 == 'school_days_lost':
            # if strategy == 'no_school':
            #     zi = 2992626
            # nsi = mean_output(df, strategy, 'num_students')
            # zi = zi / nsi
            zi = zi / 2992626. * 100

        x.append(xi)
        y.append(yi)
        z.append(zi)

    logzmax = math.ceil(np.log10(max(z)))
    zmax = 10 ** logzmax
    zmin = max(min(z), 1)
    logzmin = math.floor(np.log10(zmin))
    # logzmin = math.ceil(np.log10(zmin))
    print(logzmax, logzmin)

    sizes = []
    size_min = 8
    size_max = 40
    for zi in z:
        zi = max(1, zi)
        logzi = np.log10(zi)

        si = transform_x(logzi, logzmax, logzmin, size_max, size_min)
        sizes.append(si)

    fig = plt.figure(figsize=(13, 9))
    fig.subplots_adjust(right=0.63, top=0.85)
    ax = fig.add_subplot(111)
    alpha = 0.67

    for i in range(n_strategies):
        ax.plot(x[i], y[i], marker='o', markersize=sizes[i], alpha=alpha, markerfacecolor=colors[i], markeredgewidth=0)
        ax.plot(-5, -5, linewidth=0, marker='o', markerfacecolor=colors[i], markeredgewidth=0, label=strategy_labels[scenario_strategies[i]])

    ax.set_xlabel(measure_labels[dim1] + ' (%)', fontsize=20)
    # ax.set_xlabel(measure_labels[dim1], fontsize=22)
    ax.set_ylabel(measure_labels[dim2], fontsize=22)

    ax.set_xlim(left=min(x) - max(x) * 0.05, right=max(x) * 1.1)
    ax.set_ylim(bottom=min(y) * 0.9, top=max(y) * 1.1)
    ax.tick_params(labelsize=20)
    leg = ax.legend(loc=4, fontsize=15, bbox_to_anchor=(0.65, -0.05, 1, 0.2))
    leg.draw_frame(False)
    ax.set_title('Mobility ' + '%i' % mobility_rate + '% Pre COVID' , fontsize=28)

    # legend for marker
    left = 0.67
    bottom = 0.48
    width = 0.3
    height = 0.39

    ax2 = fig.add_axes([left, bottom, width, height])

    yticks = ax.get_yticks()
    ymax = max(yticks)
    ymin = min(yticks)

    yinterval = 0.48 / (logzmax + 1)

    for i in np.arange(logzmin, logzmax + 1):
    # for i in np.arange(logzmax + 1):

        zi = 10 ** i
        xi = 1
        yi = (0.5 + yinterval * i) * ymax
        si = transform_x(i, logzmax, logzmin, size_max, size_min)
        si = max(si, 1)
        # print(i, zi, si)

        ax2.plot(xi, yi, linestyle=None, marker='o', markersize=si, markerfacecolor='white', markeredgecolor='black')
        ax2.text(xi * 1.5, yi, '%i' % (zi), verticalalignment='center', fontsize=18)

    # ax2.text(xi * 1.2, yi * 1.08, measure_labels[dim3], horizontalalignment='center', fontsize=20)
    ax2.text(xi * 1.2, ymax * 0.99, measure_labels[dim3], horizontalalignment='center', fontsize=20)

    ax2.axis('off')
    ax2.set_xlim(left=0, right=4)
    # ax2.set_ylim(0.65, 1.10)
    ax2.set_ylim(0.48 * ymax, ymax)

    fig.savefig('mobility_rate_' + '%i' % mobility_rate + '_' + dim1 + '_' + dim2 + '_' + dim3 + '.pdf', format='pdf')


def get_summary_stats(mobility_rate, main_strategy, num_param_set, measure):
    x_by_rate = []

    for rate in mobility_rate:
        df = combine_dfs(rate, main_strategy, num_param_set)
        scenario_strategies = df.columns[1:]

        x = []

        for n, strategy in enumerate(scenario_strategies):
            xi = mean_output(df, strategy, measure)

            x.append(xi)

        x_by_rate.append(x)
    return x_by_rate


def plot_dimensions_with_mobility(mobility_rate, main_strategy, num_param_set, dim1, dim2):
    df_by_rate = []
    x_by_rate = []
    y_by_rate = []
    z_by_rate = []

    for rate in mobility_rate:
        df = combine_dfs(rate, main_strategy, num_param_set)
        df_by_rate.append(df)
        scenario_strategies = df.columns[1:]
        scenario_strategies = scenario_strategies.tolist()
        scenario_strategies.remove('no_school')
        n_strategies = len(scenario_strategies)
        # colors = sc.gridcolors(n_strategies)

        x = []
        y = []
        z = []

        for n, strategy in enumerate(scenario_strategies):
            xi = mean_output(df, strategy, dim1)
            yi = mean_output(df, strategy, dim2)
            zi = rate

            # if dim1 == 'school_days_lost':
            #     # if strategy == 'no_school':
            #     #     xi = 2992626
            #     # nsi = mean_output(df, strategy, 'num_students')
            #     # xi = xi / nsi
            #     xi = xi / 2992626. * 100
            #
            # elif dim2 == 'school_days_lost':
            #     # if strategy == 'no_school':
            #     #     yi = 2992626
            #     # nsi = mean_output(df, strategy, 'num_students')
            #     # yi = yi / nsi
            #     yi = yi / 2992626. * 100

            x.append(xi)
            y.append(yi)
            z.append(zi)

        x_by_rate.append(x)
        y_by_rate.append(y)
        z_by_rate.append(z)

    size_min = 8
    size_max = 50
    num_sizes = len(z_by_rate)
    intervals = (size_max - size_min)/num_sizes
    sizes = np.arange(size_min, size_max, step = intervals).tolist()

    right = 0.63
    bottom = 0.10
    top = 0.85
    fig = plt.figure(figsize=(13, 9))
    fig.subplots_adjust(right=right, top=top, bottom=bottom)
    ax = fig.add_subplot(111)
    alpha = 0.67

    for j, rate in enumerate(mobility_rate):
        for i in range(n_strategies):
            ax.plot(x_by_rate[j][i], y_by_rate[j][i], marker='o', markersize=sizes[j], alpha=alpha, markerfacecolor=colors[i],
                    markeredgewidth=0,
                    )

        ax.set_xlabel(measure_labels[dim1], fontsize=16)
        ax.set_ylabel(measure_labels[dim2], fontsize=16)
    ax.tick_params(labelsize=16)

    # Strategies Legend
    ax_left = right + 0.04
    ax_bottom = bottom + 0.02
    ax_right = 0.95
    ax_width = ax_right - ax_left
    ax_height = (top - bottom)/2.
    ax_leg = fig.add_axes([ax_left, ax_bottom, ax_width, ax_height])
    for s, strat in enumerate(scenario_strategies):
        ax_leg.plot(-5, -5, color=colors[s], label=strategy_labels[strat])

    leg = ax_leg.legend(loc=10, fontsize=14)
    # leg = ax.legend(loc=4, fontsize=15, bbox_to_anchor=(0.65, -0.05, 1, 0.2))
    leg.draw_frame(False)
    ax_leg.axis('off')

    # Mobility size legend
    ax_bottom_2 = ax_bottom + ax_height + 0.0
    ax_leg_2 = fig.add_axes([ax_left, ax_bottom_2, ax_width, ax_height])

    ybase = 0.5
    ytop = 1
    yinterval = (ytop - ybase)/len(sizes)

    for i in range(len(sizes)):

        xi = 1
        yi = ybase + yinterval * i
        si = sizes[i]

        ax_leg_2.plot(xi, yi, linestyle=None, marker='o', markersize=si, markerfacecolor='white', markeredgecolor='black')
        ax_leg_2.text(xi * 1.5, yi, '%i' % (mobility_rate[i]), verticalalignment='center', fontsize=16)

    ax_leg_2.text(xi * 1.2, 0.985, 'Mobility % Pre COVID', horizontalalignment='center', fontsize=18)

    ax_leg_2.axis('off')
    ax_leg_2.set_xlim(left=0, right=4)
    ax_leg_2.set_ylim(bottom=ybase*0.9, top=ytop*1.0)

    ax.set_title('Trade-Offs with School Reopening', fontsize=20)
    fig.savefig(dim1 + '_' + dim2 + '_bymobility' + '.png', format='png')


def plot_infections(mobility_rate, strats, num_param_set):

    df_by_rate = []
    for rate in mobility_rate:
        measure = 'cum_infections'
        df_mean = []
        df_std = []
        for strat in strats:
            df_mean.append(combine_results_dfs(rate, strat, num_param_set, measure, True))
            df_std.append(combine_results_dfs(rate, strat, num_param_set, measure, False))

        scenario_strategies = strats

        df_comb = pd.DataFrame(df_mean).transpose()
        df_comb.columns = scenario_strategies
        df_by_rate.append(df_comb)

    base = dt.datetime(2020,1,27)
    date_list = [base + dt.timedelta(days=x) for x in range(len(df_comb))]
    x = []
    for date in date_list:
        x.append(date.strftime('%b %d'))

    date_to_x = {d:i for i, d in enumerate(x)}
    right = 0.65

    fig, axs = plt.subplots(3, sharex=True, sharey=False, figsize=(13, 9))
    fig.subplots_adjust(hspace=0.6, right=right)
    fig.suptitle('Cumulative Infections by Community and Workplace Mobility', size=24, horizontalalignment='right')

    # colors = sc.gridcolors(len(scenario_strategies))

    for i, ax in enumerate(axs):
        for s, strat in enumerate(scenario_strategies):
            ax.plot(x, df_by_rate[i][strat].values, color=colors[s])

        # ax.set_xlim(200, 309)
        if i == len(axs) - 1:
            for s, strat in enumerate(scenario_strategies):
                ax.plot(-5, -5, color=colors[s], label=strat.replace('Screening, ', 'Screening,\n').replace('Testing, ', 'Testing,\n'))
            leg = ax.legend(fontsize=16, bbox_to_anchor=(0.63, 3, 1, 0.102))
            leg.draw_frame(False)
            xtick_labels = np.array(x)
            n_xticks = len(ax.get_xticks())
            interval = 15
            xticks = np.arange(0, n_xticks, interval)
            xtick_labels_displayed = xtick_labels[::interval]
            ax.set_xticks(xticks)
            ax.set_xticklabels(xtick_labels_displayed)

        ax.set_xlim(left=date_to_x['Aug 01'], right=date_to_x['Dec 01'])
        ax.set_ylim(bottom=50e3)
        ax.set_title('Mobility ' + '%i' % mobility_rate[i] + '% Pre COVID', fontsize=20)
        ax.tick_params(labelsize=16)
        # ax.xaxis.set_minor_locator(ticker.LinearLocator(numticks=155))

    fig.savefig('cuminfections_basecase.pdf', format='pdf')


def plot_general(mobility_rate, main_strategy, strats, num_param_set, measure_to_plot):

    df_by_rate = []
    df_by_rate_std = []
    for rate in mobility_rate:
        df_mean = []
        df_std = []
        for strat in strats:
            df_mean.append(combine_results_dfs(rate, main_strategy, strat, num_param_set, measure_to_plot, True))
            df_std.append(combine_results_dfs(rate, main_strategy, strat, num_param_set, measure_to_plot, False))

        scenario_strategies = strats

        df_comb = pd.DataFrame(df_mean).transpose()
        df_comb.columns = scenario_strategies

        df_comb_std = pd.DataFrame(df_std).transpose()
        df_comb_std.columns = scenario_strategies
        df_by_rate.append(df_comb)
        df_by_rate_std.append(df_comb_std)

    base = dt.datetime(2020,1,27)
    date_list = [base + dt.timedelta(days=x) for x in range(len(df_comb))]
    x = []
    for date in date_list:
        x.append(date.strftime('%b %d'))

    date_to_x = {d:i for i, d in enumerate(x)}

    left = 0.07
    right = 0.65
    # right = 0.63
    bottom = 0.10
    top = 0.85

    fig, axs = plt.subplots(len(mobility_rate), sharex=True, sharey=False, figsize=(13, 9))
    fig.subplots_adjust(hspace=0.6, left=left, right=right)
    if measure_to_plot == 'r_eff':
        measure = 'Effective Reproductive Number'
    elif measure_to_plot == 'cum_infections':
        measure = 'Cumulative Infections'
    elif measure_to_plot == 'new_infections':
        measure = 'New Infections'
    else:
        measure = measure_to_plot
    fig.suptitle(f'{measure} by Community and Workplace Mobility', size=18, horizontalalignment='center')

    for i, ax in enumerate(axs):
        for s, strat in enumerate(scenario_strategies):
            ax.plot(x, df_by_rate[i][strat].values, color=colors[s])

        # Add ticks on the x axis only for the last subplot
        if i == len(axs) - 1:
            xtick_labels = np.array(x)
            n_xticks = len(ax.get_xticks())
            interval = 15
            xticks = np.arange(0, n_xticks, interval)
            xtick_labels_displayed = xtick_labels[::interval]
            ax.set_xticks(xticks)
            ax.set_xticklabels(xtick_labels_displayed)

        ax.set_xlim(left=date_to_x['Sep 01'], right=date_to_x['Dec 01'])
        if measure_to_plot == 'r_eff':
            ax.set_ylim(0.5, 1.5)
            ax.axhline(y=1, xmin=0, xmax=1, color='black', ls='--')
        elif measure_to_plot == 'cum_infections':
            ax.set_ylim(50e3, 500e3)
        elif measure_to_plot == 'new_tests':
            ax.set_ylim(2e3, 4.5e3)
        elif measure_to_plot == 'new_infections':
            ymax = df_by_rate[i]['School As Normal'].max()
            ymin = df_by_rate[i]['No School'].min()
            ax.set_ylim(ymin, ymax*1.1)
        ax.set_title('Mobility ' + '%i' % mobility_rate[i] + '% Pre COVID', fontsize=16)
        ax.tick_params(labelsize=15)

    # Strategies Legend
    ax_left = right + 0.04
    ax_bottom = bottom + 0.02
    ax_right = 0.95
    ax_width = ax_right - ax_left
    ax_height = top - bottom
    ax_leg = fig.add_axes([ax_left, ax_bottom, ax_width, ax_height])
    for s, strat in enumerate(scenario_strategies):
        ax_leg.plot(-5, -5, color=colors[s],
                    label=strat.replace('Screening, ','Screening,\n').replace('Testing, ', 'Testing,\n'),
                    )

    leg = ax_leg.legend(loc=10, fontsize=16)
    # leg = ax.legend(loc=4, fontsize=15, bbox_to_anchor=(0.65, -0.05, 1, 0.2))
    leg.draw_frame(False)
    ax_leg.axis('off')

    fig.savefig(f'{measure_to_plot}_{main_strategy}.png', format='png')


if __name__ == '__main__':

    mobility_rate = [70, 80, 90, 100]

    # main_strategy = 'withmasks_'
    main_strategy = 'withoutmasks_testtracedelay_'
    strats = strats
    param_set = 0
    num_param_set = 5

    tests_by_rate = get_summary_stats(mobility_rate, main_strategy, num_param_set, 'num_tested')
    traces_by_rate = get_summary_stats(mobility_rate, main_strategy, num_param_set, 'num_traced')

    dim1, dim2, dim3 = 'school_days_lost', 'cum_infections', 'num_tested'

    # dim1, dim2, dim3 = 'school_days_lost', 'cum_infections', 'num_traced'
    # dim1, dim2, dim3 = 'student_cases', 'cum_infections', 'teacher_cases'
    # dim1, dim2, dim3 = 'student_cases', 'teacher_cases', 'cum_infections'
    # dim1, dim2, dim3 = 'student_cases', 'teacher_cases', 'num_tested'

    measure_to_plot = ['r_eff', 'new_infections', 'cum_infections']
    # measure_to_plot = 'new_infections'
    # plot_infections(mobility_rate, strats, num_param_set)
    for measure in measure_to_plot:
        plot_general(mobility_rate, main_strategy, strats, num_param_set, measure)
    # plot_general(mobility_rate, main_strategy, strats, num_param_set, measure_to_plot)
    plot_dimensions_with_mobility(mobility_rate, main_strategy, num_param_set, dim1, dim2)

    # for rate in mobility_rate:
        # plot_dimensions(rate, main_strategy, num_param_set, dim1, dim2, dim3)