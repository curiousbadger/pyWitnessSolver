'''
Created on Feb 4, 2016

@author: charper

TODO: Get rid of code invalidated by Edge logic. Make the Nodes "dumber" and less aware of things outside themselves.
'''
import string
import random
from math import hypot
from lib.Geometry import Point, Rectangle
from lib.util import MasterUniqueNumberGenerator, MasterUniqueStringGenerator


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
        self.been_traversed = False

        
        self.neighbors = set()
        self.traversable_neighbors = set()
        self.finalized_traversable_neighbors = set()

        self.color = 'black'

    def finalize(self):
        #raise NotImplementedError
        if self.sym == '!':
            self.sym = MasterUniqueStringGenerator.get()
#         if len(self.traversable_neighbors) == 0:
#             raise Exception('No traversable_neighbors', str(self))
        self.finalized_traversable_neighbors = frozenset(
            self.traversable_neighbors)
        self.neighbors = frozenset(self.neighbors)
        self.edges = frozenset(self.edges)

    def has_rule(self):
        raise Exception('foo')
        return self.rule_color or self.sun_color or self.rule_shape

    def add_neighbor(self, nbr, backref=False):
        self.neighbors.add(nbr)
        self.traversable_neighbors.add(nbr)
        if backref:
            nbr.backref_nbrs.append(self)

    # Get a random neighbor
    def get_random_traversable_neighbor(self):
        return self.neighbors[random.randint(0, len(self.neighbors) - 1)]

    def reset_node(self):
        pass

    def remove_traversable(self, other):
        try:
            self.traversable_neighbors.remove(other)
        except KeyError:
            raise Exception(
                '%s does not have %s in traversable_neighbors' % (self, other))

    def remove_traversable_no_err(self, other, warn=True):
        if not other in self.traversable_neighbors:
            if warn:
                print(self.key(), 'does not have', other.key())
            #raise Exception(str(self),'does not have', other.key())
            return
        self.remove_traversable(other)

    def pop_any_traversable(self):
        return self.traversable_neighbors.pop()
    
    def traversable_edges(self):
        for e in self.edges:
            if e.is_connected():
                yield e
                
    def traversable_nodes(self):
        for e in self.traversable_edges():
            yield e.traverse_from_node(self)
            

#     def print_nbrs(self):
#         return [n.str() for n in self.traversable_neighbors]


class GridNode(Node):
    '''A GridNode in a graph.

    # TODO: possibly should make GridNode a sub-class of Point?
        Doesn't make sense for all Nodes, but it sure does
        for those on a RectangleGrid
    '''
    
    rendering_weight = 1
    
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
        
        self.rendering_weight = GridNode.rendering_weight
        # TODO: move to sub-class
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

    # TODO: BEGIN GraphImage should handle this...
    def dimensions(self):
        return self.get_sqare_points(self.rendering_weight)
    def offset(self):
        #offset= self.x*4, self.y*4
        offset = self.x * \
            (GridSquare.rendering_weight + 1), self.y * \
            (GridSquare.rendering_weight + 1)
        return Point(offset)

    def get_color(self):
        col=self.color
        return col

    def get_imgRect(self, scalar=1):
        raw_rect = Rectangle(
            self.dimensions(), self.offset(), self.get_color()).abs_coords(scalar)
        return raw_rect

    def get_rectangle_points(self, w, h):
        pl = [[0, 0], [w, 0], [w, h], [0, h]]
        # print(offset)
        rl = [Point(p) for p in pl]
        return rl

    def get_sqare_points(self, w):
        return self.get_rectangle_points(w, w)
    # TODO: END  GraphImage should handle this...
    
    def key(self):
        return self.pt
    
    def add_90_degree_edge(self, e, direction):
        # TODO: Don't like this name
        self.edge_map[direction]=e
        self.add_edge(e)
        
    def add_edge(self, e):
        self.edges.add(e)
        
    def has_right_traversable_nbr(self):
        return self.edge_map['right'] and self.edge_map['right'].is_connected()
    
    def has_left_traversable_nbr(self):
        return self.edge_map['left'] and self.edge_map['left'].is_connected()

    def has_lower_traversable_nbr(self):
        return self.edge_map['lower'] and self.edge_map['lower'].is_connected()

    def has_upper_traversable_nbr(self):
        return self.edge_map['upper'] and self.edge_map['upper'].is_connected()

    def str(self):
        return self.__repr__()


class GridSquare(GridNode):

    rendering_weight = 3
    default_color = 'grey'

    def __init__(self, x, y, gx, gy):
        GridNode.__init__(self, x, y, gx, gy)

        ''' Since this is actually a "square" between Nodes, return 
        the coordinates of all "outer" Nodes. This is NOT the same 
        as the coordinates of my "neighbors"! (It's the corners) '''
        self.outer_node_rect = Rectangle(
            [(x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1)])
        self.outer_node_coordinates = frozenset(
            [p for p in self.outer_node_rect])

        self.color = GridSquare.default_color

        self.rendering_weight = GridSquare.rendering_weight
        
        self.partition_neighbors = []
        self.rule_shape = None
        self.rule_color = None
        self.sun_color = None
        self.partition_color = None

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
        self.partition_color = None

    def reset_node(self):
        super().reset_node()
        self.prepare_for_partitioning()
        #self.passed_rule_check = False

    def offset(self):
        # The weight of a PathNode and a GridSquare
        total_weight = GridSquare.rendering_weight + GridNode.rendering_weight
        x, y = self.x, self.y
        offset = (x * total_weight) + 1, (y * total_weight) + 1
        return Point(offset)

    def get_color(self):
        if self.sun_color:
            return self.sun_color
        if self.rule_color:
            return self.rule_color
#         if self.partition_color:
#             return self.partition_color
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
        for n in self.neighbors:
            if self.different_color(n):
                return frozenset(self.outer_node_coordinates & n.outer_node_coordinates)

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
    n.add_neighbor(n2)
    n2.add_neighbor(n)
    n.neighbors.remove(n2)
    print(n, n.neighbors, n.print_nbrs())
    print(n2, n2.neighbors, n2.print_nbrs())
    print(n.get_imgRect(), n2.get_imgRect())
    print(n.get_imgRect() + n2.get_imgRect())
