'''
Created on Feb 4, 2016

@author: charper

'''

import logging

from lib.Geometry import Point, Rectangle
from lib.util import MasterUniqueNumberGenerator, MasterUniqueStringGenerator

from lib import lib_dbg_filehandler, lib_consolehandler, lib_inf_filehandler 
module_logger=logging.getLogger(__name__)
module_logger.addHandler(lib_inf_filehandler)
module_logger.addHandler(lib_dbg_filehandler)
#module_logger.addHandler(lib_consolehandler)
linf, ldbg = module_logger.info, module_logger.debug
ldbg('init:'+__name__)
linf('Info message!')

class Node(object):
    '''A generic Node (or vertex) in a Graph '''

    def key(self):
        '''Some way to identify position within the Graph. For Nodes 
        in a Grid this is simply (x,y) coordinates. 
        
        TODO: Not sure yet how to handle for others. '''
        raise NotImplementedError
        return ''

    def __repr__(self):
        return '%s:%s @%s' % (self.__class__.__name__, self.sym, str(self.key()))

    def __init__(self, hash_int=None):
        self.hash_int = hash_int or MasterUniqueNumberGenerator.get()
        self.sym = '!'
        self.is_exit = None
        self.is_entrance = None
        self.edges = set()

        
        self.neighbors = set()
        self.traversable_neighbors = set()
        self.finalized_traversable_neighbors = set()

        self.color = 'black'

    def finalize(self):
        #raise NotImplementedError
        if self.sym == '!':
            self.sym = MasterUniqueStringGenerator.get()
#         self.finalized_traversable_neighbors = frozenset(
#             self.traversable_neighbors)
#         self.neighbors = frozenset(self.neighbors)
        self.edges = frozenset(self.edges)


    def reset_node(self):
        pass
    
    def traversable_edges(self):
        for e in self.edges:
            if e.is_connected(self):
                yield e
                
    def traversable_nodes(self, auto_cut=True):
        for e in self.traversable_edges():
            if auto_cut:
                yield e.traverse_from_node(self)
            else:
                yield e.get_other_node(self)


class GridNode(Node):
    '''A GridNode in a graph.

    # TODO: possibly should make GridNode a sub-class of Point?
        Doesn't make sense for all Nodes, but it sure does
        for those on a RectangleGrid
    '''
    
    @property
    def x(self): return self.pt[0]
    @property
    def y(self): return self.pt[1]

    def __init__(self, x, y, gx, gy):
        Node.__init__(self)

        self.pt = Point((x, y))
        
        # TODO: I don't like this name
        self.linear_order = x + (y * gx)
        
        ''' TODO: Assumes only 90 degree neighbors,
        but Nodes can be laid out in Grid and still have
        non-90 degree neighbor.
        ''' 
        self.edge_map={'left':None,'upper':None,'right':None,'lower':None}
        
        # TODO: Make this a type of Rule instead?
        self.must_travel = None
        
        # TODO: BEGIN HACK. I don't like this
        self.on_left_boundary = False
        self.on_right_boundary = False
        self.on_lower_boundary = False
        self.on_upper_boundary = False
        if x == 0:
            self.on_left_boundary = True
        elif x == gx - 1:
            self.on_right_boundary = True
        if y == 0:
            self.on_lower_boundary = True
        elif y == gy - 1:
            self.on_upper_boundary = True
        # TODO: END HACK
        
        self.color = 'blue'

    def finalize(self):
        super().finalize()
        
    # TODO: possibly should make GridNode a sub-class of Point?
    def strict_left(self, other):
        return self.pt.x < other.pt.x
    def strict_below(self, other):
        return self.pt.y < other.pt.y
    def is_vertical_with(self, other):
        return self.pt.x == other.pt.x
    def is_horizontal_with(self, other):
        return self.pt.y == other.pt.y

    def get_color(self):
        col=self.color
        return col
    
    def key(self):
        return self.pt
    
    def add_90_degree_edge(self, e, direction):
        # TODO: Don't like this name
        self.edge_map[direction]=e
        self.add_edge(e)
        
    def add_edge(self, e):
        self.edges.add(e)
        
    def str(self):
        return self.__repr__()

class GridSquare(GridNode):
    default_color = 'grey'

    def __init__(self, x, y, gx, gy):
        GridNode.__init__(self, x, y, gx, gy)

        ''' Since this is actually a "square" between Nodes, return 
        the coordinates of all "outer" Nodes. This is NOT the same 
        as the coordinates of my "neighbors"! (It's the corners) 
        TODO: Use edges instead? '''
        self.outer_node_rect = Rectangle(
            [(x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1)])
        self.outer_node_coordinates = frozenset(
            [p for p in self.outer_node_rect])

        self.color = GridSquare.default_color
        
        self.rule_shape = None
        self.rule_color = None
        self.sun_color = None

    def set_rule_shape(self, shape):
        self.rule_shape = shape

    def finalize(self):
        super().finalize()
        # TODO: Only for Squares with color, but should be low-cost if this is only called once (as intended)
        # Still wasteful though
        self.different_color_boundaries = \
            self.get_different_color_boundaries()
    
    # TODO: needed?
    def prepare_for_partitioning(self):
        pass
        #print("wasted")

    def reset_node(self):
        super().reset_node()
        #print("wasted")
        #self.prepare_for_partitioning()
        #self.passed_rule_check = False

    def get_color(self):
        if self.sun_color:
            return self.sun_color
        if self.rule_color:
            return self.rule_color
        return self.color
        
    def set_rule_color(self, rule_color):
        #self.has_rule = True
        # self.color=color
        self.rule_color = rule_color
    
    def set_rule_sun(self, sun_color):
        self.sun_color=sun_color
    
    # colors are only "different" if both squares actually have a rule_color
    def different_color(self, other):
        return (self.rule_color and other.rule_color \
                and self.rule_color != other.rule_color)
    
    # the "outer nodes" I share with neighbor squares of a different color
    def get_different_color_boundaries(self):
        if not self.rule_color:
            return None
        for e in self.traversable_edges():
            nbr=e.get_other_node(self)
            if self.different_color(nbr):
                
                return frozenset(self.outer_node_coordinates & nbr.outer_node_coordinates)
            
#         for n in self.neighbors:
#             if self.different_color(n):
#                 return frozenset(self.outer_node_coordinates & n.outer_node_coordinates)

    def overlay_traversable_rects(self):
        trl = []
        if self.has_left_traversable_nbr():
            trl.append(
                Rectangle(self.get_sqare_points(1), self.offset() + Point((-1, 1)), 'pink'))
        if self.has_right_traversable_nbr():
            trl.append(
                Rectangle(self.get_sqare_points(1), self.offset() + Point((3, 1)), 'pink'))
        if self.has_lower_traversable_nbr():
            trl.append(
                Rectangle(self.get_sqare_points(1), self.offset() + Point((1, -1)), 'pink'))
        if self.has_upper_traversable_nbr():
            trl.append(
                Rectangle(self.get_sqare_points(1), self.offset() + Point((1, 3)), 'pink'))
        return trl
    

if __name__ == '__main__':
    
    n = GridNode(1, 0, gx=7, gy=5)
    n2 = GridNode(1, 1, gx=7, gy=5)
    n.finalize(), n2.finalize()

    n.neighbors.remove(n2)
    print(n, n.neighbors, n.print_nbrs())
    print(n2, n2.neighbors, n2.print_nbrs())

