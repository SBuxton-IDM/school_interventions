import covasim as cv

filename = 'all_scens.msims'
msims = cv.load(filename)

sim = msims[0].sims[0]
sim.plot(to_plot='overview')
tt = sim.make_transtree()
tt.plot()

print('Done')