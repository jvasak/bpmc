#/usr/bin/python

import string

class TeamGroup:
    """Abstract base class for organizing teams"""
    def __init__(self, name):
        self.__name   = name
        self.__parent = None
        self.__child  = dict()

    def addChild(self, child):
        if child.setParent(self): 
            self.__child[child.getAbbr()] = child

    def setParent(self, parent):
        self.__parent = parent
        return 1

    def listChildren(self, pre='', indent='  ', recurse=1):
        print pre + self.getName()
        for child in self.__child:
            if recurse:
                self.__child[child].listChildren(pre=pre+indent, indent=indent)
            else:
                print pre + indent + child.getName()

    def getTeams(self):
        children = []
        for child in self.__child.values():
            if isinstance(child, Team):
                children.append(child)
            else:
                children.extend(child.getTeams())
        return children

    def getTeam(self, abbr):
        if abbr in self.__child:
            return self.__child[abbr]
        for child in self.__child.values():
            team = child.getTeam(abbr)
            if not team is None:
                return team
        return None
            

    def getChildren(self):
        return self.__child

    def getName(self):
        return self.__name

    def getAbbr(self):
        return self.getName()


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
        self.__abbr      = abbr;
        self.__beatpower = 0.0

    def getAbbr(self):
        return self.__abbr

    def getName(self):
        f = string.Formatter()
        return f.format("%s (%s): %3.1f" % (TeamGroup.getName(self), self.__abbr, self.__beatpower))

    def setBeatPower(self, power):
        self.__beatpower = power

