#!/usr/bin/python

import logging
import csv

from league import League
from league import Conference
from league import Division
from league import Team



def rankTeams(div):
    ranked = []
    teams  = div.getTeams()
    
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
            nextTeam = breakTie(nextTeam)
            
        ranked.extend(nextTeam)
        nextTeam = []
            
    return ranked

def breakTie(teams):
    if len(teams) > 2:
        logging.critical(" ########### Three- (or more) way ties not implemented ########### ")
        return teams
    
    teams[0].setWinPctOpponents(teams)
    teams[1].setWinPctOpponents(teams)
    if teams[0].getWinPct() > teams[1].getWinPct():
        logging.info(teams[0].getAbbr() + " better h2h")
        return teams
    elif teams[0].getWinPct() < teams[1].getWinPct():
        logging.info(teams[1].getAbbr() + " better h2h (r)")
        teams.reverse()
        return teams

    div = teams[0].getParent()
    divTeams = div.getTeams()

    teams[0].setWinPctOpponents(divTeams)
    teams[1].setWinPctOpponents(divTeams)
    if teams[0].getWinPct() > teams[1].getWinPct():
        logging.info(teams[0].getAbbr() + " better in div")
        return teams
    elif teams[0].getWinPct() < teams[1].getWinPct():
        logging.info(teams[1].getAbbr() + " better in div (r)")
        teams.reverse()
        return teams
    
    commonOpps = set(teams[0].getOpponents())
    commonOpps.intersection(set(teams[1].getOpponents()))
    
    teams[0].setWinPctOpponents(commonOpps)
    teams[1].setWinPctOpponents(commonOpps)
    if teams[0].getWinPct() > teams[1].getWinPct():
        logging.info(teams[0].getAbbr() + " better in common")
        return teams
    elif teams[0].getWinPct() < teams[1].getWinPct():
        logging.info(teams[1].getAbbr() + " better in common (r)")
        teams.reverse()
        return teams
    
    conf = div.getParent()
    confTeams = conf.getTeams()
    
    teams[0].setWinPctOpponents(confTeams)
    teams[1].setWinPctOpponents(confTeams)
    if teams[0].getWinPct() > teams[1].getWinPct():
        logging.info(teams[0].getAbbr() + " better in conf")
        return teams
    elif teams[0].getWinPct() < teams[1].getWinPct():
        logging.info(teams[1].getAbbr() + " better in conf (r)")
        teams.reverse()
        return teams
    
    logging.critical("Still tied after conference games")

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
    

    def simulateSeason(self):
        self.__league.simulateRegularSeason()
        self.__genRegularSeasonStandings()

    

    def __genRegularSeasonStandings(self):
        confs = self.__league.getChildren()
        for cname in confs:
            conf = confs[cname]
            logging.info(conf.getName())
            divs = conf.getChildren()
            for dname in divs:
                div = divs[dname]
                logging.info(div.getName())
                ranked = rankTeams(div)
                for team in ranked:
                    logging.info(team.getName())

