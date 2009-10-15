import logging

from array  import array

from teamgroup import TeamGroup

class Team(TeamGroup):
    """Group with no children is a team"""

    def __init__(self, name, abbr):
        TeamGroup.__init__(self, name);
        self.__abbr          = abbr;
        self.__beatpower     = [(0.0, 0)]
        self.__edgepower     = [(0, 0)]
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
        return "%5s (%5.1f) %3d %3d" % (self.__abbr, self.__beatpower[-1][0],
                                        len(self.__wins),
                                        len(self.__losses))

    def getBeatPower(self, week=-1):
        try:
            return self.__beatpower[week]
        except IndexError:
            logging.error("No data for %s week %d beatpower" % (self.__abbr, week))
            return (0.0, 0)

    def getEdgePower(self, week=-1):
        try:
            return self.__edgepower[week]
        except IndexError:
            logging.error("No data for %s week %d edgepower" % (self.__abbr, week))
            return (0, 0)

    def setBeatPower(self, pwrRelTuple, week=0):
        if len(self.__beatpower) > week:
            self.__beatpower[week] = pwrRelTuple
        elif len(self.__beatpower) == week:
            self.__beatpower.append(pwrRelTuple)
        else:
            logging.error("Cannot save %s beatpower for week %d. Not enough other data" \
                              % (self.__abbr, week))

    def setEdgePower(self, pwrRelTuple, week=0):
        if len(self.__edgepower) > week:
            self.__edgepower[week] = pwrRelTuple
        elif len(self.__edgepower) == week:
            self.__edgepower.append(pwrRelTuple)
        else:
            logging.error("Cannot save %s edgepower for week %d. Not enough other data" \
                              % (self.__abbr, week))

    def addWin(self, team):
        self.__wins.append(team)

    def getWins(self):
        return self.__wins

    def addTie(self, team):
        self.__ties.append(team)

    def addLoss(self, team):
        self.__losses.append(team)

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
        self.__winSnap.append(self.__wins[:])
        self.__tieSnap.append(self.__ties[:])
        self.__lossSnap.append(self.__losses[:])

    def resetGames(self, week=-1):
        logging.info("Resetting to week %d" % week)
        try:
            self.__wins      = []
            self.__wins.extend(self.__winSnap[week])

            self.__ties      = []
            self.__ties.extend(self.__tieSnap[week])

            self.__losses    = []
            self.__losses.extend(self.__lossSnap[week])

            self.__wpOpps    = []
        except IndexError as e:
            logging.error("%s missing snapshot data: %s" % (self.getAbbr(), str(e)))

    def playedEach(self, opps):
        """Returns true if team had played each of the opponent
           in the list.  Presence of the tested team in list will
           be ignored and not cause failure"""
        logging.debug("Team.playedEach")
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
