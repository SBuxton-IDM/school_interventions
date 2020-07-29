import covasim as cv

filename = 'all_scens.msims'
msims = cv.load(filename)

sim = msims[0].sims[0]
tt = sim.make_transtree()
tt.plot()

print('Done')