import sciris as sc

files = sc.getfilelist('./inputs')
n_files = len(files)

pops = []
for fn in files:
    print(f'Working on {fn}...')
    pops.append(sc.loadobj(fn))

#%%
school_ids = []
school_ids_type = []
for p,pop in enumerate(pops):
    school_ids_type.append(sc.objdict())
    inds = [i for i,val in enumerate(pop.school_id) if val is not None]
    ids = set(pop.school_id[inds])
    for ind in inds:
        kind = pop.school_type_by_person[ind]
        sid = pop.school_id[ind]
        if kind not in school_ids_type[-1]:
            school_ids_type[-1][kind] = {sid:1}
        elif sid not in school_ids_type[-1][kind]:
            school_ids_type[-1][kind][sid] = 1
        else:
            school_ids_type[-1][kind][sid] += 1
    for k in school_ids_type[-1].keys():
        school_ids_type[-1][k] = len(school_ids_type[-1][k])
    print(f'School {files[p]} has {len(ids)} unique schools')
    print(school_ids_type[-1])
    print(school_ids_type[-1]['es'] + school_ids_type[-1]['ms'] + school_ids_type[-1]['hs'])
    school_ids.append(ids)
