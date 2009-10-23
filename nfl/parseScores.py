#!/usr/bin/python

from os          import chdir
from os.path     import exists
from elementtidy import TidyHTMLTreeBuilder

import logging
import csv

logging.basicConfig(level=logging.DEBUG)

years = range(2001,2010)
regs  = [("REG%d"  % x) for x in range( 1, 18)]
ps    = [("POST%d" % x) for x in range(18, 22)]

xhtml = "{http://www.w3.org/1999/xhtml}"
div   = "%s%s" % (xhtml, 'div')
ul    = "%s%s" % (xhtml, 'ul')
li    = "%s%s" % (xhtml, 'li')

for y in years:
    logging.debug("Starting on %d" % y)
    sdir = 'scores/' + str(y)
    if not exists(sdir):
        continue

    dataout = csv.writer(open("%d.csv" % y, 'w'), delimiter=',',
                         quotechar='|', quoting=csv.QUOTE_MINIMAL)
    dataout.writerow(['season', 'week', 'away', 'home', 'awayscore', 'homescore'])

    chdir(sdir)

    weeks = regs[:]
    if y != 2009:
        weeks.extend(ps)

    for i in range(len(weeks)):
        w = weeks[i]
        if not exists(w):
            logging.error("No data for %d %s" % (y, w))
            continue

        tree  = TidyHTMLTreeBuilder.parse(w)
        for elt in tree.getiterator():
            if elt.tag == div and elt.get('class') == 'col scorebox-container':
                game = dict()
                uls = elt.findall('.//'+ul)
                for u in uls:
                    if u.get('class').endswith('-team'):
                        for l in u.getiterator():
                            if l.tag == li and l.get('class') == 'team-logo':
                                game[u.get('class')[0:4]] = l.get('id')
                                break
                divs = elt.findall('.//'+div)
                for d in divs:
                    if d.get('class') is not None and d.get('class').endswith('-score'):
                        for s in d.getiterator():
                            if s.tag == div and s.get('class') == 'the-score':
                                if s.text == '--':
                                    game[d.get('class')[0:4]+'score'] = s.text
                                else:
                                    game[d.get('class')[0:4]+'score'] = int(s.text)
                                break
                logging.debug("%3s %2s @ %2s %-3s" % (game['away'], str(game['awayscore']),
                                                      str(game['homescore']), game['home']))
                dataout.writerow([y, i+1, game['away'], game['home'], game['awayscore'], game['homescore']])

    chdir("../..")
