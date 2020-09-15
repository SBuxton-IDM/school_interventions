"""
Example of plotting different dimensions of school reopening results to
look at tradeoffs.
"""

import numpy as np
import pandas as pd
import matplotlib as mplt
import matplotlib.pyplot as plt
import os
import datetime as dt
import covasim as cv


strats = [
    'As Normal',
    'With Screening',
    'All Hybrid',
    'ES/MS in Person, HS Remote',
    'ES in Person, MS/HS Remote',
    'ES hybrid',
    'All Remote',
    # 'With Perfect Testing, Tracing & School Closure on 1 COVID+'
          ]

closure_strats = [

    'With Perfect Testing, Tracing & School Closure on 1 COVID+'
          ]


strategies = [
    'as_normal',
    'with_screening',
    'with_hybrid_scheduling',
    'ES_MS_inperson_HS_remote',
    'ES_inperson_MS_HS_remote',
    'ES_hybrid',
    'all_remote',
    # 'with_perf_testing_close_on_1'
]

closure_strategies = [

    'with_perf_testing_close_on_1'
]

strategy_labels = {
    'as_normal': 'In person, no\ncountermeasures',
    'with_screening': 'In person with \n countermeasures \n(NPI, cohorting, \nscreening)',
    'with_hybrid_scheduling': 'In person with \ncountermeasures, \n A/B scheduling',
    'ES_MS_inperson_HS_remote': 'Elementary & \nmiddle in \nperson with \ncountermeasures, \nhigh remote',
    'ES_inperson_MS_HS_remote': 'Elementary in \nperson, with \n countermeasures, \nmiddle & \nhigh remote',
    'ES_hybrid': 'Elementary with \ncountermeasures, \nA/B scheduling, \n middle & high \nremote',
    'all_remote': 'All remote',
# 'with_perf_testing_close_on_1': 'With Perfect \nTesting, Tracing & \nSchool Closure on \n1 COVID+'
}

closure_strategy_labels = {
    'with_perf_testing_close_on_1': 'With Perfect \nTesting, Tracing & \nSchool Closure on \n1 COVID+'
}

