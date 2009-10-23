#!/usr/bin/python

from urllib  import urlretrieve
from os      import chdir, mkdir
from os.path import exists

years = range(2001,2010)
regs  = [("REG%d"  % x) for x in range( 1, 18)]
ps    = [("POST%d" % x) for x in range(18, 22)]

for y in years:
    sdir = 'scores/' + str(y)
    if not exists(sdir):
        mkdir(sdir)
    chdir(sdir)

    weeks = regs
    if y != 2009:
        weeks.extend(ps)

    for w in weeks:
        if not exists(w):
            url = "http://www.nfl.com/scores/%d/%s" % (y, w)
            urlretrieve(url, w)

    chdir("../..")
