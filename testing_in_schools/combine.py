# TODO: move to utils
import covasim as cv
import os

folder = 'v20201019'

fns = [
    'batch_final_updated_antigen_0-30.sims',
    'batch_final_1wAntigen_0-30.msim',
]

fns = [os.path.join(folder, 'msims', fn) for fn in fns]

sims = []
for fn in fns:
    print(f'Loading {fn}')
    ext = os.path.splitext(fn)[1]
    if ext == '.sims':
        sims += cv.load(fn)
    elif ext == '.msim':
        msim = cv.MultiSim.load(fn)
        sims += msim.sims
    else:
        print('ERROR')

cv.save(os.path.join(folder, 'msims', 'batch_final_updatedAntigen_1wAntigen_0-30.sims'), sims)
