#/usr/bin/python

import csv
import logging

from random import normalvariate, gauss
from math   import sqrt

from teamgroup import TeamGroup

class League(TeamGroup):

    def __init__(self, name='Default'):
        TeamGroup.__init__(self, name)
        self.__sched = [[] for i in range(21)]

    def setParent(self, parent):
        logger.warn("Attempted to set parent for League.  Ignored")
        return False

    def loadBeatPower(self, filename):
        logging.info("Loading beatpower from " + filename)
        try:
            bpReader = csv.reader(open(filename),
                                  delimiter=',', quotechar='|')
            for row in bpReader:
                team = self.getTeam(row[0])
                if team is None:
                    logging.error('Cannot find team ' + row[0])
                else:
                    team.setBeatPower(float(row[1]), int(row[2]))
        except:
            logging.error("Error parsing beatpower data")
            return False

        return True

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


    def simulateSeason(self):
        teams = self.getTeams()
        for team in teams:
            team.resetGames()
        self.onResetSeason()

        self.simulateRegularSeason()
        self.simulatePostSeason()


    def simulateGame(self, home, away, ties=True):
        delta = home.getBeatPower() - away.getBeatPower()
        rels  = home.getRelationships() + away.getRelationships()
        sigma = 250 - rels * self.relMultiplier()
        res  = gauss(delta, sigma)
        while res == 0 and not ties:
            res = gauss(delta, sigma)
        return res


    def simulateRegularSeason(self):
        for week in range(self.weeksInRegularSeason()):
            logging.debug("Simulating " + str(len(self.__sched[week])) +
                          " games for week " + str(week))

            for game in self.__sched[week]:
                home = self.getTeam(game[0])
                away = self.getTeam(game[1])
                res  = self.simulateGame(home, away, ties=self.allowTies())
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


    #########################
    #
    # Hooks for subclasses

    def onResetSeason(self):
        """ Hook for subclasses to reset any internal state
            before the start of a new iteration.  Can be 
            ignored if not used. """
        pass


    def weeksInRegularSeason(self):
        """ Set the proper number of weeks to consider when
            simulating the regular season """
        return 0


    def relMultiplier(self):
        """
        Return the multiplier for number of relationship to
        scale the sigma value.

        sigma = 250 - total_rels * multiplier
        """
        return 1


    def allowTies(self):
        """ Allows subclasses to determine if regular season
            tie games will be allowed """
        return True


    def simulatePostSeason(self):
        logger.warn("League.simulatePostSeason() should be overridden")
        

    def printStats(self, plots=False):
        logger.warn("League.printStats() should be overridden")

