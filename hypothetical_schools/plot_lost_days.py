'''
Run after theoretical_reopening
'''

import covasim as cv

sdict = cv.load('sdict.obj')

for k in sdict.keys():
    a = sdict[k].school_info['school_days_lost']
    b = sdict[k].school_info['total_student_school_days']
    c = a/b
    print(f'{k:45s}: {a:10.0f}, {b:0.0f}, {c:0.2f}')