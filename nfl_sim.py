#!/usr/bin/python

import sys
#from optparse import OptionParser

from league import League
from league import Conference
from league import Division
from league import Team

if __name__ == "__main__":
    nfl = League()
    
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
    afcn.addChild(Team('Cincinnatti Bengals',  'CIN'))
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
    nfce.addChild(Team('Philladelphia Eagles', 'PHI'))
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

    nfl.listChildren()
    
    teams = nfc.getTeams()
    for team in teams:
        print team.getName()

    sys.exit(0)
    