strategy_labels_2 = {
    'as_normal':                'All in person, no\ncountermeasures',
    'with_screening':           'All in person with \n countermeasures \n(NPI, cohorting, \nscreening)',
    'with_hybrid_scheduling':   'All in person with \ncountermeasures, \n A/B scheduling',
    'ES_MS_inperson_HS_remote': 'Elementary & middle\nin person with \ncountermeasures, \nhigh remote',
    'ES_inperson_MS_HS_remote': 'Elementary in\nperson with\ncountermeasures, \nmiddle & high\nremote',
    'ES_hybrid':                'Elementary with \ncountermeasures & \nA/B scheduling, \nmiddle & high\nremote',
    # 'all_remote': 'All Remote',
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

inc_labels = {
    '20_cases_re_0.9': '20',
    '50_cases_re_0.9': '50',
    '110_cases_re_0.9': '110',
    '20_cases_re_1.1': '20',
    '50_cases_re_1.1': '50',
    '110_cases_re_1.1': '110',
}

re_labels = {
    '20_cases_re_0.9': '0.9',
    '50_cases_re_0.9': '0.9',
    '110_cases_re_0.9': '0.9',
    '20_cases_re_1.1': '1.1',
    '50_cases_re_1.1': '1.1',
    '110_cases_re_1.1': '1.1',
}

rel_trans_labels = {
    True: '50%',
    False: '100%'
}

beta_layer_labels = {
    True: 'Same as households',
    False: '20% as infectious \nas households'
}

sens_label = {
    'under10_0.5trans': '50% reduced transmission in under 10s',
    '3xschool_beta_layer': 'Infectivity in schools relative to households'
}


# Global plotting styles
font_size = 16
font_style = 'Roboto Condensed'
# font_style = 'Barlow Condensed'
# font_style = 'Source Sans Pro'
mplt.rcParams['font.size'] = font_size
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


def outputs_df(date, cases, sens=None):
    if sens is not None:
        file_path = os.path.join('results', 'school_reopening_analysis_output_' + cases + '_' + sens + '_' + date + '.csv')
    else:
        file_path = os.path.join('results', 'school_reopening_analysis_output_' + cases + '_' + date + '.csv')
    return pd.read_csv(file_path)


def results_df(strat, param_set, date, cases, sens=None):
    if sens is not None:
        file_path = os.path.join('results',
                                 strat + '_' + cases + '_' + sens + '_param' + '%i' % param_set + '_results_' + date + '.csv')
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


def combine_results_dfs(strat, num_param_set, measure, mean, date, cases, sens):
    df_list = []
    for i in range(num_param_set):
        dfi = results_df(strat, i, date, cases, sens)
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


def plot_attack_rate(date_of_file, cases, sens):
    colors = ['lightseagreen', 'lightsteelblue', 'lightcoral']

    name = 'Cases per 100k people during the\ntwo weeks prior to school reopening'
    if '1.1' in cases[0]:
        prev = 'by_cases_rising'
        subtitle = '(Re > 1)'
    else:
        prev = 'by_cases_falling'
        subtitle = '(Re < 1)'
    label = inc_labels

    if sens is not None:
        prev = prev + '_' + sens
        subtitle += f'\n ({sens_label[sens]})'

    staff_by_case = []
    students_by_case = []
    for _, case in enumerate(cases):
        df = outputs_df(date_of_file, case, sens)
        scenario_strategies = df.columns[1:]
        scenario_strategies = scenario_strategies.tolist()
        scenario_strategies.remove('all_remote')

        staff = []
        students = []
        num_staff = df[df['Unnamed: 0'] == 'num_staff']['as_normal'].values
        num_staff += df[df['Unnamed: 0'] == 'num_teachers']['as_normal'].values
        num_students = df[df['Unnamed: 0'] == 'num_students']['as_normal'].values
        for n, strategy in enumerate(scenario_strategies):
            #num_staff = df[df['Unnamed: 0'] == 'num_staff'][strategy].values
            #num_staff += df[df['Unnamed: 0'] == 'num_teachers'][strategy].values

            num_staff_cases = df[df['Unnamed: 0'] == 'num_staff_cases'][strategy].values
            num_staff_cases += df[df['Unnamed: 0'] == 'num_teacher_cases'][strategy].values

            staff.append(100 * num_staff_cases[0] / num_staff[0])

            #num_students = df[df['Unnamed: 0'] == 'num_students'][strategy].values
            num_student_cases = df[df['Unnamed: 0'] == 'num_student_cases'][strategy].values
            students.append(100 * num_student_cases[0] / num_students[0])

        staff = pd.DataFrame(staff).transpose()
        staff_by_case.append(staff)
        students = pd.DataFrame(students).transpose()
        students_by_case.append(students)

    x = np.arange(len(scenario_strategies))

    width = [-.2, 0, .2]
    width_text = [-.28, -.09, .12]

    fig, axs = plt.subplots(nrows=2, sharex=True, sharey=False, figsize=(13, 9))
    fig.subplots_adjust(hspace=0.3, right=0.9, bottom=0.15)
    fig.suptitle(f'Predicted cumulative COVID-19 infection rate from Sep. 1 to Dec. 1 for people in schools', size=24, horizontalalignment='center')

    for i, ax in enumerate(axs):
        for j, case in enumerate(cases):
            if i == 0:
                ax.bar(x + width[j], staff_by_case[j].values[0], width=0.2, label=label[case], color=colors[j])
                for h in range(len(x)):
                    ax.text(h + width_text[j], 0.5 + staff_by_case[j][h].values, round(staff_by_case[j][h].values[0], 1), fontsize=10)
                ax.set_title('Teachers and staff', size=20, horizontalalignment='center')
            else:
                ax.bar(x + width[j], students_by_case[j].values[0], width=0.2, label=label[case], color=colors[j])
                for h in range(len(x)):
                    ax.text(h + width_text[j], 0.5 + students_by_case[j][h].values, round(students_by_case[j][h].values[0], 1), fontsize=10)
                ax.set_title('Students', size=20, horizontalalignment='center')
        ax.set_ylabel('COVID-19 infection rate (%)', size=20)
        ax.set_ylim([0,27])
        ax.set_xticks(x)
        ax.set_xticklabels(strategy_labels_2.values(), fontsize=14)
        if i == 0:
            leg_i = ax.legend(fontsize=16, title=name)
            leg_i.set_title(name, prop={'size': 16})
        #ax.legend(fontsize=16, title=name)


    cv.savefig(f'attack_rate_{prev}_{date_of_file}.png')


def plot_attack_rate_all_re(date_of_file, sens):
    colors = ['lightcoral', 'lightseagreen', 'lightsteelblue', 'cornflowerblue']

    # re = ['re_0.9', 're_1.1']
    cases = ['20_cases', '50_cases', '110_cases']

    name = 'Cases per 100k in last 14 days'

    if '1.1' in cases[0]:
        prev = 'by_cases_rising'
        subtitle = '(Re > 1)'
    else:
        prev = 'by_cases_falling'
        subtitle = '(Re < 1)'
    label = inc_labels

    if sens is not None:
        prev = prev + '_' + sens
        subtitle += f'\n ({sens_label[sens]})'

    staff_by_case = []
    students_by_case = []
    for _, case in enumerate(cases):
        df = outputs_df(date_of_file, case, sens)
        scenario_strategies = df.columns[1:]
        scenario_strategies = scenario_strategies.tolist()
        scenario_strategies.remove('all_remote')

        staff = []
        students = []
        num_staff = df[df['Unnamed: 0'] == 'num_staff']['as_normal'].values
        num_staff += df[df['Unnamed: 0'] == 'num_teachers']['as_normal'].values
        num_students = df[df['Unnamed: 0'] == 'num_students']['as_normal'].values
        for n, strategy in enumerate(scenario_strategies):
            # num_staff = df[df['Unnamed: 0'] == 'num_staff'][strategy].values
            # num_staff += df[df['Unnamed: 0'] == 'num_teachers'][strategy].values

            num_staff_cases = df[df['Unnamed: 0'] == 'num_staff_cases'][strategy].values
            num_staff_cases += df[df['Unnamed: 0'] == 'num_teacher_cases'][strategy].values

            staff.append(100 * num_staff_cases[0] / num_staff[0])

            # num_students = df[df['Unnamed: 0'] == 'num_students'][strategy].values
            num_student_cases = df[df['Unnamed: 0'] == 'num_student_cases'][strategy].values
            students.append(100 * num_student_cases[0] / num_students[0])

        staff = pd.DataFrame(staff).transpose()
        staff_by_case.append(staff)
        students = pd.DataFrame(students).transpose()
        students_by_case.append(students)

    x = np.arange(len(scenario_strategies))

    width = [-.2, 0, .2]

    fig, axs = plt.subplots(nrows = 2, sharex=True, sharey=False, figsize=(13, 9))
    fig.subplots_adjust(hspace=0.6, right=0.9)
    fig.suptitle(f'COVID-19 Attack Rate in Schools {subtitle}', size=24, horizontalalignment='center')

    for i, ax in enumerate(axs):
        for j, case in enumerate(cases):
            if i == 0:
                ax.bar(x + width[j], staff_by_case[j].values[0], width=0.2, label=label[case], color=colors[j])
                ax.set_title('Teachers and Staff', size=16, horizontalalignment='center')
            else:
                ax.bar(x + width[j], students_by_case[j].values[0], width=0.2, label=label[case], color=colors[j])
                ax.set_title('Students', size=16, horizontalalignment='center')
        ax.set_ylabel('Attack Rate (%)', size=14)
        ax.set_xticks(x)
        ax.set_xticklabels(strategy_labels_2.values(), fontsize=12)
        ax.legend(fontsize=14, title=name)

    fig.savefig(f'attack_rate_{prev}_{date_of_file}.png', format='png')


def plot_attack_rate_by_sens(date_of_file, case, sens):
    colors = ['lightsteelblue', 'cornflowerblue']

    sensitivity = [True, False]
    rel_trans = [sens, None]

    if sens == 'under10_0.5trans':
        name = 'Relative Transmission in <10s'
        prev = 'rel_trans'
        label = rel_trans_labels
    else:
        name = 'Relative Transmission in Schools'
        prev = 'beta_layer'
        label = beta_layer_labels

    staff_by_case = []
    students_by_case = []
    for i, val in enumerate(rel_trans):
        df = outputs_df(date_of_file, case, val)
        scenario_strategies = df.columns[1:]
        scenario_strategies = scenario_strategies.tolist()
        scenario_strategies.remove('all_remote')

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

    x = np.arange(len(scenario_strategies))

    width = [-.2, 0, .2]

    fig, axs = plt.subplots(nrows = 2, sharex=True, sharey=False, figsize=(13, 9))
    fig.subplots_adjust(hspace=0.6, right=0.9)
    fig.suptitle(f'Percent of students, teachers and staff with COVID-19 in schools', size=20, horizontalalignment='center')

    for i, ax in enumerate(axs):
        for j, val in enumerate(sensitivity):
            if i == 0:
                ax.bar(x + width[j], staff_by_case[j].values[0], width=0.2, label=label[val], color=colors[j])
                ax.set_title('Teachers and Staff', size=16, horizontalalignment='center')
            else:
                ax.bar(x + width[j], students_by_case[j].values[0], width=0.2, label=label[val], color=colors[j])
                ax.set_title('Students', size=16, horizontalalignment='center')
        ax.set_ylabel('Percent with COVID-19 in school (%)', size=14)
        ax.set_xticks(x)
        ax.set_xticklabels(strategy_labels_2.values(), fontsize=12)
        ax.legend(fontsize=14, title=name)

    fig.savefig(f'attack_rate_{prev}_{re_labels[case]}_{date_of_file}.png', format='png')


def plot_reff_combined(num_param_set, date_of_file):

    colors = ['lightseagreen', 'lightsteelblue', 'lightcoral']

    case = '50_cases_re_0.9'
    rel_trans = 'under10_0.5trans'
    beta_layer = '3xschool_beta_layer'
    sens = [rel_trans, None, beta_layer]

    name = 'Infectivity Assumptions'
    sens_labels = {
        None: 'Baseline: children under 10 as infectious as adults; '
              '\nper-contact infectivity in school 20% relative to households',
        rel_trans: '50% reduced transmission in children under 10',
        beta_layer: 'Same infectivity per contact in schools as households'
    }

    df_by_prev = []
    df_by_prev_std = []

    for sen in sens:
        df_mean = []
        df_std = []
        for strat in strategies:
            df_mean.append(combine_results_dfs(strat, num_param_set, 'r_eff', True, date_of_file, case, sen))
            df_std.append(combine_results_dfs(strat, num_param_set, 'r_eff', False, date_of_file, case, sen))

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

    for i, _ in enumerate(sens):
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
    for i, sen in enumerate(sens):
        ax.bar(x + width[i], df_by_prev[i].values, yerr = df_by_prev_std[i].values/2, width=0.2,
               label=sens_labels[sen], color=colors[i], alpha = 0.87)
    # ax.bar(x, df_comb.values, yerr=df_comb_std.values / 2, width=0.4, alpha=0.87)
    ax.axhline(y=1, xmin=0, xmax=1, color='black', ls='--')

    ax.set_ylabel('Effective Reproductive Number', size=16)
    ax.set_title(f'Effective Reproductive Number by School Reopening Strategy', size=18, horizontalalignment='center')
    ax.set_ylim(0.7, 1.5)
    leg_i = ax.legend(fontsize=12, title=name)
    leg_i.set_title(name, prop={'size': 12})
    ax.set_xticks(x)
    ax.set_xticklabels(strategy_labels.values(), fontsize=10)

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

    fig.savefig(f'r_eff_{date_of_file}.png', format='png')


def plot_reff(cases, num_param_set, date_of_file, sens):

    colors = ['lightcoral', 'lightseagreen', 'lightsteelblue', 'cornflowerblue']

    df_by_prev = []
    df_by_prev_std = []

    for case in cases:
        df_mean = []
        df_std = []
        for strat in strategies:
            df_mean.append(combine_results_dfs(strat, num_param_set, 'r_eff', True, date_of_file, case, sens))
            df_std.append(combine_results_dfs(strat, num_param_set, 'r_eff', False, date_of_file, case, sens))
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

    name = 'Cases per 100k in last 14 days'
    prev = 'by_cases'
    label = inc_labels

    fig, ax = plt.subplots(figsize=(13,9))
    for i, rate in enumerate(cases):
        ax.bar(x + width[i], df_by_prev[i].values, yerr = df_by_prev_std[i].values/2, width=0.2,
               label=label[rate], color=colors[i], alpha = 0.87)
    # ax.bar(x, df_comb.values, yerr=df_comb_std.values / 2, width=0.4, alpha=0.87)
    ax.axhline(y=1, xmin=0, xmax=1, color='black', ls='--')

    ax.set_ylabel('Effective Reproductive Number', size=16)
    ax.set_title(f'Effective Reproductive Number by School Reopening Strategy', size=18, horizontalalignment='center')
    ax.set_ylim(0.5, 1.7)
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

    fig.savefig(f'r_eff_{prev}_{date_of_file}.png', format='png')


def plot_reff_by_sens(cases, num_param_set, date_of_file, sens):

    colors = ['lightcoral', 'lightseagreen', 'lightsteelblue', 'cornflowerblue']

    df_by_prev = []
    df_by_prev_std = []

    sensitivity = [True, False]
    rel_trans = [sens, None]

    for i in rel_trans:
        df_mean = []
        df_std = []
        for strat in strategies:
            df_mean.append(combine_results_dfs(strat, num_param_set, 'r_eff', True, date_of_file, cases, i))
            df_std.append(combine_results_dfs(strat, num_param_set, 'r_eff', False, date_of_file, cases, i))
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

    for i in range(len(rel_trans)):
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

    if sens == 'under10_0.5trans':
        name = 'Relative Transmission in <10s'
        prev = 'rel_trans'
        label = rel_trans_labels
    else:
        name = 'Relative Transmission in Schools'
        prev = 'beta_layer'
        label = beta_layer_labels

    fig, ax = plt.subplots(figsize=(13,9))
    for i, val in enumerate(sensitivity):
        ax.bar(x + width[i], df_by_prev[i].values, yerr = df_by_prev_std[i].values/2, width=0.2,
               label=label[val], color=colors[i], alpha = 0.87)
    # ax.bar(x, df_comb.values, yerr=df_comb_std.values / 2, width=0.4, alpha=0.87)
    ax.axhline(y=1, xmin=0, xmax=1, color='black', ls='--')

    ax.set_ylabel('Effective Reproductive Number', size=16)
    ax.set_title(f'Effective Reproductive Number by School Reopening Strategy', size=16, horizontalalignment='center')
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

    fig.savefig(f'r_eff_{prev}_{cases}_{date_of_file}.png', format='png')


def get_re(cases, num_param_set, date_of_file, sens):
    df_mean = []
    for case in cases:
        df_mean.append(combine_results_dfs('all_remote', num_param_set, 'r_eff', True, date_of_file, case, sens))

    df_mean = pd.DataFrame(df_mean).transpose()
    base = dt.datetime(2020, 7, 1)
    date_list = [base + dt.timedelta(days=x) for x in range(len(df_mean[0]))]
    x = []
    for date in date_list:
        x.append(date.strftime('%b %d'))

    date_to_x = {d: i for i, d in enumerate(x)}
    min_x = date_to_x['Sep 01']
    max_x = date_to_x['Dec 01']
    df_mean = df_mean.iloc[min_x:max_x, ]
    df_mean = df_mean.mean(axis=0)

    return(df_mean.values)


def get_inc(cases, num_seeds, date, sens):
    df_sum = []
    for case in cases:
        df_sum.append(combine_results_dfs('all_remote', num_seeds, 'new_diagnoses', True, date, case, sens))

    df_sum = pd.DataFrame(df_sum).transpose()
    base = dt.datetime(2020, 7, 1)
    date_list = [base + dt.timedelta(days=x) for x in range(len(df_sum[0]))]
    x = []
    for date in date_list:
        x.append(date.strftime('%b %d'))

    date_to_x = {d: i for i, d in enumerate(x)}
    min_x = date_to_x['Aug 16']
    max_x = date_to_x['Aug 30']

    df_sum = df_sum.iloc[min_x:max_x, ]
    df_sum = df_sum.sum(axis=0).values
    df_sum = df_sum* 100e3/ 2.25e6
    return (df_sum)


def plot_dimensions(date_of_file, cases, sens):

    name = 'Cases per 100k in last 14 days'
    if '1.1' in cases[0]:
        prev = 'by_cases_rising'
        subtitle = '(Re > 1)'
    else:
        prev = 'by_cases_falling'
        subtitle = '(Re < 1)'
    label = inc_labels

    if sens is not None:
        prev = prev + '_' + sens
        subtitle += f'\n ({sens_label[sens]})'

    attack_rate_by_case = []
    perc_school_days_lost_by_case = []
    efficient_y_by_case = []
    efficient_x_by_case = []

    for _, case in enumerate(cases):
        df = outputs_df(date_of_file, case, sens)
        scenario_strategies = df.columns[1:]
        scenario_strategies = scenario_strategies.tolist()
        scenario_strategies.remove('all_remote')
        perc_school_days_lost = []
        # perc_school_days_lost = [0,	0,	60.76923077,	34.72494893,	59.94845764,	84.83944482]
        # total = df[df['Unnamed: 0'] == 'num_staff']['as_normal'].values
        # total += df[df['Unnamed: 0'] == 'num_teachers']['as_normal'].values
        # total = df[df['Unnamed: 0'] == 'num_students']['as_normal'].values
        attack_rate = []
        efficient_y = []
        efficient_x = []
        weekend_days = df[df['Unnamed: 0'] == 'school_days_lost']['with_screening'].values
        total_school_days = df[df['Unnamed: 0'] == 'student_school_days']['with_screening'].values
        for n, strategy in enumerate(scenario_strategies):
            total = df[df['Unnamed: 0'] == 'num_staff'][strategy].values
            total += df[df['Unnamed: 0'] == 'num_teachers'][strategy].values
            total += df[df['Unnamed: 0'] == 'num_students'][strategy].values

            num_cases = df[df['Unnamed: 0'] == 'num_staff_cases'][strategy].values
            num_cases += df[df['Unnamed: 0'] == 'num_teacher_cases'][strategy].values
            num_cases += df[df['Unnamed: 0'] == 'num_student_cases'][strategy].values

            attack_rate.append(100 * num_cases[0] / total[0])

            school_days_lost = df[df['Unnamed: 0'] == 'school_days_lost'][strategy].values
            if strategy != 'as_normal':
                school_days_lost = school_days_lost[0] - weekend_days[0]
                perc_school_days_lost.append(100 * school_days_lost/total_school_days[0])
            else:
                perc_school_days_lost.append(100 * school_days_lost[0] / total_school_days[0])

            if strategy != 'with_hybrid_scheduling':
                efficient_y.append(attack_rate[n])
                efficient_x.append(perc_school_days_lost[n])

        attack_rate = pd.DataFrame(attack_rate).transpose()
        attack_rate_by_case.append(attack_rate)

        efficient_y = pd.DataFrame(efficient_y).transpose()
        efficient_y_by_case.append(efficient_y)
        efficient_x = pd.DataFrame(efficient_x).transpose()
        efficient_x_by_case.append(efficient_x)

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
        ax.plot(efficient_x_by_case[j].iloc[0, :].values, efficient_y_by_case[j].iloc[0, :].values, linewidth=3, alpha=0.33, color='grey', linestyle='-')
        for i in range(n_strategies):
            ax.plot(perc_school_days_lost_by_case[j][i], attack_rate_by_case[j][i], marker='o', markersize=sizes[j], alpha=alpha,
                    markerfacecolor=colors[i],
                    markeredgewidth=0,
                    )

        ax.set_xlabel('Days of Distance Learning (% of Total School Days)', fontsize=16)
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
        ax_leg.plot(-5, -5, color=colors[s], label=strategy_labels_2[strat])

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
        ax_leg_2.text(xi * 4, yi, (label[cases[i]]), verticalalignment='center', fontsize=16)

        ax_leg_2.text(xi * 7, 0.985, f'{name}', horizontalalignment='center', fontsize=18)

    ax_leg_2.axis('off')
    ax_leg_2.set_xlim(left=0, right=20)
    ax_leg_2.set_ylim(bottom=ybase * 0.9, top=ytop * 1.0)

    ax.set_title(f'Trade-Offs with School Reopening', fontsize=20)
    fig.savefig(f'tradeoffs_{prev}_{date_of_file}.png', format='png')


if __name__ == '__main__':
    num_seeds = 20

    by_case = True

    if by_case:
        cases = ['20_cases', '50_cases', '110_cases']
        re = 're_0.9'
        # cases_rising = False
        # if cases_rising:
        #     re = 're_1.1'
        # else:
        #     re = 're_0.9'

        for i, case in enumerate(cases):
            cases[i] = case + '_' + re
    else:
        cases = ['50_cases_re_0.9']

    rel_trans = 'under10_0.5trans'
    beta_layer = '3xschool_beta_layer'
    #sens = beta_layer
    #sens = rel_trans
    sens = None
    date = '2020-08-05'

    comm_inc = get_inc(cases, num_seeds, date, sens)
    comm_re = get_re(cases, num_seeds, date, sens)
    # for i, case in enumerate(cases):
    #     inc_labels[case] = round(comm_inc[i], 0)
    #
    print(comm_inc)
    print(comm_re)

    # if sens is not None:
    #     for val in cases:
    #         plot_reff_by_sens(val, num_seeds, date, sens)
    #         plot_attack_rate_by_sens(date, val, sens)
    #
    # plot_reff(cases, num_seeds, date, sens)
    # plot_attack_rate(date, cases, sens)
    # plot_dimensions(date, cases, sens)


    # plot_reff(cases, num_seeds, date, sens)
    plot_attack_rate(date, cases, sens)
    # plot_dimensions(date, cases, sens)
    plot_reff_combined(num_seeds, date)

    print('done')
