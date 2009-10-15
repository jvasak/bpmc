#!/usr/bin/python

import sys
import logging
import random
from   optparse import OptionParser

from nfl  import NFL
from ddpl import DDPL

LOGGING_LEVELS = {'critical': logging.CRITICAL,
                  'error'   : logging.ERROR,
                  'warning' : logging.WARNING,
                  'info'    : logging.INFO,
                  'debug'   : logging.DEBUG}

def main():
    usage   = "usage: %prog [options] schedule.csv"
    version = "%prog 0.10"

    parser = OptionParser(usage=usage, version=version)
    parser.add_option("-i", "--iterations", dest="iterations", type="int",
                      help="number of simulations to run",
                      metavar="NUM", default=1000)
    parser.add_option("-b", "--beatpower", dest="bpfile", type="string",
                      help="csv file with beatpower scores",
                      metavar="FILE")
    parser.add_option("-e", "--edgepower", dest="edge", action="store_true",
                      help="Use alternate EdgePower", default=False)
    parser.add_option("-d", "--ddpl", dest="ddpl", action="store_true",
                      help="Operate on DDPL data", default=False)
    parser.add_option("-w", "--week", dest="week", type="int",
                      help="week to simulate from (default: latest)",
                      metavar="NUM", default=None)
    parser.add_option('-l', '--logging-level', help='Logging level')
    parser.add_option('-f', '--logging-file', help='Logging file name')
    (options, args) = parser.parse_args()

    logging_level = LOGGING_LEVELS.get(options.logging_level, logging.WARN)
    logging.basicConfig(level=logging_level, filename=options.logging_file,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    logging.debug("Option parsing finished with " + str(len(args)) + " args left")

    if len(args) < 1:
        parser.print_help()
        sys.exit(1)
    
    if options.ddpl:
        league = DDPL()
    else:
        league = NFL()

    if not league.loadCsvSchedule(args[0]):
        logging.critical("Error loading season schedule")
        sys.exit(1)

    if options.bpfile is not None:
        if league.isPartialSeason():
            logging.warn("Cannot overwrite partial season beatpower")
        else:
            if not league.loadBeatPower(options.bpfile):
                logging.critical("Error loading beatpower file")
                sys.exit(1)

    if options.iterations > 0:
        random.seed()
        for i in range(1, options.iterations + 1):
            logging.info("###==================================###")
            logging.info("   Iteration " + str(i) + " of " + str(options.iterations))
            league.simulateSeason(options.week)
            if i % 10  == 0 and not i % 100 == 0: print '.',; sys.stdout.flush()
            if i % 100 == 0:                      print '#',; sys.stdout.flush()
            if i % 200 == 0:                      print ' %8d' % i

        print
        league.printStats(plots=True)

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
