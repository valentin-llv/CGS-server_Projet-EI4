import objgraph # Required to be installed and Graphviz to be installed

from gamesManager.gamesManager import GamesManager

def simpleMemoryVisualiser():
    objgraph.show_backrefs(GamesManager, filename='../sample-backref-graph.png')