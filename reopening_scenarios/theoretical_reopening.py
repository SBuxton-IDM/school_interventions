'''Show optimized runs'''

import covasim as cv


create_pop = False
rerun = True
load_pop = True
popfile = f'inputs/hybrid_100k.ppl'

# schools_closure_scenarios = ['close_on_5', 'close_on_10', 'close_on_100']
# num_pos = [5, 10, 100]

schools_closure_scenarios = ['notrigger', 'close_on_5_tracing_at_home', 'close_on_5_no_tracing_at_home', 'close_on_100_tracing_at_home', 'close_on_100_no_tracing_at_home']
num_pos = [None, 5, 5, 100, 100]
trace_athome = [None, True, False, True, False]

# schools_closure_scenarios = ['close_on_100']
# num_pos = [100]

pars = {'pop_size'      : 100e3,
        'n_imports'     : 400,
        'pop_type'      : 'hybrid',
        'start_day'     : '2020-08-30',
        'end_day'       : '2020-10-01'
        }

# if create_pop:
#     sim = cv.Sim(pars)
#     cv.make_people(sim, popfile=popfile, save_pop=True, school_type=True,
#                    school_type_ages=[[6, 11], [11, 14], [14, 18], [18, 22]])

if rerun:
    all_sims = []
    for i, scen in enumerate(schools_closure_scenarios):
        sim = cv.Sim(pars, popfile=popfile, load_pop=load_pop, label=scen)
        interventions = [cv.test_prob(start_day=0, symp_prob=0.06, asymp_prob=0.0006, symp_quar_prob=1.0,
                         asymp_quar_prob=1.0, quar_policy='start', test_delay=2)]
        if i != 0:
            interventions += [cv.close_schools(start_day='2020-08-30', num_pos=num_pos[i], ili_prev=0.1, trace_athome=trace_athome[i])]

        sim['interventions'] = interventions
        all_sims.append(sim)

    msim = cv.MultiSim(all_sims)

    if __name__ == '__main__':
        msim.run()
        cv.save(filename=f'theoretical_closure.msim', obj=msim)
        fig1 = msim.plot(to_plot=['n_infectious'], do_show=True)
        fig3 = msim.plot(to_plot=['cum_infections'], do_show=True)

else:
    msim = cv.load('theoretical_closure.msim')
    msim



