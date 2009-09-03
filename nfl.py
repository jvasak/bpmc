#!/usr/bin/python

import logging
import csv
import random

from league import League
from league import Conference
from league import Division
from league import Team


def rankTeams(teams, div=True):
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
            if div:
                nextTeam = breakDivTie(nextTeam)
            else:
                nextTeam = breakConfTie(nextTeam)

        ranked.extend(nextTeam)
        nextTeam = []

    return ranked


def tieBreakStep(teams, opps, callback, msg):
    logging.info("Tie break between " + str(len(teams)) + " using " + msg)

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
        return (False, teams[:brkIdx])


def breakDivTie(teams):
    if len(teams) == 1:
        return teams

    (finished, teams) = tieBreakStep(teams, teams, breakDivTie, "h2h")

    if finished:
        return teams

    div = teams[0].getParent()
    divTeams = div.getTeams()
    (finished, teams) = tieBreakStep(teams, divTeams, breakDivTie, "div")

    if finished:
        return teams

    commonOpps = set(teams[0].getOpponents())
    commonOpps.intersection(set(teams[1].getOpponents()))
    (finished, teams) = tieBreakStep(teams, commonOpps, breakDivTie, "common")

    if finished:
        return teams

    conf = div.getParent()
    confTeams = conf.getTeams()
    (finished, teams) = tieBreakStep(teams, confTeams, breakDivTie, "conf")

    if finished:
        return teams

    coin = random.randint(0, len(teams)-1)
    logging.info(teams[coin].getAbbr() + " by coin flip")
    tmp         = teams[0]
    teams[0]    = teams[coin]
    teams[coin] = tmp
    teams[1:]   = breakDivTie(teams[1:])

    return teams


def breakConfTie(teams):
    if len(teams) == 1:
        return teams

    logging.debug("breakConfTie")

    if len(teams) >= 3:
        # Check if they've all played each other
        for team in teams:
            if not team.playedEach(teams):
                break
        else:
            # This is a special test for a sweep (good or bad), so
            #  don't set the callback function.  We'll do it ourself
            (finished, teams) = tieBreakStep(teams, teams, None, "h2h")
            if teams[0].getWinPct() == 1.0:
                logging.info(teams[0].getAbbr() + " swept others")
                teams[1:] = breakConfTie(teams[1:])
                return teams
            elif teams[-1].getWinPct() == 0.0:
                logging.debug(teams[-1].getAbbr() + " got swept")
                teams[:-1] = breakConfTie(teams[:-1])
                return teams

        conf = teams[0].getParent().getParent()
        confTeams = conf.getTeams()
        (finished, teams) = tieBreakStep(teams, confTeams, breakConfTie, "conf")

        if finished:
            return teams


        commonOpps = set(teams[0].getOpponents())
        for i in range(1,len(teams)):
            commonOpps.intersection(set(teams[i].getOpponents()))
        if len(commonOpps) >= 4:
            (finished, teams) = tieBreakStep(teams, commonOpps, breakConfTie, "common")

            if finished:
                return teams
        else:
            logging.debug("Not enough common opponents to break tie")


        coin = random.randint(0, len(teams)-1)
        logging.info(teams[coin].getAbbr() + " by coin flip")
        tmp         = teams[0]
        teams[0]    = teams[coin]
        teams[coin] = tmp
        teams[1:]   = breakConfTie(teams[1:])

        return teams

    # Now down to just 2 teams
    if teams[0].playedEach(teams):
        (finished, teams) = tieBreakStep(teams, teams, breakDivTie, "h2h")
        if finished:
            return teams

    conf = teams[0].getParent().getParent()
    confTeams = conf.getTeams()
    (finished, teams) = tieBreakStep(teams, confTeams, breakConfTie, "conf")
    if finished:
        return teams

    commonOpps = set(teams[0].getOpponents())
    commonOpps.intersection(set(teams[1].getOpponents()))
    if len(commonOpps) >= 4:
        (finished, teams) = tieBreakStep(teams, commonOpps, breakConfTie, "common")
        if finished:
            return teams
    else:
        logging.debug("Not enough common opponents to break tie")

    coin = random.randint(0, 1)
    logging.info(teams[coin].getAbbr() + " by coin flip")
    if coin:
        teams.reverse()

    return teams


