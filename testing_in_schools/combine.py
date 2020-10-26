# TODO: move to utils
import covasim as cv
import os

folder = 'v20201019'

fns = [
    'sensitivity_v2_0-5.msim',
    'sensitivity_v2_5-10.msim',
    'sensitivity_v2_10-15.msim',
    'sensitivity_v2_15-30.msim',
]

fns = [os.path.join(folder, 'msims', fn) for fn in fns]

msims = []
for fn in fns:
    msims.append( cv.MultiSim.load(fn) )

msim = cv.MultiSim.merge(msims)
sims = msim.sims
cv.save(os.path.join(folder, 'msims', 'sensitivity_v2_0-30.sims'), sims)
