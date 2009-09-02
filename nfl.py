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
    
    coin = random.randint(0, len(teams))
    logging.info(teams[coin].getAbbr() + " by coin flip")
    tmp         = teams[0]
    teams[0]    = teams[coin]
    teams[coin] = tmp
    teams[1:]   = breakDivTie(teams[1:])

    return teams

def breakConfTie(teams):
    return teams

class NFL:
    def __init__(self):
        logging.debug("In NFL constructor")
        self.__setup()

    def __setup(self):
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

    

    def __genRegularSeasonStandings(self):
        confs = self.__league.getChildren()
        for cname in confs:
            conf = confs[cname]
            leaders = []
            logging.info(conf.getName())
            divs = conf.getChildren()
            for dname in divs:
                div = divs[dname]
                logging.info(div.getName())
                ranked = rankTeams(div.getTeams())
                for team in ranked:
                    logging.info(team.getName())
                leaders.append(ranked.pop(0))
            slotted = rankTeams(leaders, div=False)
            for i in range(0,len(slotted)):
                print ("%d: %s") % (i+1, slotted[i].getName())
