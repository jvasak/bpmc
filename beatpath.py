from   pygraphviz import *
from   array      import array
import pygame.image
import pygame.display

import logging
import tempfile

from league import League
from team   import Team

class Beatpath:

    def __init__(self, leag):
        self.__leag  = leag
        self.__gr    = None
        self.__tDict = dict()

    def buildGraph(self, week, display=True):
        if self.__gr is not None:
            logging.error("Graph already exists!")
            return

        gr = AGraph(strict=False)

        gr.graph_attr['size']    = '6,6'
        gr.graph_attr['bgcolor'] = 'gray87'

        gr.node_attr['shape'] = 'box'
        gr.node_attr['style'] = 'filled'

        gr.edge_attr['dir'] = 'forward'
        gr.edge_attr['color'] = 'black'

        teams = self.__leag.getTeams()
        teams.sort(key=Team.getAbbr)

        # First create the nodes, so we can set
        # attibutes
        for team in teams:
            colors = team.getParent().getColors()
            gr.add_node(team.getAbbr())
            n = gr.get_node(team.getAbbr())
            n.attr['name'] = team.getAbbr()
            n.attr['color'] = 'black'
            n.attr['fontcolor'] = colors[0]
            n.attr['fillcolor'] = colors[1]
            #n.attr['label'] = "<TABLE BORDER=\"0\" CELLSPACING=\"0\" CELLPADDING=\"0\"><TR><TD>" + team.getAbbr() + \
            #    "</TD></TR><TR><TD><IMG SRC=\"/home/jvasak/ffstats/logos/" + team.getAbbr() + \
            #    ".png\" /></TD></TR></TABLE>"


        # Now loop over them to process games
        for team in teams:
            wins = team.getWins()
            for beaten in wins:
                gr.add_edge(team.getAbbr(), beaten.getAbbr())

        self.__gr = gr

        # Clean up
        self.__findAndRemoveBeatloops(len(teams))
        self.__genEdgeScores(week)
        self.__findAndRemoveRedundant()
        self.__genBeatScores(week)


        # Output
        logging.debug(self.__gr.string())
        tmppng = tempfile.NamedTemporaryFile(suffix='.png', delete=True)
        self.__gr.draw(tmppng.name, prog="dot")
        logging.info("Wrote graph to " + tmppng.name)
        img  = pygame.image.load(tmppng.name)
        pygame.display.set_mode(img.get_size())
        surf = pygame.display.get_surface()
        surf.blit(img, (0, 0))
        pygame.display.update()



    ####################
    #
    def __findLoop(self, curNode, startNode, depth):
        """ Find loop by recursively checking if current node can get back to start node """
        loopEdges = []

        if (depth <= 0):
            return loopEdges

        for edge in self.__gr.out_edges(nbunch=[curNode]):
            node = edge[1]
            if (node == startNode):
                loopEdges.append(edge)
            else:
                newEdges = self.__findLoop(node, startNode, depth-1)
                if (len(newEdges) > 0):
                    for recursiveEdge in newEdges:
                        loopEdges.append(recursiveEdge)
                    loopEdges.append(edge)

        return loopEdges

    ####################
    #
    def __findAndRemoveBeatloops(self, numTeams):
        """ Loop over all nodes in graph to find loops and remove them """
        self.__loops = dict()
        for node in self.__gr.nodes():
            self.__loops[node] = set()

        for maxDepth in (range(2,numTeams+1)):
            badEdges = set()

            for node in self.__gr.nodes():
                loops = self.__findLoop(node, node, maxDepth)
                for edge in loops:
                    logging.debug(node + ": " + edge[0] + " => " + edge[1])
                    self.__loops[node].add(edge[0])
                    badEdges.add(edge)

            if (len(badEdges) > 0):

                logging.info("Found loops at depth " + str(maxDepth) + ".  Removing")
                self.__printLoops(badEdges, maxDepth)
                for edge in badEdges:
                    self.__gr.delete_edge(edge[0], edge[1])

    ####################
    #
    def __printLoops(self, edgeset, depth):
        import code
        if len(edgeset) == 0:
            return

        edgelist = list(edgeset)
        used = array('B', [0] * len(edgelist))

        while used.count(False):
            prLoops = []
            start = used.index(False)

            prLoops.append([edgelist[start][0], edgelist[start][1]])
            used[start] = True

            for d in range(1, depth):
                loopLen = len(prLoops)
                for i in range(loopLen):
                    lastTeam = prLoops[i][-1]
                    first = True
                    for e in range(len(edgelist)):
                        edge = edgelist[e]
                        if edge[0] == lastTeam:
                            if d == (depth-1) and edge[1] != prLoops[i][0]:
                                continue
                            used[e] = True
                            if first:
                                prLoops[i].append(edge[1])
                                first = False
                            else:
                                #code.interact(local=locals())
                                prLoops.append([v for v in prLoops[i]])
                                prLoops[-1][-1] = edge[1]

            for i in range(len(prLoops)):
                if len(prLoops[i]) == depth+1:
                    logging.info(" => ".join(prLoops[i]))

    ####################
    #
    def __removeOneAway(self, node, start, closest):
        """ Recursively move any redundant links """
        for edge in self.__gr.out_edges([node]):
            if edge[1] in closest:
                closest.remove(edge[1])
                self.__gr.delete_edge(start, edge[1])
            closest = self.__removeOneAway(edge[1], start, closest)

        return closest


    ####################
    #
    def __findAndRemoveRedundant(self):
        """ Iterate over all nodes in graph to remove redundant links to beaten teams """

        for curNode in self.__gr.nodes():
            # Find everything one away.  If we see these later,
            # we can quickly remove them
            closest = []
            for edge in self.__gr.out_edges([curNode]):
                if edge[1] not in closest:
                    closest.append(edge[1])
                else:
                    self.__gr.delete_edge(edge[0], edge[1])

            # Now recursively dive down looking for these one
            # away nodes
            for edge in self.__gr.out_edges([curNode]):
                closest = self.__removeOneAway(edge[1], curNode, closest)


    ####################
    #
    def __genEdgeScores(self, week):

        for node in self.__gr.nodes():
            rels     = 0

            relSet   = set()
            winEdges = self.__countEdges(node, relSet, cntDown=True)
            rels    += len(relSet)

            relSet.clear()
            losEdges = self.__countEdges(node, relSet, cntDown=False)
            rels    += len(relSet)

            edgePower = winEdges - losEdges

            print ("%2d  %3s: %2d - %2d = %4d (%2d)") % (week, node,
                                                         winEdges, losEdges,
                                                         edgePower, rels)
            

    def __countEdges(self, node, visited, cntDown):
        count = 0
        if visited is None:
            visited = set()

        if cntDown:
            edgeList = self.__gr.out_edges(node)
            next     = 1
        else:
            edgeList = self.__gr.in_edges(node)
            next     = 0

        for edge in edgeList:
            count += 1
            if edge[next] in visited:
                continue
            visited.add(edge[next])
            count += self.__countEdges(edge[next], visited, cntDown)

        return count

    ####################
    #
    def __genBeatScores(self, week):

        for node in self.__gr.nodes():
            winSet  = self.__gatherDown(node)
            lossSet = self.__gatherUp(node)

            self.__loops[node] -= winSet | lossSet
            self.__loops[node].discard(node)

            wins     = len(winSet)
            losses   = len(lossSet)
            loopRels = len(self.__loops[node])

            totRels   = wins + losses + loopRels
            beatPower = (wins / float(totRels)) - (losses / float(totRels))
            beatPower = (beatPower + 1) * 50

            self.__leag.getTeam(node).setBeatPower(beatPower, totRels)

            #print ("%3s: %d/%d - %d/%d = %5.1f") % (node,
            #                                        wins, totRels,
            #                                        losses, totRels,
            #                                        beatPower)

    def __gatherDown(self, node):
        nodes = set()
        for edge in self.__gr.out_edges([node]):
            nodes.add(edge[1])
            for lower in self.__gatherDown(edge[1]):
                nodes.add(lower)
        return nodes

    def __gatherUp(self, node):
        nodes = set()
        for edge in self.__gr.in_edges(node):
            nodes.add(edge[0])
            for higher in self.__gatherUp(edge[0]):
                nodes.add(higher)
        return nodes
