'''
Created on Feb 23, 2016

@author: charper
TODO: Move any Puzzle solving code out of Graph
'''

import itertools
import os
import string
from collections import defaultdict, OrderedDict, deque

from lib.util import simplePickler, UniqueColorGenerator,\
    UniqueStringGenerator, MasterUniqueColorGenerator, sqliteDB
from lib.Geometry import MultiBlock
from lib.Node import GridNode, Rectangle, Point, GridSquare
from lib.Edge import Edge, OuterEdge, InnerEdge


class Graph(dict):
    '''
    A Graph containing Nodes(vertices) and Edges(links).

    Since this generic Graph can have any structure, we need the
    Nodes and Edges to be setup elsewhere.
    '''

    def __init__(self):
        self.paths = None
        self.potential_paths = None
        self.current_path = []
        self.solutions = []
        self.partitions = None
        self._all_paths = None

        self.edges=dict()

        self.rule_color_nodes = None
        self.rule_shape_nodes = None
        self.rule_sun_nodes = None
        self.must_travel_nodes = None
        
        # TODO: Hack
        self.finalized=False

    def set_nodes(self, node_list):
        ''' This should be called with a list of Nodes whose coordinate values
        have already been set (whatever that means for a particular Node/Graph 
        system).
        
        Since Graph inherits from dict, this is just assigning keys to values.
        '''
        for n in node_list:
            self[n.key()]=n
            #self.unsearched_nodes=self.copy()
    
    # TODO: Needed?
    def color_generator(self):
        return MasterUniqueColorGenerator

    def all_path_filename(self):
        raise NotImplementedError
    
    def get_edge(self, na, nb):
        return self.edges[frozenset([na,nb])]

if __name__ == '__main__':
    pass
    