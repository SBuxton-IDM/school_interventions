'''
Run after theoretical_reopening_explorations. Does not plot. Sorry for the misinformation
'''

import covasim as cv

sdict = cv.load('sdict.obj')

print('columns: scenario, gained, lost, total, lost/total, gained+lost')
for k in sdict.keys():
    q = sdict[k].school_info['school_days_gained']
    a = sdict[k].school_info['school_days_lost']
    b = sdict[k].school_info['total_student_school_days']
    c = a/b
    d = q+a
    print(f'{k:45s}: {q:10.0f}, {a:10.0f}, {b:0.0f}, {c:0.2f}, {d:0.0f}')