#!/usr/bin/python

import sys
#from optparse import OptionParser

from league import League
from league import Conference

if __name__ == "__main__":
    nfl = League('NFL')
    
    afc = Conference('AFC')
    nfc = Conference('NFC')
    
    nfl.addChild(afc)
    nfl.addChild(nfc)
    nfl.listChildren()
    
    sys.exit(0)
    
