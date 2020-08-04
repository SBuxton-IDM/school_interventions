import covasim as cv
import sciris as sc
import pandas as pd
import matplotlib as mplt
import matplotlib.pyplot as plt
import math
import os
import datetime as dt
import palettable

schools_reopening_scenarios = [
        'as_normal',
        'with_screening',
        'with_hybrid_scheduling',
        'ES_MS_inperson_HS_remote',
        'ES_inperson_MS_HS_remote',
        'ES_hybrid',
        'all_remote',
    ]

schools_reopening_scenarios_label = [
        'As Normal',
        'With Screening',
        'All Hybrid',
        'ES/MS in Person, HS Remote',
        'ES in Person, MS/HS Remote',
        'ES Hybrid',
        'All Remote',
    ]


# res = ['0.9', '1.1']
res = ['0.9']
cases = ['20', '50', '110']

for re in res:
    for case in cases:
        es_with_a_case = []
        ms_with_a_case = []
        hs_with_a_case = []
        for i, scen in enumerate(schools_reopening_scenarios):
            analysis_name = f'{scen}_{case}_cases_re_{re}'
            filename = f'msims/{analysis_name}.msim'
            msim = cv.load(filename)
            del msim.orig_base_sim
            es = []
            ms = []
            hs = []
            df = []
            for j in range(len(msim.sims)):
                results = pd.DataFrame(msim.sims[j].results)
                df.append(results)
                num_es = msim.sims[j].school_info['num_es']
                num_ms = msim.sims[j].school_info['num_ms']
                num_hs = msim.sims[j].school_info['num_hs']
                es.append(pd.DataFrame(msim.sims[j].school_info['es_with_a_case']))
                ms.append(pd.DataFrame(msim.sims[j].school_info['ms_with_a_case']))
                hs.append(pd.DataFrame(msim.sims[j].school_info['hs_with_a_case']))

            es_concat = pd.concat(es)
            by_row_index = es_concat.groupby(es_concat.index)
            es_means = by_row_index.mean()
            es_means.columns = [scen]
            es_with_a_case.append(es_means/num_es)

            ms_concat = pd.concat(ms)
            by_row_index = ms_concat.groupby(ms_concat.index)
            ms_means = by_row_index.mean()
            ms_means.columns = [scen]
            ms_with_a_case.append(ms_means/num_ms)

            hs_concat = pd.concat(hs)
            by_row_index = hs_concat.groupby(hs_concat.index)
            hs_means = by_row_index.mean()
            hs_means.columns = [scen]
            hs_with_a_case.append(hs_means/num_hs)

        es_with_a_case = pd.concat(es_with_a_case, ignore_index=True, axis=1)
        es_with_a_case.columns = schools_reopening_scenarios_label
        ms_with_a_case = pd.concat(ms_with_a_case, ignore_index=True, axis=1)
        ms_with_a_case.columns = schools_reopening_scenarios_label
        hs_with_a_case = pd.concat(hs_with_a_case, ignore_index=True, axis=1)
        hs_with_a_case.columns = schools_reopening_scenarios_label


