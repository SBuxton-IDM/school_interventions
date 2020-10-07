import covasim as cv
import pandas as pd

msim = cv.MultiSim.load('msim.obj')

df = pd.DataFrame(msim.sims[0].school_stats).T

print(df.loc[5]['n_students_at_school_while_infectious'])

#msim.plot()
