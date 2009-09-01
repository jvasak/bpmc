#!/usr/bin/python

import sys
import logging
from optparse import OptionParser

from nfl import NFL

LOGGING_LEVELS = {'critical': logging.CRITICAL,
                  'error'   : logging.ERROR,
                  'warning' : logging.WARNING,
                  'info'    : logging.INFO,
                  'debug'   : logging.DEBUG}

def main():
    usage   = "usage: %prog [options] beatpower.csv schedule.csv"
    version = "%prog 0.10"

    parser = OptionParser(usage=usage, version=version)
    parser.add_option("-s", "--sigma", dest="sigma", type="float",
                      help="float value to use for variance",
                      metavar="SIGMA", default=10.0)
    parser.add_option('-l', '--logging-level', help='Logging level')
    parser.add_option('-f', '--logging-file', help='Logging file name')
    (options, args) = parser.parse_args()

    logging_level = LOGGING_LEVELS.get(options.logging_level, logging.WARN)
    logging.basicConfig(level=logging_level, filename=options.logging_file,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    logging.debug("Option parsing finished with " + str(len(args)) + " args left")

    if len(args) < 2:
        parser.print_help()
        sys.exit(1)

    league = NFL()
    
    if not league.loadSeasonInfo(args[0], args[1]):
        sys.exit(1)

    league.simulateSeason()
    
    sys.exit(0)
    

if __name__ == "__main__":
    main()






    # Dump structure (debugging)
    # nfl.listChildren()
    
    # Test getting of teams from conference
    #confs = nfl.getChildren()
    #for conf in confs:
    #    if confs[conf].getName() == 'NFC':
    #        nfc = confs[conf]
    #        break
    #if nfc:
    #    teams = nfc.getTeams()
    #    for team in teams:
    #        print team.getName()
    #else:
    #    print "Could not find NFC"
    #    sys.exit(1)

    #vikes = nfl.getTeam('MIN')
    #print '---------------'
    #print vikes.getName()

    #afc = nfl.getTeam('AFC')
    #if afc is None:
    #    print 'Ack!!'
    #else:
    #    vikes = afc.getTeam('MIN')
    #    if not vikes is None:
    #        print 'Ack again!!'
