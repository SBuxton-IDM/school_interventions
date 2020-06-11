import sciris as sc
import covasim as cv

with_school_types = True
school_mixing_type = 'clustered'

pars = sc.objdict(
        pop_size = 225e3,
        pop_type = 'synthpops',
        rand_seed = 1,
    )

popfile = f'inputs/kc_synthpops_seed{pars.rand_seed}.ppl'

sim = cv.Sim(pars)
cv.make_people(sim, popfile=popfile, save_pop=True, generate=True, with_facilities=True,
               with_school_types=with_school_types, school_mixing_type=school_mixing_type)


sim

