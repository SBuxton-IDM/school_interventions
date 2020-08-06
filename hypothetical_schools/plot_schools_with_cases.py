'''
Plot number of schools with >=1 infection, replacing the table
'''

import pylab as pl
import numpy as np
import matplotlib as mplt
import sciris as sc
import covasim as cv

# Global plotting styles
font_size = 16
font_style = 'Roboto Condensed'
mplt.rcParams['font.size'] = font_size
mplt.rcParams['font.family'] = font_style
date = '2020-08-05'


# Define the data
print('Be careful, data are hard-coded!')
data = sc.odict({' 20': sc.odict({'es': 5.8,  'ms':8.0, 'hs':6.9}),
                 ' 50': sc.odict({'es': 13.9, 'ms':18.3, 'hs':16.1}),
                 '110': sc.odict({'es': 26,   'ms':33, 'hs':42}),
                 })


# Labels and options
labels = {'es':'Elementary\nschool', 'ms':'Middle\nschool', 'hs':'High\nschool'}
name = 'Cases per 100k people during the\ntwo weeks prior to school reopening'
colors = ['lightseagreen', 'lightsteelblue', 'lightcoral']
x = np.arange(len(labels))
width = [-.2, 0, .2]


# Actual plotting
fig = pl.figure(figsize=(10, 6))
ax = pl.subplot(111)
fig.subplots_adjust(hspace=0.3, right=0.9, bottom=0.15)
fig.suptitle(f'Schools with at least one infected person on the first day of term', size=24, horizontalalignment='center')

for j, schooldata in data.enumvals():
    ax.bar(x + width[j], schooldata.values(), width=0.2, label=data.keys()[j], color=colors[j])
ax.set_ylabel('Schools with a case (%)', size=20)
ax.set_xticks(x)
ax.set_xticklabels(labels.values(), fontsize=font_size)

leg_i = ax.legend(fontsize=font_size, title=name)
leg_i.set_title(name, prop={'size': font_size})


# Tidying
cv.savefig(f'schools_with_a_case_{date}.png')
print('Done.')