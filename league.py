#/usr/bin/python

import csv
import logging
from array import array
from random import normalvariate, gauss
from math import sqrt

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


class League(TeamGroup):
    """Simple class not much more than a named list of conferences"""

    def __init__(self, name='NFL'):
        TeamGroup.__init__(self, name)
        self.__sched = [[] for i in range(21)]

    def setParent(self, parent):
        return False

    def loadCsvSchedule(self, csvfile):
        logging.info("Loading schedule from: " + csvfile)
        self.__partial = False
        try:
            skdReader = csv.reader(open(csvfile),
                                   delimiter=',', quotechar='|')

            (wkIdx, awIdx, hmIdx, awScrIdx, hmScrIdx) = (None, None, None, None, None)
            hdr = skdReader.next()
            for i in range(0, len(hdr)):
                if   hdr[i].lower() == 'week':
                    wkIdx = i
                    logging.debug("Week info in column " + str(i))
                elif hdr[i].lower() == 'away':
                    awIdx = i
                    logging.debug("Away info in column " + str(i))
                elif hdr[i].lower() == 'home':
                    hmIdx = i
                    logging.debug("Home info in column " + str(i))
                elif hdr[i].lower() == 'awayscore':
                    awScrIdx = i
                    logging.debug("Away score in column " + str(i))
                elif hdr[i].lower() == 'homescore':
                    hmScrIdx = i
                    logging.debug("Home score in column " + str(i))

            for row in skdReader:
                logging.debug("Wk " + row[wkIdx] + ": " + row[awIdx] + " " + row[awScrIdx] +
                              " @ " + row[hmScrIdx] + " " + row[hmIdx]);
                if row[awScrIdx] == '--' or row[awScrIdx] == '--':
                    self.__sched[int(row[wkIdx])-1].append((row[hmIdx],row[awIdx]))
                else:
                    self.__partial = True
                    home = self.getTeam(row[hmIdx])
                    away = self.getTeam(row[awIdx])
                    if int(row[hmScrIdx]) > int(row[awScrIdx]):
                        home.addWin(away)
                        away.addLoss(home)
                    elif int(row[awScrIdx]) > int(row[hmScrIdx]):
                        away.addWin(home)
                        home.addLoss(away)
                    else:
                        home.addTie(away)
                        away.addTie(home)

        except:
            logging.error("Schedule parsing error")
            return False

        if self.__partial:
            teams = self.getTeams()
            for team in teams:
                team.saveSnapshot()

            # Build me a graph!
            from beatpath import Beatpath
            bp = Beatpath(self)
            bp.buildGraph()
            bp.genBeatScores()

        return True



    def isPartialSeason(self):
        return self.__partial


    def simulateGame(self, home, away, ties=True):
        confidence = home.getBeatPower() - away.getBeatPower()
        rels = home.getRelationships() + away.getRelationships()
        res  = gauss(confidence, 100-rels)
        while res == 0 and not ties:
            res = gauss(confidence, 100-rels)
        return res


    def simulateRegularSeason(self):
        for week in range(17):
            logging.debug("Simulating " + str(len(self.__sched[week])) +
                          " games for week " + str(week))

            for game in self.__sched[week]:
                home = self.getTeam(game[0])
                away = self.getTeam(game[1])
                res  = self.simulateGame(home, away)
                if res > 0:
                    logging.debug(home.getAbbr() + " def. " + away.getAbbr())
                    home.addWin(away)
                    away.addLoss(home)
                elif res == 0:
                    logging.debug(home.getAbbr() + " TIE " + away.getAbbr())
                    home.addTie(away)
                    away.addTie(home)
                else:
                    logging.debug(away.getAbbr() + " def. " + home.getAbbr())
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
        self.__abbr          = abbr;
        self.__beatpower     = 0.0
        self.__relationships = 0
        self.__wins   = []
        self.__ties   = []
        self.__losses = []
        self.__winSnap  = []
        self.__tieSnap  = []
        self.__lossSnap = []
        self.__resetStats()

    def getAbbr(self):
        return self.__abbr

    def getName(self):
        return "%5s (%5.1f) %3d %3d" % (self.__abbr, self.__beatpower,
                                        len(self.__wins),
                                        len(self.__losses))

    def getBeatPower(self):
        return self.__beatpower

    def getRelationships(self):
        return self.__relationships

    def setBeatPower(self, power, rels):
        self.__beatpower     = power
        self.__relationships = rels

    def addWin(self, team):
        self.__wins.append(team)

    def delWin(self, team):
        self.__wins.remove(team)

    def getWins(self):
        return self.__wins

    def addTie(self, team):
        self.__ties.append(team)

    def delTie(self, team):
        self.__ties.remove(team)

    def getTies(self):
        return self.__ties

    def addLoss(self, team):
        self.__losses.append(team)

    def delLoss(self, team):
        self.__losses.remove(team)

    def getLosses(self):
        return self.__losses

    def getRecord(self):
        return (len(self.__wins), len(self.__losses))

    def getOpponents(self):
        opps = []
        opps.extend(self.__wins)
        opps.extend(self.__losses)
        opps.extend(self.__ties)
        return opps

    def saveSnapshot(self):
        logging.debug("Saving snaphot for " + self.getAbbr())
        if len(self.__wins):
            self.__winSnap.extend(self.__wins)
        if len(self.__ties):
            self.__tieSnap.extend(self.__ties)
        if len(self.__losses):
            self.__lossSnap.extend(self.__losses)

    def resetGames(self):
        self.__wins      = []
        if len(self.__winSnap):
            self.__wins.extend(self.__winSnap)

        self.__ties      = []
        if len(self.__tieSnap):
            self.__ties.extend(self.__tieSnap)

        self.__losses    = []
        if len(self.__lossSnap):
            self.__losses.extend(self.__lossSnap)

        self.__wpOpps    = []


    def playedEach(self, opps):
        """Returns true if team had played each of the opponent
           in the list.  Presence of the tested team in list will
           be ignored and not cause failure"""
        logging.info("Team.playedEach")
        for opp in opps:
            if opp == self:
                logging.debug("Skipping self in opponent list")
                continue
            if opp not in self.getOpponents():
                logging.debug("Didn't play " + opp.getAbbr())
                return False
        return True


    def setWinPctOpponents(self, opps):
        self.resetWinPctOpponents()
        self.__wpOpps.extend(opps)

    def resetWinPctOpponents(self):
        self.__wpOpps = []

    def getWinPct(self):
        opps = self.__wpOpps
        wins, ties, loss = 0, 0, 0
        if len(opps) == 0:
            wins = len(self.__wins)
            ties = len(self.__ties)
            loss = len(self.__losses)
        else:
            for opp in opps:
                wins += self.__wins.count(opp)
                ties += self.__ties.count(opp)
                loss += self.__losses.count(opp)
        if (wins + ties + loss) == 0:
            return -1
        return (wins + 0.5*ties)/float(wins + ties + loss)


    def dumpGames(self):
        print ("%3s: ") % self.getAbbr(),
        for w in self.__wins:
            print ("%3s(W)  ") % w.getAbbr(),
        for l in self.__losses:
            print ("%3s(L)  ") % l.getAbbr(),
        for t in self.__ties:
            print ("%3s(T)  ") % t.getAbbr(),
        print

    #
    # Team stats functions
    #
    def __resetStats(self):
        self.__divStats  = array('I', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.__wcStats   = 0
        self.__confChamp = 0
        self.__sbWins    = 0

    def tallyDivisionPlace(self, rank):
        self.__divStats[rank] += 1

    def getAvgDivPlace(self):
        num = 0.0
        for i in range(len(self.__divStats)):
            num += (i+1)*self.__divStats[i]
        return num / float(sum(self.__divStats))

    def tallyWildCard(self):
        self.__wcStats += 1

    def getPostseasonPct(self):
        psApps = self.__divStats[0] + self.__wcStats
        runs   = sum(self.__divStats)
        return float(psApps) / float(runs)

    def tallyConfChamp(self):
        self.__confChamp += 1

    def getConfChampPct(self):
        return float(self.__confChamp) / float(sum(self.__divStats))

    def tallySuperBowl(self):
        self.__sbWins += 1

    def getSuperBowlPct(self):
        return float(self.__sbWins) / float(sum(self.__divStats))
