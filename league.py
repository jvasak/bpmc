#/usr/bin/python

class League:
    """Simple class not much more than a named list of conferences"""
    confs = []
    name  = ''
    
    def __init__(self, name=None):
        if name is None:
            self.name = 'NFL'
        else:
            self.name = name
    
    def addConf(self, conf):
        self.confs.append(conf)
        conf.setLeague(self)
        
    def listConfs(self):
        print "%s Conferences:" % (self.name)
        for conf in self.confs:
            print "\t%s" % (conf.name)
        print

class Conference:
    """Simple class not much more than a named list of divisions"""
    divs   = []
    name   = ''
    parent = ''
    
    def __init__(self, name=None):
        if name is None:
            print "Conferences cannot be unamed!"
            self.name = "DUMMY"
        else:
            self.name = name
    
    def setLeague(self, league):
        self.parent = league

