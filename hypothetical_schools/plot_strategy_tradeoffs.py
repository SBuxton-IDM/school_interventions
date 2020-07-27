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
import palettable


strats = [
    'As Normal',
    'With Screening',
    'ES/MS in Person, HS Remote',
    'ES in Person, MS/HS Remote',
    'All Hybrid',
    'All Remote'
          ]


strategies = [
    'as_normal',
    'with_screening',
    'ES_MS_inperson_HS_remote',
    'ES_inperson_MS_HS_remote',
    'with_hybrid_scheduling',
    'all_remote'
]

strategy_labels = {
    'as_normal': 'As Normal',
    'with_screening': 'All In-Person \n with Screening, \nNPI, Cohorting',
    'ES_MS_inperson_HS_remote': 'Elementary In-Person, \nMiddle & High \nRemote',
    'ES_inperson_MS_HS_remote': 'Elementary & \nMiddle In-Person, \nHigh Remote',
    'with_hybrid_scheduling': 'All Hybrid \nScheduling',
    'all_remote': 'All Remote'
}

strategy_labels_2 = {
    'as_normal': 'As Normal',
    'with_screening': 'All In-Person with Screening, \nNPI, Cohorting',
    'ES_MS_inperson_HS_remote': 'Elementary In-Person, Middle & High \nRemote',
    'ES_inperson_MS_HS_remote': 'Elementary & Middle In-Person, \nHigh Remote',
    'with_hybrid_scheduling': 'All Hybrid Scheduling',
    'all_remote': 'All Remote'
}

measure_labels = {
    'num_staff': 'Total Staff',
    'num_teachers': 'Total Teachers',
    'num_students': 'Total Students',
    'student_cases': 'Student Cases',
    'teacher_cases': 'Teacher Cases',
    'staff_cases': 'Staff Cases'
}

