# TODO: move to utils
import covasim as cv
import os

folder = 'v20201016_225k'

fns = [
    'batch_final_20-30.msim',
    'batch_final_0-20_all_remote.msim',
    'batch_final_0-20_k5.msim',
    'batch_final_0-20_all_hybrid.msim',
    'batch_final_0-20_as_normal.msim',
    'batch_final_0-20_with_countermeasures.msim',
]

fns = [os.path.join(folder, 'msims', fn) for fn in fns]

msims = []
for fn in fns:
    msims.append( cv.MultiSim.load(fn) )

msim = cv.MultiSim.merge(msims)
msim.save('batch_final_0-30.msim')
