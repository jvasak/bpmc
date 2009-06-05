#/usr/bin/python

class TeamGroup:
    """Abstract base class for organizing teams"""
    def __init__(self, name):
        self.__name   = name
        self.__parent = None
        self.__child  = []

    def addChild(self, child):
        self.__child.append(child)
        child.setParent(self)

    def setParent(self, parent):
        self.__parent = parent

    def listChildren(self, pre='', indent='  ', recurse=1):
        print pre + self.__name
        for child in self.__child:
            if recurse:
                child.listChildren(pre=pre+indent, indent=indent)
            else:
                print pre + indent + child.getName()

    def getChildren(self):
        return self.__child

    def getName(self):
        return self.__name




class League(TeamGroup):
    """Simple class not much more than a named list of conferences"""
    
    def __init__(self, name='NFL'):
        TeamGroup.__init__(self, name)


    

class Conference(TeamGroup):
    """Simple class not much more than a named list of divisions"""
    pass



class Division(TeamGroup):
    pass



class Team(TeamGroup):
    """Group with no children is a team"""

    def __init__(self, name, abbr):
        TeamGroup.__init__(self, name);
        self.__abbr = abbr;

    def getName(self):
        print 'YIKES'
        return TeamGroup.getName(self) + ' (' + self.__abbr + ')'

