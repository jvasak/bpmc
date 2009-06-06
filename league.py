#/usr/bin/python

class TeamGroup:
    """Abstract base class for organizing teams"""
    def __init__(self, name):
        self.__name   = name
        self.__parent = None
        self.__child  = []

    def addChild(self, child):
        if child.setParent(self): 
            self.__child.append(child)

    def setParent(self, parent):
        self.__parent = parent
        return 1

    def listChildren(self, pre='', indent='  ', recurse=1):
        print pre + self.getName()
        for child in self.__child:
            if recurse:
                child.listChildren(pre=pre+indent, indent=indent)
            else:
                print pre + indent + child.getName()

    def getTeams(self):
        teams = []
        if self.__child:
            if isinstance(self.__child[0], Team):
                return self.__child;
            else:
                for child in self.__child:
                    teams = teams[:] + child.getTeams()
        return teams
            

    def getChildren(self):
        return self.__child

    def getName(self):
        return self.__name




class League(TeamGroup):
    """Simple class not much more than a named list of conferences"""
    
    def __init__(self, name='NFL'):
        TeamGroup.__init__(self, name)

    def setParent(self, parent):
        return 0
    

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
        return TeamGroup.getName(self) + ' (' + self.__abbr + ')'

