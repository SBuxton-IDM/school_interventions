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
    'All Remote',
    # 'With Perfect Testing, Tracing & School Closure on 1 COVID+'
          ]

closure_strats = [

    'With Perfect Testing, Tracing & School Closure on 1 COVID+'
          ]


strategies = [
    'as_normal',
    'with_screening',
    'ES_MS_inperson_HS_remote',
    'ES_inperson_MS_HS_remote',
    'with_hybrid_scheduling',
    'all_remote',
    # 'with_perf_testing_close_on_1'
]

closure_strategies = [

    'with_perf_testing_close_on_1'
]

strategy_labels = {
    'as_normal': 'As Normal',
    'with_screening': 'All In Person \n with Screening, \nNPI, Cohorting',
    'ES_MS_inperson_HS_remote': 'Elementary & \nMiddle In Person, \nHigh Remote',
    'ES_inperson_MS_HS_remote': 'Elementary In \nPerson, Middle \n& High Remote',
    'with_hybrid_scheduling': 'All Hybrid \nScheduling',
    'all_remote': 'All Remote',
# 'with_perf_testing_close_on_1': 'With Perfect \nTesting, Tracing & \nSchool Closure on \n1 COVID+'
}

closure_strategy_labels = {
    'with_perf_testing_close_on_1': 'With Perfect \nTesting, Tracing & \nSchool Closure on \n1 COVID+'
}

