import covasim as cv
import pandas as pd

msim = cv.MultiSim.load('msim.obj')

dfs = []
for sim_id, sim in enumerate(msim.sims):
    df = pd.DataFrame(msim.sims[0].school_stats).T
    df.drop('scenario', axis=1, inplace=True)
    df = df.loc[df['type'].isin(['es', 'ms', 'hs'])]
    df.index.name = 'school_id'
    df['sim_id'] = sim_id
    dfs.append(df)

df = pd.concat(dfs)
cols = ['cum_unique_students_at_school_while_infectious', 'n_students']
for col in cols:
    df[col] = df[col].astype('int')

#print(df)
print(df.dtypes)

df['Frac students at home'] = df['cum_unique_students_at_school_while_infectious'] / df['n_students']

mu = df.groupby(['type'])['Frac students at home'].mean()
print(mu)

#msim.plot()
