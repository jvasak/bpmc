#!/usr/bin/python

import sys
import re
import csv
from optparse import OptionParser

def resetTeamPower():
    return (None, None)

def loadTeamDict():
    return (dict({'colts'     : 'IND',
                  'jets'      : 'NYJ',
                  'titans'    : 'TEN',
                  'steelers'  : 'PIT',
                  'giants'    : 'NYG',
                  'patriots'  : 'NE',
                  'ravens'    : 'BAL',
                  'cardinals' : 'ARI',
                  'dolphins'  : 'MIA',
                  'panthers'  : 'CAR',
                  'cowboys'   : 'DAL',
                  'broncos'   : 'DEN',
                  'vikings'   : 'MIN',
                  'texans'    : 'HOU',
                  'falcons'   : 'ATL',
                  'bengals'   : 'CIN',
                  '49ers'     : 'SF',
                  'eagles'    : 'PHI',
                  'bears'     : 'CHI',
                  'buccaneers': 'TB',
                  'bills'     : 'BUF',
                  'saints'    : 'NO',
                  'chargers'  : 'SD',
                  'redskins'  : 'WAS',
                  'browns'    : 'CLE',
                  'raiders'   : 'OAK',
                  'jaguars'   : 'JAX',
                  'packers'   : 'GB',
                  'chiefs'    : 'KC',
                  'seahawks'  : 'SEA',
                  'lions'     : 'DET',
                  'rams'      : 'STL'
                  }))

if __name__ == "__main__":
    """Main processing loop for parsing BeatPower from saved HTML"""

    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="parse HTML FILE for team BeatPower scores", 
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

    bpWriter = csv.writer(open(options.outfile, 'w'), delimiter=',',
                          quotechar='|', quoting=csv.QUOTE_MINIMAL) 

    with open(options.filename) as f:
        (team, power) = resetTeamPower()
        team_re  = re.compile('nflimg.(\w+)_65')
        power_re = re.compile('<h3>([0-9\.]+)</h3>')
        curr_re  = team_re
        for line in f:
            res = curr_re.search(line)
            if res:
                if team is None:
                    team = res.group(1)
                    curr_re = power_re
                else:
                    bpWriter.writerow([teamMap[team], res.group(1)])
                    (team, power) = resetTeamPower()
                    curr_re = team_re

    sys.exit(0)

