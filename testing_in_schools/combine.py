# TODO: move to utils
import covasim as cv
import os

folder = 'v20201015_225k'

fns = [
        'batch_15-30_as_normal.msim',
        'batch_15-30_with_countermeasures.msim',
        'batch_15-30_all_hybrid.msim',
        'batch_15-30_all_remote.msim',
        'batch_15-30_k5.msim',
        'batch_15-30.msim',
]

fns = [os.path.join(folder, 'msims', fn) for fn in fns]

msims = []
for fn in fns:
    msims.append( cv.MultiSim.load(fn) )

msim = cv.MultiSim.merge(msims)
msim.save('new_antigen_tests.msim')
