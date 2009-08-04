#/usr/bin/python

import string
import csv
from random import normalvariate
from math import sqrt

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
        return True

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
        self.__sched = [[] for i in range(21)]

    def setParent(self, parent):
        return False
    
    def loadCsvSchedule(self, csvfile):
        try:
            skdReader = csv.reader(open(csvfile), 
                                   delimiter=',', quotechar='|')
            
            (wkIdx, awIdx, hmIdx) = (None, None, None)
            hdr = skdReader.next()
            for i in range(0, len(hdr)):
                if   hdr[i].lower() == 'week':
                    wkIdx = i
                elif hdr[i].lower() == 'away':
                    awIdx = i
                elif hdr[i].lower() == 'home':
                    hmIdx = i
        
            for row in skdReader:
                self.__sched[int(row[wkIdx])-1].append((row[hmIdx],row[awIdx]))
                
        except:
            print "Schedule parsing error"
            return False

        return True

    def simulateRegularSeason(self):
        for week in range(17):
            print "Simulating %2d games for week %2d" % (len(self.__sched[week]),
                                                          week)
            for game in self.__sched[week]:
                home = self.getTeam(game[0])
                away = self.getTeam(game[1])
                confidence = home.getBeatPower() - away.getBeatPower()
                res = normalvariate(confidence, 50)
                if res >= 0:
                    #print "%3s d. %3s" % (home.getAbbr(), away.getAbbr())
                    home.addWin(away)
                    away.addLoss(home)
                elif res == 0:
                    home.addTie(away)
                    away.addTie(home)
                else:
                    #print "%3s d. %3s" % (away.getAbbr(), home.getAbbr())
                    home.addLoss(away)
                    away.addWin(home)
            



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
        self.__wins      = []
        self.__ties      = []
        self.__losses    = []

    def getAbbr(self):
        return self.__abbr

    def getName(self):
        f = string.Formatter()
        return f.format("%5s (%5.1f) %3d %3d" % (self.__abbr, self.__beatpower,
                                                 len(self.__wins),
                                                 len(self.__losses)))
    
    def getBeatPower(self):
        return self.__beatpower

    def setBeatPower(self, power):
        self.__beatpower = power

    def addWin(self, team):
        self.__wins.append(team)

    def addTie(self, team):
        self__ties.append(team)

    def addLoss(self, team):
        self.__losses.append(team)

    def getRecord(self):
        return (len(self.__wins), len(self.__losses))

    def getOpponents(self):
        opps = self.__wins
        opps.extend(self.__losses)
        opps.extend(self.__ties)
        return opps
    
    def getWinPct(self, opps=None):
        wins, ties, loss = 0, 0, 0
        if opps is None:
            wins = len(self.__wins)
            ties = len(self.__ties)
            loss = len(self.__losses)
        elif isinstance(opps,Team):
            wins = self.__wins.count(opps)
            ties = self.__ties.count(opps)
            loss = self.__losses.count(opps)
        else:
            for opp in opps:
                wins += self.__wins.count(opp)
                ties += self.__ties.count(opp)
                loss += self.__losses.count(opp)
        return (wins + 0.5*ties)/float(wins + ties + loss)
