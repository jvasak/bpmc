#/usr/bin/python

class TeamGroup:
    """Abstract base class for organizing teams"""
    __child  = []
    __parent = None
    __name   = ''

    def __init__(self, name):
        self.__name = name

    def addChild(self, child):
        self.__child.append(child)
        child.setParent(self)

    def setParent(self, parent):
        self.__parent = parent

    def listChildren(self):
        print self.__name
        for child in self.__child:
            print "-> %s" % (child.getName())
        print

    def getName(self):
        return self.__name


class League(TeamGroup):
    """Simple class not much more than a named list of conferences"""
    
    def __init__(self, name='NFL'):
        TeamGroup.__init__(self, name)
    

class Conference(TeamGroup):
    """Simple class not much more than a named list of divisions"""
    pass

