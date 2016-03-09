'''
Created on Feb 4, 2016

@author: charper
'''
import string
import random
from math import hypot
from lib.Geometry import Point,Rectangle
from lib.util import MasterUniqueNumberGenerator, MasterUniqueStringGenerator
class Node(object):
    '''A generic Node (or vertex) in a Graph '''
    
#     def __hash__(self):
#         return self.hash_int
#     
#     def __eq__(self,other):
#         return self.__hash__() == other.__hash__()
     
    def __repr__(self):
        '''Ideally a single character string that should be unique within the Graph.

        Useful for rendering in ASCII art'''
        return self.sym
    
    def __init__(self, hash_int=None):
        self.hash_int = hash_int or MasterUniqueNumberGenerator.get()
        self.sym = '!'
        self.is_exit = None
        self.is_entrance = None
        
        self.been_traversed = False
        
        #TODO: GridSquare only?
        self.been_partitioned = False
        self.neighbors = set()
        self.traversable_neighbors = set()
        self.has_rule=False
        self.has_rule_color=False
        self.has_rule_shape=False
        self.passed_rule_check=False
        
        # A list of all the nodes that have me as a neighbor
        self.backref_nbrs = []
        
        self.color='black'
        
    def finalize(self):
        raise NotImplementedError
    
    def has_rule(self):
        return self.has_rule
    
    def add_neighbor(self, nbr, backref=False):
        self.neighbors.add(nbr)
        self.traversable_neighbors.add(nbr)
        if backref:
            nbr.backref_nbrs.append(self)
    
    # Get a random neighbor
    def get_random_traversable_neighbor(self):
        return self.neighbors[random.randint(0, len(self.neighbors) - 1)]
    
    def reset(self):
        self.been_traversed = False
        self.traversable_neighbors = set(self.neighbors)
        # TODO: Redundant?
        self.been_partitioned = False
        
    def remove_traversable(self, other):
        self.traversable_neighbors.remove(other)
        
    # TODO: Why did I think this was ever a good idea? Added Exception, get rid of this eventually
    def remove_traversable_no_err(self, other, warn=True):
        if not other in self.traversable_neighbors:
            if warn: print(self.vec(),'does not have', other.vec())
            raise Exception(self.vec(),'does not have', other.vec())
            return
        self.remove_traversable(other)
        
    def pop_any_traversable(self):
        return self.traversable_neighbors.pop()

    # TODO: If we want to do any fancy internal stuff when we get traversed, do it here?
    # TODO: No, we should do this in the Edge class
    def traverse(self, backref=True):
        if backref:
            for n in self.backref_nbrs:
                n.traversable_neighbors.remove(self)

    def print_nbrs(self):
        return [n.str() for n in self.traversable_neighbors]

    
class GridNode(Node):
    '''A GridNode in a graph.

    # TODO: possibly should make GridNode a sub-class of Point?
        Doesn't make sense for all Nodes, but it sure does
        for those on a RectangleGrid
    '''
    ColorList=['white','aqua','red','yellow','blue','green','purple']
    ColorDict=dict(enumerate(ColorList,start=1))
    
    rendering_weight=1
    
    @property
    def x(self): return self.pt[0]
    @property
    def y(self): return self.pt[1]
    
    def __init__(self, x, y, gx, gy):
        Node.__init__(self)
        
        self.pt=Point((x,y))
        
        self.on_left_boundary=False
        self.on_right_boundary=False
        self.on_lower_boundary=False
        self.on_upper_boundary=False
        if x == 0:
            self.on_left_boundary = True
        elif x == gx - 1:
            self.on_right_boundary = True
        if y == 0:
            self.on_lower_boundary = True
        elif y == gy - 1:
            self.on_upper_boundary = True
        
        self.rendering_weight=GridNode.rendering_weight
        # TODO: move to sub-class
        self.color='blue'
        #self.nType='out'
        self.has_rule=None
        
    def finalize(self):
        self.neighbors=frozenset(self.neighbors)
        if self.hash_int is None:
            self.hash_int=MasterUniqueNumberGenerator.get()
        if self.sym=='!':
            self.sym=MasterUniqueStringGenerator.get()
            
    # TODO: possibly should make GridNode a sub-class of Point?
    def strict_left(self, other):
        return self.pt.x < other.pt.x
    def strict_below(self,other):
        return self.pt.y < other.pt.y
    def is_vertical_with(self,other):
        return self.pt.x==other.pt.x
    def is_horizontal_with(self,other):
        return self.pt.y==other.pt.y
    
    def dimensions(self):
        return self.get_sqare_points(self.rendering_weight)
    
    def offset(self):
        #offset= self.x*4, self.y*4
        offset = self.x*(GridSquare.rendering_weight+1),self.y*(GridSquare.rendering_weight+1)
        return Point(offset)
    
    def get_color(self):
        return self.color
    def get_imgRect(self,scalar=1):
        raw_rect=Rectangle(self.dimensions(),self.offset(),self.get_color()).abs_coords(scalar)
        return raw_rect
    
    #TODO: Stubs, should put in Edge class anyways
    def left_path_traversed(self): return False
    def right_path_traversed(self): return False
    def upper_path_traversed(self): return False
    def lower_path_traversed(self): return False
    
    def get_rectangle_points(self,w,h):
        pl=[[0,0],[w,0],[w,h],[0,h]]
        #print(offset)
        rl=[Point(p) for p in pl]
        return rl
    
    def get_sqare_points(self,w): 
        return self.get_rectangle_points(w, w)

    def vec(self):
        return self.pt
    
    # TODO: finding traversable_neighbors is sloppy
    def has_right_traversable_nbr(self):
        return not self.on_right_boundary \
            and any([(self.x + 1, self.y) == n.vec() for n in self.traversable_neighbors])
    def has_left_traversable_nbr(self):
        return not self.on_left_boundary \
            and any([(self.x - 1, self.y) == n.vec() for n in self.traversable_neighbors])
    def has_lower_traversable_nbr(self):
        return not self.on_lower_boundary \
            and any([(self.x, self.y - 1) == n.vec() for n in self.traversable_neighbors])
    def has_upper_traversable_nbr(self):
        return not self.on_upper_boundary \
            and any([(self.x, self.y + 1) == n.vec() for n in self.traversable_neighbors])
    
    def str(self): return str(self.x) + ',' + str(self.y)+self.color

