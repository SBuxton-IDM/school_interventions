import pylab as pl
import numpy as np
import pandas as pd
import matplotlib as mplt
import sciris as sc

# Global plotting styles
font_size = 16
font_style = 'Roboto Condensed'
# font_style = 'Barlow Condensed'
# font_style = 'Source Sans Pro'
mplt.rcParams['font.size'] = font_size
mplt.rcParams['font.family'] = font_style


raw_data = sc.odict({' 20': sc.odict({'es': 5.8,  'ms':8.0, 'hs':6.9}),
                 ' 50': sc.odict({'es': 13.9, 'ms':18.3, 'hs':16.1}),
                 '110': sc.odict({'es': 26,   'ms':33, 'hs':42}),
                 })

labels = {'es':'Elementary\nschool', 'ms':'Middle\nschool', 'hs':'High\nschool', }

# Ooops, data wrong way around
data = sc.odict(pd.DataFrame(raw_data).T.to_dict())

fig = pl.figure(figsize=(10, 6))
ax = pl.subplot(111)
fig.subplots_adjust(hspace=0.3, right=0.9, bottom=0.15)
fig.suptitle(f'Schools with at least one infected person on the first day of term', size=24, horizontalalignment='center')

colors = ['lightseagreen', 'lightsteelblue', 'lightcoral']

x = np.arange(len(labels))

width = [-.2, 0, .2]
for j, label, schooldata in data.enumitems():
    ax.bar(x + width[j], schooldata.values(), width=0.2, label=raw_data.keys()[j], color=colors[j])
ax.set_ylabel('Schools with a case (%)', size=20)
# ax.set_ylim([0,25])
ax.set_xticks(x)
ax.set_xticklabels(labels.values(), fontsize=16)

name = 'Cases per 100k people during the\ntwo weeks prior to school reopening'
leg_i = ax.legend(fontsize=16, title=name)
leg_i.set_title(name, prop={'size': 16})