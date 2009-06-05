#!/usr/bin/python

import sys
from optparse import OptionParser

from league import League
from league import Conference

if __name__ == "__main__":
    nfl = League()
    
    afc = Conference('AFC')
    nfc = Conference('NFC')
    
    nfl.addConf(afc)
    nfl.addConf(nfc)
    nfl.listConfs()
    
    sys.exit(0)
    