class GridSquare(GridNode):
    
    rendering_weight=3
    default_color='grey'
    def __init__(self, x, y, gx, gy):
        GridNode.__init__(self, x, y, gx, gy)
        
        ''' Since this is actually a "square" between Nodes, return the coordinates of all "outer" Nodes
        This is NOT the same as the coordinates of my "neighbors"! (It's the corners) '''
        
        self.outer_node_rect = Rectangle([(x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1)])
        self.outer_node_coordinates = frozenset([p for p in self.outer_node_rect])
        
        self.color=GridSquare.default_color
        
        self.rendering_weight=GridSquare.rendering_weight
        self.been_partitioned=False
        self.partition_neighbors=[]
        self.rule_shape=None
        self.rule_color=None
        self.partition_color=None
    
    def set_rule_shape(self, shape):
        self.has_rule=True
        self.has_rule_shape=True
        self.rule_shape=shape
        
    
    def finalize(self):
        
        self.different_color_boundaries = self.get_different_color_boundaries()
    
    def prepare_for_partitioning(self):    
        self.been_partitioned=False
        #self.color=GridSquare.default_color
        self.partition_color=None
        self.partition_neighbors=list(self.traversable_neighbors)
        
    def pop_any_partition_neighbor(self):
        nbr=self.partition_neighbors.pop()
        # And don't come back! *ptew*
        nbr.partition_neighbors.remove(self)
        return nbr
    
    def reset(self):
        super().reset()
        self.prepare_for_partitioning()
        self.passed_rule_check=False

    def reset_rule_check(self):
        self.been_partitioned=False
        self.passed_rule_check=False
        
    def offset(self):
        # The weight of a PathNode and a GridSquare
        total_weight=GridSquare.rendering_weight+GridNode.rendering_weight
        x,y=self.x,self.y
        offset= (x*total_weight)+1, (y*total_weight)+1
        return Point(offset)
    
    def get_color(self):
        if self.rule_color:
            return self.rule_color
        if self.partition_color:
            return self.partition_color
        return self.color
    def set_rule_color(self,color):
        self.has_rule=True
        self.has_rule_color=True
        #self.color=color
        self.rule_color=color
    
    # colors are only "different" if both squares actually have a rule_color
    def different_color(self, other):
        return (self.has_rule and other.has_rule and self.rule_color != other.rule_color)

    # the "outer nodes" I share with neighbor squares of a different color
    def get_different_color_boundaries(self):
        for n in self.neighbors:
            if self.different_color(n):
                return frozenset(self.outer_node_coordinates & n.outer_node_coordinates)

    def overlay_traversable_rects(self):
        trl=[]
        if self.has_left_traversable_nbr():
            trl.append(Rectangle(self.get_sqare_points(1),self.offset()+Point((0,1)),'pink'))
        if self.has_right_traversable_nbr():
            trl.append(Rectangle(self.get_sqare_points(1),self.offset()+Point((2,1)),'pink'))
        if self.has_lower_traversable_nbr():
            trl.append(Rectangle(self.get_sqare_points(1),self.offset()+Point((1,0)),'pink'))
        if self.has_upper_traversable_nbr():
            trl.append(Rectangle(self.get_sqare_points(1),self.offset()+Point((1,2)),'pink'))
        return trl
    
if __name__ == '__main__':
    a=None
    b='purple'
    #b=None
    print(a and b and a!=b)
    exit(0)
    n = GridNode(1, 0, gx=7, gy=5)
    n2 = GridNode(1, 1, gx=7, gy=5)
    n.finalize(),n2.finalize()
    n.add_neighbor(n2)
    n2.add_neighbor(n)
    n.neighbors.remove(n2)
    print(n,n.neighbors,n.print_nbrs())
    print(n2,n2.neighbors,n2.print_nbrs())
    print(n.get_imgRect(),n2.get_imgRect())
    print(n.get_imgRect()+n2.get_imgRect())
    

