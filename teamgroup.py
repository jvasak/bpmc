import logging

class TeamGroup:
    """Abstract base class for organizing teams"""
    def __init__(self, name):
        self.__name   = name
        self.__parent = None
        self.__child  = dict()
        self.__colors = ('black', 'gray')

    def addChild(self, child):
        if child.setParent(self):
            self.__child[child.getAbbr()] = child

    def setParent(self, parent):
        self.__parent = parent
        return True

    def listChildren(self, pre='', indent='  ', recurse=1):
        print pre + self.getName()
        for child in self.__child:
            if recurse:
                self.__child[child].listChildren(pre=pre+indent, indent=indent)
            else:
                print pre + indent + child.getName()

    def getTeams(self):
        from team import Team

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

    def getParent(self):
        return self.__parent

    def getChildren(self):
        return self.__child

    def getName(self):
        return self.__name

    def getAbbr(self):
        return self.getName()

    def setColors(self, line, fill):
        self.__colors = (line, fill)

    def getColors(self):
        return self.__colors