prev_labels = {
    'prev_0.1': '0.1%',
    'prev_0.2': '0.2%',
    'prev_0.4': '0.4%'
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


def outputs_df(date, cases=None):
    if cases is not None:
        file_path = os.path.join('results', 'school_reopening_analysis_output_' + cases + '_' + date + '.csv')
    else:
        file_path = os.path.join('results', 'school_reopening_analysis_output_' + date + '.csv')

    return pd.read_csv(file_path)


def results_df(strat, param_set, date, cases=None):
    if cases is not None:
        file_path = os.path.join('results', strat + '_' + cases + '_param' + '%i' % param_set + '_results_' + date + '.csv')
    else:
        file_path = os.path.join('results', strat + '_param' + '%i' % param_set + '_results_' + date + '.csv')
    return pd.read_csv(file_path)


def combine_dfs(mobility_rate, main_strategy, num_param_set):
    df_list = []
    for i in range(num_param_set):
        dfi = outputs_df(mobility_rate, main_strategy, i)
        df_list.append(dfi)

    df = pd.concat(df_list)
    return df


def combine_results_dfs(strat, num_param_set, measure, mean, date, cases=None):
    df_list = []
    for i in range(num_param_set):
        if cases is not None:
            dfi = results_df(strat, i, date, cases)
        else:
            dfi = results_df(strat, i, date)
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


def plot_prevalence(date, cases):

    staff_by_case = []
    students_by_case = []
    for _, case in enumerate(cases):
        df = outputs_df(date, case)
        scenario_strategies = df.columns[1:]

        staff = []
        students = []
        for n, strategy in enumerate(scenario_strategies):
            num_staff = df[df['Unnamed: 0'] == 'num_staff'][strategy].values
            num_staff += df[df['Unnamed: 0'] == 'num_teachers'][strategy].values

            num_staff_cases = df[df['Unnamed: 0'] == 'num_staff_cases'][strategy].values
            num_staff_cases += df[df['Unnamed: 0'] == 'num_teacher_cases'][strategy].values

            staff.append(100 * num_staff_cases[0] / num_staff[0])

            num_students = df[df['Unnamed: 0'] == 'num_students'][strategy].values
            num_student_cases = df[df['Unnamed: 0'] == 'num_student_cases'][strategy].values
            students.append(100 * num_student_cases[0] / num_students[0])

        staff = pd.DataFrame(staff).transpose()
        staff_by_case.append(staff)
        students = pd.DataFrame(students).transpose()
        students_by_case.append(students)

    x = np.arange(len(strategy_labels))

    fig, axs = plt.subplots(nrows = len(cases), sharex=True, sharey=False, figsize=(13, 9))
    fig.subplots_adjust(hspace=0.6, right=0.9)
    fig.suptitle('Prevalence of COVID-19 in Schools', size=24, horizontalalignment='center')

    for i, ax in enumerate(axs):
        ax.bar(x + .2, staff_by_case[i], width=0.2, alpha=0.87, label='Teachers and Staff')
        ax.bar(x - .2, students_by_case[i], width=0.2, alpha=0.87, label='Students')
        ax.set_ylabel('Prevalence (%)', size=16)
        ax.set_title(prev_labels[cases[i]] + ' COVID-19 Prevalence on 09/01', size=16, horizontalalignment='center')
        ax.set_xticks(x)
        ax.set_xticklabels(strategy_labels.values(), fontsize=12)
        ax.legend(fontsize=12)
    fig.savefig(f'prevalence.png', format='png')


def plot_prevalence_2(date, cases):
    colors = ['lightcoral', 'lightseagreen', 'lightsteelblue', 'cornflowerblue']

    staff_by_case = []
    students_by_case = []
    for _, case in enumerate(cases):
        df = outputs_df(date, case)
        scenario_strategies = df.columns[1:]

        staff = []
        students = []
        for n, strategy in enumerate(scenario_strategies):
            num_staff = df[df['Unnamed: 0'] == 'num_staff'][strategy].values
            num_staff += df[df['Unnamed: 0'] == 'num_teachers'][strategy].values

            num_staff_cases = df[df['Unnamed: 0'] == 'num_staff_cases'][strategy].values
            num_staff_cases += df[df['Unnamed: 0'] == 'num_teacher_cases'][strategy].values

            staff.append(100 * num_staff_cases[0] / num_staff[0])

            num_students = df[df['Unnamed: 0'] == 'num_students'][strategy].values
            num_student_cases = df[df['Unnamed: 0'] == 'num_student_cases'][strategy].values
            students.append(100 * num_student_cases[0] / num_students[0])

        staff = pd.DataFrame(staff).transpose()
        staff_by_case.append(staff)
        students = pd.DataFrame(students).transpose()
        students_by_case.append(students)

    x = np.arange(len(strategy_labels))

    fig, axs = plt.subplots(nrows = 2, sharex=True, sharey=False, figsize=(13, 9))
    fig.subplots_adjust(hspace=0.6, right=0.9)
    fig.suptitle('Prevalence of COVID-19 in Schools', size=24, horizontalalignment='center')

    width = [-.2, 0, .2]

    for i, ax in enumerate(axs):
        for j, case in enumerate(cases):
            if i == 0:
                ax.bar(x + width[j], staff_by_case[j], width=0.2, label=prev_labels[case], color=colors[j])
                ax.set_title('Teachers and Staff', size=16, horizontalalignment='center')
            else:
                ax.bar(x + width[j], students_by_case[j], width=0.2, label=prev_labels[case], color=colors[j])
                ax.set_title('Students', size=16, horizontalalignment='center')
        ax.set_ylabel('Prevalence (%)', size=12)
        ax.set_xticks(x)
        ax.set_xticklabels(strategy_labels.values(), fontsize=12)
        ax.legend(fontsize=12, title='COVID-19 Prevalence on 09/01')

    fig.savefig(f'prevalence.png', format='png')


def plot_infections(num_param_set, date, cases):
    df_by_prev = []
    df_by_prev_std = []
    measure = 'new_infections'

    for case in cases:
        df_mean = []
        df_std = []
        for strat in strategies:
            df_mean.append(combine_results_dfs(strat, num_param_set, measure, True, date, case))
            df_std.append(combine_results_dfs(strat, num_param_set, measure, False, date, case))

        scenario_strategies = strats

        df_comb = pd.DataFrame(df_mean).transpose()
        df_comb.columns = scenario_strategies

        df_comb_std = pd.DataFrame(df_std).transpose()
        df_comb_std.columns = scenario_strategies

        df_by_prev.append(df_comb)
        df_by_prev_std.append(df_comb_std)

    base = dt.datetime(2020,7,1)
    date_list = [base + dt.timedelta(days=x) for x in range(len(df_comb))]
    x = []
    for date in date_list:
        x.append(date.strftime('%b %d'))

    date_to_x = {d:i for i, d in enumerate(x)}
    right = 0.65

    fig, axs = plt.subplots(len(cases), sharex=True, sharey=False, figsize=(13, 9))
    fig.subplots_adjust(hspace=0.6, right=right)
    fig.suptitle('New Infections by COVID-Prevalence on 09/01', size=20, horizontalalignment='center')

    # colors = sc.gridcolors(len(scenario_strategies))

    for i, ax in enumerate(axs):
        for s, strat in enumerate(scenario_strategies):
            ax.plot(x, df_by_prev[i][strat].values, color=colors[s], label=strat)

        if i == len(axs) - 1:
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
        ax.set_title(prev_labels[cases[i]] + ' COVID-19 Prevalence on 09/01', fontsize=14)
        ax.tick_params(labelsize=12)


    fig.savefig(f'{measure}.png', format='png')


def plot_reff(num_param_set, date):

    colors = ['lightcoral', 'lightseagreen', 'lightsteelblue', 'cornflowerblue']

    df_mean = []
    df_std = []
    for strat in strategies:
        df_mean.append(combine_results_dfs(strat, num_param_set, 'r_eff', True, date))
        df_std.append(combine_results_dfs(strat, num_param_set, 'r_eff', False, date))
        # df_mean.append(combine_results_dfs(rate, main_strategy, strat, num_param_set, 'new_infections', True))

    # averted_deaths.append(sum(df_mean[1][218:309]) - sum(df_mean[7][218:309]))
    scenario_strategies = strats

    df_comb = pd.DataFrame(df_mean).transpose()
    df_comb.columns = scenario_strategies

    df_comb_std = pd.DataFrame(df_std).transpose()
    df_comb_std.columns = scenario_strategies

    base = dt.datetime(2020,7,1)
    date_list = [base + dt.timedelta(days=x) for x in range(len(df_comb))]
    x = []
    for date in date_list:
        x.append(date.strftime('%b %d'))

    date_to_x = {d:i for i, d in enumerate(x)}

    min_x = date_to_x['Aug 30']
    max_x = date_to_x['Dec 01']

    df_comb = df_comb.iloc[min_x:max_x, ]
    df_comb = df_comb.mean(axis=0)

    df_comb_std = df_comb_std.iloc[min_x:max_x, ]
    df_comb_std = df_comb_std.mean(axis=0)
    x = np.arange(len(strategy_labels))

    width = [-.2, 0, .2,]

    left = 0.07
    right = 0.9
    # right = 0.63
    bottom = 0.10
    top = 0.85

    fig, ax = plt.subplots(figsize=(13,9))
    ax.bar(x, df_comb.values, yerr=df_comb_std.values / 2, width=0.4, alpha=0.87)
    ax.axhline(y=1, xmin=0, xmax=1, color='black', ls='--')

    ax.set_ylabel('Effective Reproductive Number', size=16)
    ax.set_title(f'Effective Reproductive Number by School Reopening Strategy', size=18, horizontalalignment='center')
    ax.set_ylim(0.7, 1.4)
    ax.set_xticks(x)
    ax.set_xticklabels(strategy_labels.values(), fontsize=12)

    # Strategies Legend
    ax_left = right + 0.04
    ax_bottom = bottom + 0.02
    ax_right = 0.95
    ax_width = ax_right - ax_left
    ax_height = top - bottom
    ax_leg = fig.add_axes([ax_left, ax_bottom, ax_width, ax_height])
    leg = ax_leg.legend(loc=10, fontsize=14)
    # leg = ax.legend(loc=4, fontsize=15, bbox_to_anchor=(0.65, -0.05, 1, 0.2))
    leg.draw_frame(False)
    ax_leg.axis('off')

    fig.savefig(f'r_eff.png', format='png')


def plot_reff_with_prev(cases, num_param_set, date):

    colors = ['lightcoral', 'lightseagreen', 'lightsteelblue', 'cornflowerblue']

    df_by_prev = []
    df_by_prev_std = []

    for case in cases:
        df_mean = []
        df_std = []
        for strat in strategies:
            df_mean.append(combine_results_dfs(strat, num_param_set, 'r_eff', True, date, case))
            df_std.append(combine_results_dfs(strat, num_param_set, 'r_eff', False, date, case))
            # df_mean.append(combine_results_dfs(rate, main_strategy, strat, num_param_set, 'new_infections', True))

        # averted_deaths.append(sum(df_mean[1][218:309]) - sum(df_mean[7][218:309]))
        scenario_strategies = strats

        df_comb = pd.DataFrame(df_mean).transpose()
        df_comb.columns = scenario_strategies

        df_comb_std = pd.DataFrame(df_std).transpose()
        df_comb_std.columns = scenario_strategies

        df_by_prev.append(df_comb)
        df_by_prev_std.append(df_comb_std)

    base = dt.datetime(2020, 7, 1)
    date_list = [base + dt.timedelta(days=x) for x in range(len(df_comb))]
    x = []
    for date in date_list:
        x.append(date.strftime('%b %d'))

    date_to_x = {d: i for i, d in enumerate(x)}

    min_x = date_to_x['Aug 30']
    max_x = date_to_x['Dec 01']

    for i, _ in enumerate(cases):
        df_by_prev[i] = df_by_prev[i].iloc[min_x:max_x,]
        df_by_prev[i] = df_by_prev[i].mean(axis=0)
        df_by_prev_std[i] = df_by_prev_std[i].iloc[min_x:max_x, ]
        df_by_prev_std[i] = df_by_prev_std[i].mean(axis=0)


    x = np.arange(len(strategy_labels))

    width = [-.2, 0, .2]

    left = 0.07
    right = 0.9
    # right = 0.63
    bottom = 0.10
    top = 0.85

    fig, ax = plt.subplots(figsize=(13,9))
    for i, rate in enumerate(cases):
        ax.bar(x + width[i], df_by_prev[i].values, yerr = df_by_prev_std[i].values/2, width=0.2,
               label=prev_labels[rate], color=colors[i], alpha = 0.87)
    # ax.bar(x, df_comb.values, yerr=df_comb_std.values / 2, width=0.4, alpha=0.87)
    ax.axhline(y=1, xmin=0, xmax=1, color='black', ls='--')

    ax.set_ylabel('Effective Reproductive Number', size=16)
    ax.set_title(f'Effective Reproductive Number by School Reopening Strategy', size=18, horizontalalignment='center')
    ax.set_ylim(0.7, 1.4)
    ax.legend(fontsize=12, title='COVID-19 Prevalence on 09/01')
    ax.set_xticks(x)
    ax.set_xticklabels(strategy_labels.values(), fontsize=12)

    # Strategies Legend
    ax_left = right + 0.04
    ax_bottom = bottom + 0.02
    ax_right = 0.95
    ax_width = ax_right - ax_left
    ax_height = top - bottom
    ax_leg = fig.add_axes([ax_left, ax_bottom, ax_width, ax_height])
    leg = ax_leg.legend(loc=10, fontsize=14)
    leg.draw_frame(False)
    ax_leg.axis('off')

    fig.savefig(f'r_eff.png', format='png')


if __name__ == '__main__':
    num_param_set = 5

    cases = ['prev_0.1', 'prev_0.2', 'prev_0.4']

    date = '2020-07-27'

    # plot_reff(num_param_set, date)
    # plot_reff_with_prev(cases, num_param_set, date)
    plot_infections(num_param_set, date, cases)
    plot_prevalence_2(date, cases)


    print('done')