class NFL:
    def __init__(self):
        logging.debug("In NFL constructor")
        self.__setup()

    def __setup(self):
        self.__standings  = dict()
        self.__postseason = dict()
        self.__league = League('NFL')

        afc = Conference('AFC')
        nfc = Conference('NFC')

        self.__league.addChild(afc)
        self.__league.addChild(nfc)

        afce = Division('East')
        afcn = Division('North')
        afcs = Division('South')
        afcw = Division('West')

        afc.addChild(afce)
        afc.addChild(afcn)
        afc.addChild(afcs)
        afc.addChild(afcw)

        afce.addChild(Team('Buffalo Bills',        'BUF'))
        afce.addChild(Team('Miami Dolphins',       'MIA'))
        afce.addChild(Team('New England Patriots', 'NE'))
        afce.addChild(Team('New York Jets',        'NYJ'))

        afcn.addChild(Team('Baltimore Ravens',     'BAL'))
        afcn.addChild(Team('Cincinnati Bengals',   'CIN'))
        afcn.addChild(Team('Cleveland Browns',     'CLE'))
        afcn.addChild(Team('Pittsburgh Steelers',  'PIT'))

        afcs.addChild(Team('Houston Texans',       'HOU'))
        afcs.addChild(Team('Indianapolis Colts',   'IND'))
        afcs.addChild(Team('Jacksonville Jaguars', 'JAC'))
        afcs.addChild(Team('Tennessee Titans',     'TEN'))

        afcw.addChild(Team('Denver Broncos',       'DEN'))
        afcw.addChild(Team('Kansas City Chiefs',   'KC'))
        afcw.addChild(Team('Oakland Raiders',      'OAK'))
        afcw.addChild(Team('San Diego Chargers',   'SD'))

        nfce = Division('East')
        nfcc = Division('Central')
        nfcs = Division('South')
        nfcw = Division('West')

        nfc.addChild(nfce)
        nfc.addChild(nfcc)
        nfc.addChild(nfcs)
        nfc.addChild(nfcw)

        nfce.addChild(Team('Dallas Cowboys',       'DAL'))
        nfce.addChild(Team('New York Giants',      'NYG'))
        nfce.addChild(Team('Philadelphia Eagles',  'PHI'))
        nfce.addChild(Team('Washington Redskins',  'WAS'))

        nfcc.addChild(Team('Chicago Bears',        'CHI'))
        nfcc.addChild(Team('Detroit Lions',        'DET'))
        nfcc.addChild(Team('Green Bay Packers',    'GB'))
        nfcc.addChild(Team('Minnesota Vikings',    'MIN'))

        nfcs.addChild(Team('Atlanta Falcons',      'ATL'))
        nfcs.addChild(Team('Carolina Panthers',    'CAR'))
        nfcs.addChild(Team('New Orleans Saints',   'NO'))
        nfcs.addChild(Team('Tampa Bay Buccaneers', 'TB'))

        nfcw.addChild(Team('Arizona Cardnials',    'ARI'))
        nfcw.addChild(Team('San Francisco 49ers',  'SF'))
        nfcw.addChild(Team('Seattle Seahawks',     'SEA'))
        nfcw.addChild(Team('St. Louis Rams',       'STL'))


    def loadSeasonInfo(self, power, sched):
        if not (self.__loadBeatPower(power) and
                self.__league.loadCsvSchedule(sched)):
            return False
        return True


    def __loadBeatPower(self, filename):
        logging.info("Loading beatpower from " + filename)
        try:
            bpReader = csv.reader(open(filename),
                                  delimiter=',', quotechar='|')
            for row in bpReader:
                team = self.__league.getTeam(row[0])
                if team is None:
                    print 'Cannot find team ' + row[0]
                else:
                    team.setBeatPower(float(row[1]))
        except:
            print "Error parsing beatpower data"
            return False

        return True



    def simulateSeason(self, sigma):
        self.__league.simulateRegularSeason(sigma)
        self.__genRegularSeasonStandings()
        self.__setWildCard()
        self.__simulatePostSeason(sigma)


    def __genRegularSeasonStandings(self):
        self.__standings.clear()
        confs = self.__league.getChildren()
        for cname in confs:
            conf = confs[cname]

            logging.info(conf.getName())
            self.__standings[cname] = dict()

            divs = conf.getChildren()
            for dname in divs:
                div = divs[dname]
                logging.info(div.getName())
                ranked = rankTeams(div.getTeams())

                self.__standings[cname][dname] = ranked

                for team in ranked:
                    logging.info(team.getName())


    def __setWildCard(self):
        logging.debug("Setting postseason")
        self.__postseason.clear()
        for conf in self.__standings.keys():
            logging.debug("Examining " + conf)
            leaders = []

            # Rank division leaders
            for div in self.__standings[conf].keys():
                leaders.append(self.__standings[conf][div].pop(0))
            self.__postseason[conf] = rankTeams(leaders, False)

            # Now consider all the #2 folks for the first WC slot
            for div in self.__standings[conf].keys():
                leaders.append(self.__standings[conf][div].pop(0))
            leaders = rankTeams(leaders, False)

            wc = leaders.pop(0)
            self.__postseason[conf].append(wc)
            leaders.append(self.__standings[conf][wc.getParent().getAbbr()].pop(0))

            leaders = rankTeams(leaders, False)
            self.__postseason[conf].append(leaders[0])

            for i in range(len(self.__postseason[conf])):
                print ("%d. %s") % (i, self.__postseason[conf][i].getName())



    def __simulatePostSeason(self, sigma):
        """Match up postseason opponents and simulate all games
           through the Super Bowl"""
        sbTeams = []
        for conf in self.__postseason.keys():
            teams = self.__postseason[conf]
            divOpp = [None, None]
            res = self.__league.simulateGame(sigma, teams[2], teams[5], ties=False)
            if res > 0:
                divOpp[1] = teams[2]
            else:
                divOpp[0] = teams[5]

            res = self.__league.simulateGame(sigma, teams[3], teams[4], ties=False)
            if res > 0:
                if divOpp[0] is None:
                    divOpp[0] = teams[3]
                else:
                    divOpp[1] = teams[3]
            else:
                if divOpp[0] is None:
                    divOpp[0] = teams[4]
                else:
                    divOpp[1] = teams[4]

            champ = []
            res = self.__league.simulateGame(sigma, teams[0], divOpp[0], ties=False)
            if res > 0:
                champ.append(teams[0])
            else:
                champ.append(divOpp[0])
            res = self.__league.simulateGame(sigma, teams[1], divOpp[1], ties=False)
            if res > 0:
                champ.append(teams[1])
            else:
                champ.append(divOpp[1])

            res = self.__league.simulateGame(sigma, champ[0], champ[1], ties=False)
            if res > 0:
                sbTeams.append(champ[0])
            else:
                sbTeams.append(champ[1])

        res = self.__league.simulateGame(sigma, sbTeams[0], sbTeams[1], ties=False)
        if res > 0:
            print "Super Bowl champ: " + sbTeams[0].getAbbr()
        else:
            print "Super Bowl champ: " + sbTeams[1].getAbbr()
