#/usr/bin/python

import csv
import logging

from random import normalvariate, gauss
from math   import sqrt

from teamgroup import TeamGroup

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

