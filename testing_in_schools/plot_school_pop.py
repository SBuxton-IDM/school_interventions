import covasim as cv

fn = 'inputs/kc_synthpops_clustered_withstaff_seed0.ppl'

sim = cv.Sim(pop_size=225e3, pop_type='synthpops', popfile=fn, load_pop=True)
sim.initialize()
sim.people.plot()

cv.savefig('people_plot.png')
