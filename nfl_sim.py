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

    nfce = Division('East')
    nfcc = Division('Central')
    nfcn = Division('North')
    nfcw = Division('West')

    nfc.addChild(nfce)
    nfc.addChild(nfcc)
    nfc.addChild(nfcn)
    nfc.addChild(nfcw)

    nfce.addChild(Team('Dallas Cowboys',       'DAL'))
    nfce.addChild(Team('New York Giants',      'NYG'))
    nfce.addChild(Team('Philladelphia Eagles', 'PHI'))
    nfce.addChild(Team('Washington Redskins',  'WAS'))

    teams = nfce.getChildren()
    for team in teams:
        team.getName()

    nfl.listChildren()

    sys.exit(0)
    
