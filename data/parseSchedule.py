#!/usr/bin/python

import sys
import re
import csv
from optparse import OptionParser

def loadTeamDict():
    return (dict({'Indianapolis'    : 'IND',
                  'New York Jets'   : 'NYJ',
                  'Tennessee'       : 'TEN',
                  'Pittsburgh'      : 'PIT',
                  'New York Giants' : 'NYG',
                  'New England'     : 'NE',
                  'Baltimore'       : 'BAL',
                  'Arizona'         : 'ARI',
                  'Miami'           : 'MIA',
                  'Carolina'        : 'CAR',
                  'Dallas'          : 'DAL',
                  'Denver'          : 'DEN',
                  'Minnesota'       : 'MIN',
                  'Houston'         : 'HOU',
                  'Atlanta'         : 'ATL',
                  'Cincinnati'      : 'CIN',
                  'San Francisco'   : 'SF',
                  'Philadelphia'    : 'PHI',
                  'Chicago'         : 'CHI',
                  'Tampa Bay'       : 'TB',
                  'Buffalo'         : 'BUF',
                  'New Orleans'     : 'NO',
                  'San Diego'       : 'SD',
                  'Washington'      : 'WAS',
                  'Cleveland'       : 'CLE',
                  'Oakland'         : 'OAK',
                  'Jacksonville'    : 'JAX',
                  'Green Bay'       : 'GB',
                  'Kansas City'     : 'KC',
                  'Seattle'         : 'SEA',
                  'Detroit'         : 'DET',
                  'St. Louis'       : 'STL'
                  }))

if __name__ == "__main__":
    """Main processing loop for parsing BeatPower from saved HTML"""

    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="parse HTML FILE for season schedule", 
                      metavar="FILE")
    parser.add_option("-o", "--outfile", dest="outfile",
                      help="comma-separated output file (.csv)",
                      metavar="OUTFILE")
    (options, args) = parser.parse_args()

    if options.filename is None:
        print "Must specify file to parse.  Use --help for syntax"
        sys.exit(-1)

    if options.outfile is None:
        print "Must specify output file.  Use --help for syntax"
        sys.exit(-1)

    teamMap = loadTeamDict()

    skdWriter = csv.writer(open(options.outfile, 'w'), delimiter=',',
                          quotechar='|', quoting=csv.QUOTE_MINIMAL) 
    skdWriter.writerow(['week','away','home'])

    with open(options.filename) as f:
        week_re = re.compile('a name="(\d+)"')
        away_re = re.compile('^\s+<td>\s([\w \.]+?)\s+$')
        home_re = re.compile('^\s+([\w \.]+)\s</td>\s+$')
        end_re  = re.compile('</table>')
        week    = None

        for line in f:
            if week is None:
                res = week_re.search(line)
                if res:
                    week = res.group(1)
            else:
                end = end_re.search(line)
                if end:
                    week = None
                    continue
                res = away_re.search(line)
                if res:
                    away = res.group(1)
                    f.next() # throw away 'at' line
                    nxt  = f.next()
                    res  = home_re.search(nxt)
                    if res is None:
                        print "Parsing error"
                        sys.exit(1)
                    home = res.group(1)
                    skdWriter.writerow([week,teamMap[away],teamMap[home]])
                    
    sys.exit(0)

