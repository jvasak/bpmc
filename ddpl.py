#!/usr/bin/python

import logging
import csv
import random

from teamgroup  import TeamGroup
from league     import League
from conference import Conference
from division   import Division
from team       import Team


class DDPL(League):
    def __init__(self):
        logging.debug("In DDPL constructor")

        self.__standings  = dict()
        self.__postseason = dict()

        League.__init__(self, 'DDPL')

        pc = Conference('Piler')
        afce.setColors('black', 'blue')

        fc = Conference('Fornicator')
        afce.setColors('black', 'red')

        self.addChild(pc)
        self.addChild(fc)

        pc.addChild(Team('Beaners',           'BE'))
        pc.addChild(Team('Brains',            'BR'))
        pc.addChild(Team('CM All-Stars',      'CM'))
        pc.addChild(Team('Cuban Prostitutes', 'CP'))
        pc.addChild(Team('Hairy Palms',       'HP'))
        pc.addChild(Team('Umbrellas',         'UM'))

        fc.addChild(Team('Charlies',          'CH'))
        fc.addChild(Team('Dictators',         'DI'))
        fc.addChild(Team('La Players',        'LP'))
        fc.addChild(Team('Raw Doggers',       'RD'))
        fc.addChild(Team('Rusty Trombones',   'RT'))
        fc.addChild(Team('Sausage Milkers',   'SM'))


    def weeksInRegularSeason(self):
        return 13


    def onResetSeason(self):
        self.__postseason.clear()
        self.__standings.clear()


    def simulatePostSeason(self):
        self.__genRegularSeasonStandings()
        self.__simulatePostSeason()


    def __genRegularSeasonStandings(self):
        confs = self.getChildren()
        for cname in confs:
            conf = confs[cname]

            logging.info(conf.getName())
            self.__standings[cname] = dict()

            ranked = rankTeams(conf.getTeams())

            self.__standings[cname] = ranked

            for i in range(len(ranked)):
                logging.info(ranked[i].getName())
                ranked[i].tallyDivisionPlace(i)


    def __simulatePostSeason(self):
        """Match up postseason opponents and simulate all games
           through the Super Bowl"""
        sbTeams = []
        for conf in self.__postseason.keys():
            teams = self.__postseason[conf]

            res = self.simulateGame(teams[1], teams[2], ties=False)
            if res > 0:
                winner = teams[1]
            else:
                winner = teams[2]

            res = self.simulateGame(teams[0], winner, ties=False)
            if res > 0:
                sbTeams.append(teams[0])
            else:
                sbTeams.append(winner)


        sbTeams[0].tallyConfChamp()
        sbTeams[1].tallyConfChamp()
        res = self.simulateGame(sbTeams[0], sbTeams[1], ties=False)
        if res > 0:
            logging.info("Donkey Bowl champ: " + sbTeams[0].getAbbr())
            sbTeams[0].tallySuperBowl()
        else:
            logging.info("Donkey Bowl champ: " + sbTeams[1].getAbbr())
            sbTeams[1].tallySuperBowl()


    def printStats(self):
        confs = self.getChildren()
        for cname in confs:
            print cname
            conf = confs[cname]
            
            teams = conf.getTeams()
            teams.sort(key=Team.getAvgDivPlace)

            for team in teams:
                print ("    %-3s (%5.1f)  %4.2f   %6.4f   %6.4f   %6.4f") % (team.getAbbr(),
                                                                             team.getBeatPower(),
                                                                             team.getAvgDivPlace(),
                                                                             team.getPostseasonPct(),
                                                                             team.getConfChampPct(),
                                                                             team.getSuperBowlPct())


######################################################
#
#
#
#   Helper functions for sorting/ranking teams
#
#
#
#######################################################

def rankTeams(teams):
    ranked = []

    # basic sort by win pct
    for team in teams:
        team.resetWinPctOpponents()
    teams.sort(key=Team.getWinPct, reverse=True)

    nextTeam = []
    while len(teams) > 0:
        nextTeam.append(teams.pop(0))

        while len(teams) > 0 and teams[0].getWinPct() == nextTeam[0].getWinPct():
            nextTeam.append(teams.pop(0))

        if len(nextTeam) > 1:
            nextTeam = breakConfTie(nextTeam)

        ranked.extend(nextTeam)
        nextTeam = []

    return ranked


def tieBreakStep(teams, opps, callback, msg):
    logging.debug("Tie break between " + str(len(teams)) + " using " + msg)

    for team in teams:
        team.setWinPctOpponents(opps)
    teams.sort(key=Team.getWinPct, reverse=True)

    brkIdx = -1
    wp = teams[0].getWinPct()
    for i in range(1, len(teams)):
        if teams[i].getWinPct() == wp:
            continue
        else:
            logging.debug("Break off top " + str(i) + " teams using " + msg)
            brkIdx = i
            break

    if brkIdx == -1:
        return (False, teams)

    elif brkIdx == 1:
        if not callback is None:
            teams[1:] = callback(teams[1:])
        return (True, teams)

    if not callback is None:
        teams[:brkIdx] = callback(teams[:brkIdx])
        teams[brkIdx:] = callback(teams[brkIdx:])
        return (True, teams)
    else:
        return (False, teams)



def breakConfTie(teams):
    if len(teams) == 1:
        return teams

    logging.debug("breakConfTie")

    if len(teams) >= 3:
        # This is a special test for a sweep (good or bad), so
        #  don't set the callback function.  We'll do it ourself
        (finished, teams) = tieBreakStep(teams, teams, None, "h2h")
        if teams[0].getWinPct() == 1.0:
            logging.debug(teams[0].getAbbr() + " swept others")
            teams[1:] = breakConfTie(teams[1:])
            return teams
        elif teams[-1].getWinPct() == 0.0:
            logging.debug(teams[-1].getAbbr() + " got swept")
            teams[:-1] = breakConfTie(teams[:-1])
            return teams

    else:
        (finished, teams) = tieBreakStep(teams, teams, breakDivTie, "h2h")
        if finished:
            return teams

    conf = teams[0].getParent()
    confTeams = conf.getTeams()
    (finished, teams) = tieBreakStep(teams, confTeams, breakConfTie, "conf")

    if finished:
        return teams

    coin = random.randint(0, len(teams)-1)
    logging.debug(teams[coin].getAbbr() + " by coin flip")
    tmp         = teams[0]
    teams[0]    = teams[coin]
    teams[coin] = tmp
    teams[1:]   = breakConfTie(teams[1:])

    return teams