strategy_labels_2 = {
    'as_normal': 'As Normal',
    'with_screening': 'All In-Person with Screening, \nNPI, Cohorting',
    'ES_MS_inperson_HS_remote': 'Elementary & Middle In-Person, \nHigh Remote',
    'ES_inperson_MS_HS_remote': 'Elementary In-Person, Middle & High \nRemote',
    'with_hybrid_scheduling': 'All Hybrid Scheduling',
    'all_remote': 'All Remote',
    # 'with_perf_testing_close_on_1': 'With Perfect Testing, Tracing & School Closure on 1 COVID+'
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

re_labels = {
    're_0.9': '0.9',
    're_1.1': '1.1'
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


def outputs_df(date, cases, rel_trans):
    if rel_trans:
        file_path = os.path.join('results', 'school_reopening_analysis_output_' + cases + '_under10_0.5trans_' + date + '.csv')
    else:
        file_path = os.path.join('results', 'school_reopening_analysis_output_' + cases + '_' + date + '.csv')
    return pd.read_csv(file_path)


def results_df(strat, param_set, date, cases, rel_trans):
    if rel_trans:
        file_path = os.path.join('results',
                                 strat + '_' + cases + '_under10_0.5trans_param' + '%i' % param_set + '_results_' + date + '.csv')
    else:
        file_path = os.path.join('results', strat + '_' + cases + '_param' + '%i' % param_set + '_results_' + date + '.csv')
    return pd.read_csv(file_path)


def combine_dfs(mobility_rate, main_strategy, num_param_set):
    df_list = []
    for i in range(num_param_set):
        dfi = outputs_df(mobility_rate, main_strategy, i)
        df_list.append(dfi)

    df = pd.concat(df_list)
    return df


def combine_results_dfs(strat, num_param_set, measure, mean, date, cases, rel_trans):
    df_list = []
    for i in range(num_param_set):
        dfi = results_df(strat, i, date, cases, rel_trans)
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


def plot_attack_rate(date, cases, by_prev, rel_trans):
    colors = ['lightcoral', 'lightseagreen', 'lightsteelblue', 'cornflowerblue']

    if by_prev:
        labels = prev_labels
        name = 'COVID-19 Prevalence on 09/01'
        prev = 'by_prev'
    else:
        labels = re_labels
        name = 'Community Reff'
        prev = 'by_re'

    if rel_trans:
        prev = prev + '_under10_0.5trans'
        subtitle = '\n (50% reduced transmission in under 10s)'
    else:
        subtitle = ''

    staff_by_case = []
    students_by_case = []
    for _, case in enumerate(cases):
        df = outputs_df(date, case, rel_trans)
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

    width = [-.2, 0, .2]

    fig, axs = plt.subplots(nrows = 2, sharex=True, sharey=False, figsize=(13, 9))
    fig.subplots_adjust(hspace=0.6, right=0.9)
    fig.suptitle(f'COVID-19 Attack Rate in Schools {subtitle}', size=24, horizontalalignment='center')

    for i, ax in enumerate(axs):
        for j, case in enumerate(cases):
            if i == 0:
                ax.bar(x + width[j], staff_by_case[j].values[0], width=0.2, label=labels[case], color=colors[j])
                ax.set_title('Teachers and Staff', size=16, horizontalalignment='center')
            else:
                ax.bar(x + width[j], students_by_case[j].values[0], width=0.2, label=labels[case], color=colors[j])
                ax.set_title('Students', size=16, horizontalalignment='center')
        ax.set_ylabel('Attack Rate (%)', size=14)
        ax.set_xticks(x)
        ax.set_xticklabels(strategy_labels.values(), fontsize=12)
        ax.legend(fontsize=14, title=name)

    fig.savefig(f'attack_rate_{prev}.png', format='png')


def plot_infections(num_param_set, date, cases, by_prev, rel_trans):
    df_by_prev = []
    df_by_prev_std = []
    measure = 'new_infections'

    for case in cases:
        df_mean = []
        df_std = []
        for strat in strategies:
            df_mean.append(combine_results_dfs(strat, num_param_set, measure, True, date, case, rel_trans))
            df_std.append(combine_results_dfs(strat, num_param_set, measure, False, date, case, rel_trans))

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

    if by_prev:
        labels = prev_labels
        name = ' COVID-19 Prevalence on 09/01'
        prev = 'by_prev'
    else:
        labels = re_labels
        name = ' Community Reff'
        prev = 'by_re'

    if rel_trans:
        prev = prev + '_under10_0.5trans'
        subtitle = '\n (50% reduced transmission in under 10s)'
    else:
        subtitle = ''

    fig, axs = plt.subplots(len(cases), sharex=True, sharey=False, figsize=(13, 9))
    fig.subplots_adjust(hspace=0.6, right=right)
    fig.suptitle(f'New Infections {subtitle}', size=20, horizontalalignment='center')

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
        ax.set_title(labels[cases[i]] + name, fontsize=14)
        ax.tick_params(labelsize=12)


    fig.savefig(f'{measure}_{prev}.png', format='png')


def plot_reff_with_prev(cases, num_param_set, date, by_prev, rel_trans):

    colors = ['lightcoral', 'lightseagreen', 'lightsteelblue', 'cornflowerblue']

    df_by_prev = []
    df_by_prev_std = []

    for case in cases:
        df_mean = []
        df_std = []
        for strat in strategies:
            df_mean.append(combine_results_dfs(strat, num_param_set, 'r_eff', True, date, case, rel_trans))
            df_std.append(combine_results_dfs(strat, num_param_set, 'r_eff', False, date, case, rel_trans))
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

    if by_prev:
        name = 'COVID-19 Prevalence on 09/01'
        prev = 'by_prev'
        label = prev_labels
    else:
        name = 'Community Reff'
        prev = 'by_re'
        label = re_labels

    if rel_trans:
        prev = prev + '_under10_0.5trans'
        subtitle = '\n (50% reduced transmission in under 10s)'
    else:
        subtitle = ''

    fig, ax = plt.subplots(figsize=(13,9))
    for i, rate in enumerate(cases):
        ax.bar(x + width[i], df_by_prev[i].values, yerr = df_by_prev_std[i].values/2, width=0.2,
               label=label[rate], color=colors[i], alpha = 0.87)
    # ax.bar(x, df_comb.values, yerr=df_comb_std.values / 2, width=0.4, alpha=0.87)
    ax.axhline(y=1, xmin=0, xmax=1, color='black', ls='--')

    ax.set_ylabel('Effective Reproductive Number', size=16)
    ax.set_title(f'Effective Reproductive Number by School Reopening Strategy {subtitle}', size=18, horizontalalignment='center')
    ax.set_ylim(0.7, 1.4)


    ax.legend(fontsize=12, title=name)
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

    fig.savefig(f'r_eff_{prev}.png', format='png')


def get_re(cases, num_param_set, date, rel_trans):
    df_mean = []
    for case in cases:
        df_mean.append(combine_results_dfs('all_remote', num_param_set, 'r_eff', True, date, case, rel_trans))

    df_mean = pd.DataFrame(df_mean).transpose()
    base = dt.datetime(2020, 7, 1)
    date_list = [base + dt.timedelta(days=x) for x in range(len(df_mean[0]))]
    x = []
    for date in date_list:
        x.append(date.strftime('%b %d'))

    date_to_x = {d: i for i, d in enumerate(x)}
    min_x = date_to_x['Aug 30']
    max_x = date_to_x['Dec 01']

    df_mean = df_mean.iloc[min_x:max_x, ]
    df_mean = df_mean.mean(axis=0)

    return(df_mean.values)


def plot_dimensions(date, cases, by_prev, rel_trans):

    if by_prev:
        labels = prev_labels
        name = 'COVID-19 Prevalence on 09/01'
        prev = 'by_prev'
        subtitle = 'By Prevalence'
    else:
        labels = re_labels
        name = 'Community Reff'
        prev = 'by_re'
        subtitle = 'By Community Reff'

    if rel_trans:
        prev = prev + '_under10_0.5trans'

    attack_rate_by_case = []
    perc_school_days_lost_by_case = []

    for _, case in enumerate(cases):
        df = outputs_df(date, case, rel_trans)
        scenario_strategies = df.columns[1:]
        perc_school_days_lost = []
        attack_rate = []
        for n, strategy in enumerate(scenario_strategies):
            total = df[df['Unnamed: 0'] == 'num_staff'][strategy].values
            total += df[df['Unnamed: 0'] == 'num_teachers'][strategy].values
            total += df[df['Unnamed: 0'] == 'num_students'][strategy].values

            num_cases = df[df['Unnamed: 0'] == 'num_staff_cases'][strategy].values
            num_cases += df[df['Unnamed: 0'] == 'num_teacher_cases'][strategy].values
            num_cases += df[df['Unnamed: 0'] == 'num_student_cases'][strategy].values

            attack_rate.append(100 * num_cases[0] / total[0])

            school_days_lost = df[df['Unnamed: 0'] == 'perc_school_days_lost'][strategy].values
            perc_school_days_lost.append(100 * school_days_lost[0])

        attack_rate = pd.DataFrame(attack_rate).transpose()
        attack_rate_by_case.append(attack_rate)

        perc_school_days_lost = pd.DataFrame(perc_school_days_lost).transpose()
        perc_school_days_lost_by_case.append(perc_school_days_lost)

    n_strategies = len(scenario_strategies)

    size_min = 8
    size_max = 50
    num_sizes = len(cases)
    intervals = (size_max - size_min) / num_sizes
    sizes = np.arange(size_min, size_max, step=intervals).tolist()

    right = 0.63
    bottom = 0.10
    top = 0.85
    fig = plt.figure(figsize=(13, 9))
    fig.subplots_adjust(right=right, top=top, bottom=bottom)
    ax = fig.add_subplot(111)
    alpha = 0.67

    for j, rate in enumerate(cases):
        ax.plot(perc_school_days_lost_by_case[j].iloc[0, :].values, attack_rate_by_case[j].iloc[0, :].values, linewidth=3, alpha=0.33, color='grey', linestyle='-')
        for i in range(n_strategies):
            ax.plot(perc_school_days_lost_by_case[j][i], attack_rate_by_case[j][i], marker='o', markersize=sizes[j], alpha=alpha,
                    markerfacecolor=colors[i],
                    markeredgewidth=0,
                    )

        ax.set_xlabel('In-Person School Days Lost (%)', fontsize=16)
        ax.set_ylabel('Within-School Attack Rate (%)', fontsize=16)
        # ax.set_ylim(0, 15)
        # ax.set_xlim(0, 10)
    ax.tick_params(labelsize=16)

    # Strategies Legend
    ax_left = right + 0.04
    ax_bottom = bottom + 0.02
    ax_right = 0.95
    ax_width = ax_right - ax_left
    ax_height = (top - bottom) / 2.
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
    yinterval = (ytop - ybase) / len(sizes)

    for i in range(len(sizes)):
        xi = 1
        yi = ybase + yinterval * i
        si = sizes[i]

        ax_leg_2.plot(xi * 1.5, yi, linestyle=None, marker='o', markersize=si, markerfacecolor='white',
                      markeredgecolor='black')
        ax_leg_2.text(xi * 4, yi, (labels[cases[i]]), verticalalignment='center', fontsize=16)

    ax_leg_2.text(xi * 7, 0.985, f'{name}', horizontalalignment='center', fontsize=18)

    ax_leg_2.axis('off')
    ax_leg_2.set_xlim(left=0, right=20)
    ax_leg_2.set_ylim(bottom=ybase * 0.9, top=ytop * 1.0)

    ax.set_title(f'Trade-Offs with School Reopening \n {subtitle}', fontsize=20)
    fig.savefig(f'tradeoffs_{prev}.png', format='png')


if __name__ == '__main__':
    num_param_set = 5

    prevalence = ['prev_0.1', 'prev_0.2', 'prev_0.4']
    re = ['re_0.9', 're_1.1']
    rel_trans = False
    date = '2020-07-28'
    by_prev = True
    if by_prev:
        cases = prevalence
    else:
        cases = re
        re = get_re(cases, num_param_set, date, rel_trans)
        for i, case in enumerate(cases):
            re_labels[case] = round(re[i], 1)

    # plot_reff_with_prev(cases, num_param_set, date, by_prev, rel_trans)
    # plot_attack_rate(date, cases, by_prev, rel_trans)
    plot_dimensions(date, cases, by_prev, rel_trans)
    plot_infections(num_param_set, date, cases, by_prev, rel_trans)

    print('done')