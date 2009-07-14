#!/usr/bin/python

import sys
import csv
import pickle
from optparse import OptionParser

from league import League
from league import Conference
from league import Division
from league import Team

def setupNFL():
    """Create structure for NFL teams"""

    nfl = League('NFL')
    
    afc = Conference('AFC')
    nfc = Conference('NFC')

    nfl.addChild(afc)
    nfl.addChild(nfc)

    afce = Division('East')
    afcn = Division('North')
    afcs = Division('South')
    afcw = Division('West')

    afc.addChild(afce)
    afc.addChild(afcn)
    afc.addChild(afcs)
    afc.addChild(afcw)

    afce.addChild(Team('Buffalo Bills',        'BUF'))
    afce.addChild(Team('Miami Dolphins',       'MIA'))
    afce.addChild(Team('New England Patriots', 'NE'))
    afce.addChild(Team('New York Jets',        'NYJ'))

    afcn.addChild(Team('Baltimore Ravens',     'BAL'))
    afcn.addChild(Team('Cincinnati Bengals',   'CIN'))
    afcn.addChild(Team('Cleveland Browns',     'CLE'))
    afcn.addChild(Team('Pittsburgh Steelers',  'PIT'))

    afcs.addChild(Team('Houston Texans',       'HOU'))
    afcs.addChild(Team('Indianapolis Colts',   'IND'))
    afcs.addChild(Team('Jacksonville Jaguars', 'JAX'))
    afcs.addChild(Team('Tennessee Titans',     'TEN'))

    afcw.addChild(Team('Denver Broncos',       'DEN'))
    afcw.addChild(Team('Kansas City Chiefs',   'KC'))
    afcw.addChild(Team('Oakland Raiders',      'OAK'))
    afcw.addChild(Team('San Diego Chargers',   'SD'))

    nfce = Division('East')
    nfcc = Division('Central')
    nfcs = Division('South')
    nfcw = Division('West')

    nfc.addChild(nfce)
    nfc.addChild(nfcc)
    nfc.addChild(nfcs)
    nfc.addChild(nfcw)

    nfce.addChild(Team('Dallas Cowboys',       'DAL'))
    nfce.addChild(Team('New York Giants',      'NYG'))
    nfce.addChild(Team('Philadelphia Eagles',  'PHI'))
    nfce.addChild(Team('Washington Redskins',  'WAS'))

    nfcc.addChild(Team('Chicago Bears',        'CHI'))
    nfcc.addChild(Team('Detroit Lions',        'DET'))
    nfcc.addChild(Team('Green Bay Packers',    'GB'))
    nfcc.addChild(Team('Minnesota Vikings',    'MIN'))
    
    nfcs.addChild(Team('Atlanta Falcons',      'ATL'))
    nfcs.addChild(Team('Carolina Panthers',    'CAR'))
    nfcs.addChild(Team('New Orleans Saints',   'NO'))
    nfcs.addChild(Team('Tampa Bay Buccaneers', 'TB'))

    nfcw.addChild(Team('Arizona Cardnials',    'ARI'))
    nfcw.addChild(Team('San Francisco 49ers',  'SF'))
    nfcw.addChild(Team('Seattle Seahawks',     'SEA'))
    nfcw.addChild(Team('St. Louis Rams',       'STL'))

    return nfl


def loadBeatPower(filename, nfl):

    try:
        bpReader = csv.reader(open(filename), 
                              delimiter=',', quotechar='|')
        for row in bpReader:
            team = nfl.getTeam(row[0])
            if team is None:
                print 'Cannot find team ' + row[0]
            else:
                team.setBeatPower(float(row[1]))
    except:
        print "Error parsing beatpower data"
        return False

    return True


def breakTie2(A, B):
    print "Tie between %3s and %3s" % (A.getAbbr(), B.getAbbr())
    print "%3s %3.1f v %3.1f %3s" % (A.getAbbr(), A.getWinPct(B),
                                     B.getWinPct(A), B.getAbbr())
    
    # Test 01: Head-to-Head
    if A.getWinPct(B) > B.getWinPct(A):
        return [A, B]
    elif B.getWinPct(A) > A.getWinPct(B):
        return [B, A]

    return [A, B]

    

def breakTie(teams):
    if len(teams) == 2:
        return breakTie2(teams[0], teams[1])
    return teams.sort(key=Team.getAbbr)


def rankTeams(div):
    ranked = []
    teams  = div.getTeams()
    
    # basic sort by win pct
    teams.sort(key=Team.getWinPct, reverse=True)

    nextTeam = []
    while len(teams) > 0:
        nextTeam.append(teams.pop(0))

        while len(teams) > 0 and teams[0].getWinPct() == nextTeam[0].getWinPct():
            nextTeam.append(teams.pop(0))
            
        if len(nextTeam) > 1:
            nextTeam = breakTie(nextTeam)
            
        ranked.extend(nextTeam)
        nextTeam = []
            
    return ranked


#
# Drive down to division level and rank teams
#
def genRegularSeasonStandings(nfl):
    confs = nfl.getChildren()
    for cname in confs:
        conf = confs[cname]
        print conf.getName()
        divs = conf.getChildren()
        for dname in divs:
            div = divs[dname]
            print div.getName()
            ranked = rankTeams(div)
            for team in ranked:
                print team.getName()


if __name__ == "__main__":
    usage   = "usage: %prog [options] beatpower.csv schedule.csv"
    version = "%prog 0.10"

    parser = OptionParser(usage=usage, version=version)
    parser.add_option("-s", "--sigma", dest="sigma", type="float",
                      help="float value to use for variance",
                      metavar="SIGMA", default=10.0)
    parser.add_option('-d', '--dbg-out', dest="dbgfile", 
                      type="string", default="",
                      help="filename dump league (blank to suppress)",
                      metavar="FILE")
    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        sys.exit(1)

    # Get league structure
    nfl = setupNFL()
    
    if not (loadBeatPower(args[0], nfl) and
            nfl.loadCsvSchedule(args[1])):
        sys.exit(1)


    nfl.simulateRegularSeason()

    genRegularSeasonStandings(nfl)

    # Dump structure (debugging)
    # nfl.listChildren()
    
    if options.dbgfile != "":
        try:
            with open(options.dbgfile, 'w') as out:
                pickle.dump(nfl, out)
        except:
            print "Error pickling NFL"
            
    
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
    
    sys.exit(0)
    
