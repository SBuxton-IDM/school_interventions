import covasim as cv
import os

folder = 'v20201019'

fns = [
    'final_20201026_v2_0-10.msim', 
    'final_20201026_v2_10-20.msim', 
    'final_20201026_v2_20-30.msim',
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

fn = os.path.join(folder, 'msims', 'final_20201026_v2_0-30.sims')
print(f'Saving to {fn}')
cv.save(fn, sims)
