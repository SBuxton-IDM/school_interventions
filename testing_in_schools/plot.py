import covasim as cv
import pandas as pd

msim = cv.MultiSim.load('msim.obj')

ss = []
for sim_id, sim in enumerate(msim.sims):
    print(sim.rescale_vec)
    for sid,stats in sim.school_stats.items():
        if stats['type'] not in ['es', 'ms', 'hs']:
            continue

        s = {
            'type': stats['type'],
            'inc': sim.par['inc'],
            'inf_students': stats['cum_unique_students_at_school_while_infectious'],
            'n_students': stats['n_students'],
            'sid': sid
        }
        ss.append(s)

df = pd.DataFrame(ss)

#cols = ['cum_unique_students_at_school_while_infectious', 'n_students']
#for col in cols:
#    df[col] = df[col].astype('int')

#print(df)
print(df.dtypes)

df['Frac students at home'] = df['inf_students'] / df['n_students']

mu = df.groupby(['type', 'inc'])['Frac students at home'].mean().unstack(level=1)
print(mu)

#msim.plot()
