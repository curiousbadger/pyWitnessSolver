'''
Created on Feb 23, 2016

@author: charper
'''
from collections import defaultdict
import itertools
import os
import pickle
import string

from lib.Geometry import MultiBlock
from lib.Node import GridNode, Rectangle, Point, GridSquare
from lib.util import simplePickler, UniqueColorGenerator,\
    MasterUniqueColorGenerator
from lib.util import sqliteDB


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
        self.all_paths_pickler = simplePickler(self.all_path_filename())
        self._color_generator = None
    
    def color_generator(self):
        if not self._color_generator: self._color_generator = UniqueColorGenerator()
        return self._color_generator
    def all_path_filename(self):
        raise NotImplementedError

class RectGridGraph(Graph):
    '''A Graph laid out in a rectangular gx*gy grid.

    The "interior squares" are  the locations between any 4 Nodes connected
    in a ring. These also form Graphs, where the Edges are defined by
    the "outer" Edges which have NOT been traversed by a Path (the line).
    '''

    def __init__(self, gx, gy, is_outer=True):
        # TODO: Ugh, everything is turning into RectGridGraph :(
        self.gx = gx
        self.gy = gy
        Graph.__init__(self)

        self.is_outer = is_outer

        # Create Rectangle Grid
        for y in range(gy):
            for x in range(gx):
                #print (x,y)
                n = GridNode(x, y, gx, gy) if is_outer else GridSquare(
                    x, y, gx, gy)
                self[x, y] = n
                #self[x, y].nType = 'out' if is_outer else 'in'

        ''' Setup a list of sorted keys for when we want to iterate in order
        The sort key is just the GridNode vector reversed (y,x) so that we can return
        the lowest row left-right then continue up.
        '''
        self.sorted_keys = sorted(self.keys(), key=lambda k: (k[1], k[0]))

        # teach each node it's neighbors
        for iy in range(self.gy):
            for ix in range(self.gx):
                n = self[ix, iy]
                # top nbr ex iy=gy-1
                if iy < gy - 1:
                    n.add_neighbor(self[ix, iy + 1])
                # add bottom ex iy=0
                if iy > 0:
                    n.add_neighbor(self[ix, iy - 1])
                # add right ex ix=0
                if ix < gx - 1:
                    n.add_neighbor(self[ix + 1, iy])
                # add left ex ix=0
                if ix > 0:
                    n.add_neighbor(self[ix - 1, iy])

        '''BEGIN: Outer-Grid specific setup '''
        if is_outer == True:

            # initialize the "inner squares" grid
            self.inner_grid = RectGridGraph(gx - 1, gy - 1, False)

            # Create mapping from Segment in a Path to bordering Squares
            self.create_edge_to_square_map()

            # Assign each GridNode a unique hash value and symbol (if possible)
            # within this Graph
            self.assign_keys()

            # some paths are best avoided...
            for iy in range(self.gy):
                for ix in range(self.gx):
                    n = self[ix, iy]
                    # Remove left neighbor from bottom row
                    if iy == 0 and ix > 0:
                        n.remove_traversable_no_err(self[ix - 1, iy])
                    # Remove left neighbor from top row
                    if iy == gy - 1 and ix > 0:
                        n.remove_traversable_no_err(self[ix - 1, iy])
                    # Remove bottom neighbor from left row
                    if (ix == 0 or ix == gx - 1) and iy > 0:
                        n.remove_traversable_no_err(self[ix, iy - 1])
                    # Remove bottom neighbor from right row
        '''END: Outer-Grid specific setup '''
    '''END: __init__ '''

    def create_edge_to_square_map(self):
        ''' For each pair of Outer Nodes, setup a dictionary that returns 
        the Inner Squares they touch. This answers the question, what Squares
        are on either side of any given Segment (Edge) in a Path?
        '''
        oid = self.outer_to_inner = defaultdict(list)
        for n in self.values():
            for nbr in n.neighbors:
                # sort the node and neighbor so that they are always in left-right
                # or lower-upper order
                first, second = sorted([n, nbr], key=lambda x: x.pt)

                segment = frozenset([first.pt, second.pt])

                if segment not in oid:
                    # vertical segment, add left-right squares
                    if first.is_vertical_with(second):
                        # add the left square if it exists
                        if not first.on_left_boundary:
                            oid[segment].append(
                                self.inner_grid[first.x - 1, first.y])
                        # add the right square if not on right edge
                        if not first.on_right_boundary:
                            oid[segment].append(
                                self.inner_grid[first.x, first.y])
                    # horizontal segment, add above-below squares
                    elif first.is_horizontal_with(second):
                        # Lower square
                        if not first.on_lower_boundary:
                            oid[segment].append(
                                self.inner_grid[first.x, first.y - 1])
                        # Upper sqare
                        if not first.on_upper_boundary:
                            oid[segment].append(
                                self.inner_grid[first.x, first.y])

    def assign_keys(self):
        '''Should assign a unique hash value and optionally an ASCII string
        for visualization.'''
        for hi, n in zip(itertools.count(), self.iter_all()):
            n.hash_int = hi

        # All numbers and letters
        symbol_string = string.digits + \
            string.ascii_letters + string.punctuation
        # IMPORTANT: Symbol will NOT be unique if Grid has more Nodes than
        # characters in symbol_string
        symbol_list = [c for c in symbol_string if c != '!']
        for n, sym in zip(self.iter_all_sorted(), itertools.cycle(symbol_list)):
            n.sym = sym

    def iter_sorted(self):
        for sk in self.sorted_keys:
            yield self[sk]

    def iter_all(self):
        '''Should return iterators for every GridNode in the Graph, regardless of GridNode sub-class '''
        return itertools.chain(self.values(), self.inner_grid.values())

    def iter_all_sorted(self):
        return itertools.chain(self.iter_sorted(), self.inner_grid.iter_sorted())

    def lower_left(self):
        return self[0, 0]

    def upper_right(self):
        return self[self.gx - 1, self.gy - 1]

    def iter_nodes_print_order(self):
        '''Iterate over the nodes in print order, top left-right the down a row... '''
        for y in range(self.gy - 1, -1, -1):
            for x in range(self.gx):
                yield self[x, y]

    def outer_row_str(self, row):
        return ' '.join([self[x, row].sym for x in range(self.gx)])

    def inner_row_str(self, row):
        return ' ' + ' '.join(self.inner_grid[x, row].sym for x in range(self.gx - 1))

    def render_both(self):
        m = []
        m.append('-------------------')
        for y in range(self.gy - 1, -1, -1):
            m.append(self.outer_row_str(y))
            if y > 0:
                m.append(self.inner_row_str(y - 1))

        m.append('********************')

        jm = '\n'.join([l for l in m])
        return jm

    # TODO: Come up with better naming convention for entrance/exit node variations?
    # Probably better to put that info in a sqliteDB, this is getting too cumbersome
    def paths_filename(self):
        gx, gy = self.gx, self.gy
        return '%dx%dRectGridGraph' % (gx, gy)
        
    def all_path_filename(self):
        return self.paths_filename()+'_all'
    
    def remove_inner_nbrs(self, seg):
        '''For each Square on either side of the segment, remove it's neighbors
        TODO: Encapsulate in Edge class?
        '''
        sorted_seg = frozenset(seg)
        squares = self.outer_to_inner[sorted_seg]

        if not squares:
            raise Exception('no squares', seg)

        # only do this if the segment is not on the border
        if len(squares) == 2:
            s1, s2 = squares
            s1.remove_traversable(s2)
            s2.remove_traversable(s1)

    def finalize(self):
        for n in self.iter_all():
            n.finalize()

    def reset(self):
        for n in self.values():
            n.reset()

    def render_with_links(self, sx, sy):
        m = []
        m.append(['-------------------\n'])
        dl = []
        for y in range(self.gy - 1, -1, -1):
            m.append([])
            dl = []
            for x in range(self.gx):
                m[-1].append('!' if x == sx and y ==
                             sy else str(self.nl[x][y]))
                m[-1].append('-' if self.nl[x]
                             [y].has_right_traversable_nbr() else ' ')
                dl.append(
                    '|' if self.nl[x][y].has_lower_traversable_nbr() else ' ')
                dl.append(' ')
            m.append(dl)
        m.append([' '])
        #m[-1].extend([str(x) for x in range(self.width)])
        m.append(['********************'])
        jm = '\n'.join([''.join([str(y) for y in x]) for x in m])
        return jm

    def load_paths(self):
        if self.paths:
            print('Warning: self.paths already loaded')
            #raise Exception('self.paths already loaded')
        self.paths = self.all_paths_pickler.load()
    
    def add_path(self, new_path, to_obj=True, to_db=False):
        if to_obj:
            # TODO: make path a set based class with ordering
            #self.paths.add(new_path)
            self.paths.append(new_path)
        if to_db:
            pass
    
    def generate_paths(self, overwrite=False):
        '''Traverse all possible Paths.

        TODO: Early dead-end detection?
        '''
        if self.all_paths_pickler.file_exists():
            if not overwrite:
                print('Skipping path generation...')
                return
            else:
                print('overwriting:', self.all_path_filename())
                
        # TODO: make path a set based class with ordering (OrderedDict?)
        #self.paths = set()
        self.paths = []
        path = []
        entrance_nodes = [n for n in self.values() if n.is_entrance]

        for n in entrance_nodes:
            self.travel(n, path)

        print('Done! found:', len(self.paths), 'total paths')
        self.all_paths_pickler.dump(self.paths)


    def travel(self, n, path):
        ''' Depth-first traversal of all possible paths'''
        # A node cannot be entered twice
        if n.vec() in path:
            return
        # Append the new node to the new path
        new_path = list(path)
        new_path.append(n.vec())

        # Are we done yet?
        if n.is_exit:
            self.add_path(new_path,to_obj=True, to_db=False)
            # TODO: Assumes that there's only 1 exit
            return

        # head on down the line...
        for nxt in n.neighbors:
            self.travel(nxt, new_path)

    def travel_write_to_db(self, n, path):
        if n.vec() in path:
            return
        new_path = list(path)
        new_path.append(n.vec())
        # Are we done yet?
        if n.is_exit:
            # self.paths_txt.write(str(new_path)+'\n')
            self.db.write_path(path)
            return
        for nxt in n.traversable_neighbors:
            self.travel_write_to_db(nxt, new_path)

    def check_colors(self, n, color):
        ''' Recursively iterate over every neighbor of n, at each point check 
        for a difference in color. On first violation, return True. 
        If no violations are found, return False. 

        PRE: Colors have been assigned to squares. 
        '''
        # TOOD: Sloppy to use has_rule, should detect ColorSquare subclass of
        # GridNode?
        if n.has_rule and n.color != color:
            return True

        # TODO: Should not actually occur since it's much more efficient to
        # call this with all and only colored squares
        if n.has_rule and color is None:
            color = n.color

        while n.traversable_neighbors:
            nbr = n.pop_any_traversable()
            if self.check_colors(nbr, color):
                return True
        return False

    def set_current_path(self, path):
        # Restore all traversable links between Squares
        self.inner_grid.reset()
        self.current_path = []
        # Traverse the path, removing neighbors from Squares accordingly
        for i in range(len(path) - 1):
            # For each Segment in the Path (technically an edge between Outer
            # Nodes)
            seg = list(path[i:i + 2])

            # Sever the link between 2 Squares (unless on Graph border)
            self.remove_inner_nbrs(seg)
            self.current_path.append(frozenset(seg))

    def find_any_shape_violation(self):
        violation=False
        for n in self.inner_grid.values():
            if n.has_rule_shape and not n.passed_rule_check:
                violation = self.shape_violation_check(n)
                # print(n,'found shape violation')
                if violation: break
        return violation
    
    def shape_violation_check(self, n):
        '''Returns True if n cannot reside in it's Partition.
        TODO: Invert so that each Partition with MultiBlock shapes checks all
        it's Nodes '''
        
        
        current_partition=self.retreive_partition(n)
        if not current_partition: raise Exception('Unable to find partition for ', n)
        
        #print('Checking GridSquare:', n, 'in partition', current_partition)

        # TODO: Make Partition a class that knows the rules, counts etc of it's Squares?
        # accumulate all MultiBlocks in this partition
        shapes = [n.rule_shape for n in current_partition if n.rule_shape]
        
        #calculate the sum of all points in all shapes
        num_shape_points=sum([len(n) for n in shapes])
        #print('shapes', shapes,'num_shape_points',num_shape_points)
        # get all points with the partition
        partition_points = [n.pt for n in current_partition]
        #print('partition_points', partition_points)
        # A set of points is a MultiBlock... (and a Grid and a Graph and ugh...)
        partition_multiblock = MultiBlock(
            partition_points, name='partition_multiblock', auto_shift_Q1=True)
        #print('partition_multiblock', partition_multiblock)
        
        # Check the easy violations first
        
        '''If this partition doesn't have the same number of Squares as the 
        sum of the number of points in the shapes, there's no way they will
        fit.
        TODO: Until of course I add the blue "subtraction shapes"...
        '''
        if num_shape_points!=len(partition_multiblock):
            return True
        
        return not self.compose_shapes(0, shapes, partition_multiblock, None)
    
    def compose_shapes(self,counter, shapes_list, partition, last_offset):
        #print('START compose_shapes')
        #print('    counter',counter)
        #print('    partition',partition.part_off())
        cur_shape=shapes_list[counter]
        
        # Remember the last offset, if we find a solution this helps with rendering
        cur_shape.last_offset=partition.last_offset
        
        # Iterate over all possible positions this shape could occupy
        for remaining_partition_points,new_offset in cur_shape.compose(partition):
            
            #print('remaining_partition_points',remaining_partition_points)
            if not remaining_partition_points:
                if counter==len(shapes_list)-1:
                    #print('Found solution!!') 
                    return True
                else:
                    #print('Ran out of room')
                    return False
            elif counter < len(shapes_list)-1:
                remaining_partition=MultiBlock(remaining_partition_points)
                remaining_partition.last_offset+=partition.last_offset
                #print('remaining_partition.last_offset',remaining_partition.last_offset)
                ret = self.compose_shapes(counter+1, shapes_list, remaining_partition, new_offset)
                if ret==True:
                    return True
                else: 
                    #print('counter',counter,'cur_shape',cur_shape)
                    pass
            else:
                #print('counter',counter,'at end of shape list')
                pass
        return False

    def travel_partition(self, n, partition):
        if n not in partition:
            n.been_partitioned = True
            partition.add(n)

        while n.partition_neighbors:
            nbr = n.pop_any_partition_neighbor()
            self.travel_partition(nbr, partition)
            
    def generate_partition(self, n, auto_color=True):
        '''Return the Partition that contains this GridSquare'''
        if not self.partitions:
            self.partitions=[]
        new_partition = set()
        self.travel_partition(n, new_partition)
        finalized_new_partition=frozenset(new_partition)
        self.partitions.append(finalized_new_partition)
        
        # Optionally color partitions
        if auto_color == True:
            partition_color = self.color_generator().get()
            for n in finalized_new_partition:
                n.color = partition_color
                # print(p,self.inner_grid[nvec].vec())
                    
        return finalized_new_partition
    
    def retreive_partition(self,n):
        # Find the partition that contains this Node (for now just GridSquares)
        found_partition=None
        
        if not n.been_partitioned:
            found_partition=self.generate_partition(n)
        
        for p in self.partitions:
            if n in p: found_partition=p
        if found_partition is None:
            raise Exception('Unable to find partition for', n)
        return found_partition
    
    def generate_all_partitions(self):
        '''Returns a list of Partitions.
        A Partition is a sub-set of one or more GridSquares bounded by the Path and the outer border.
        Each GridSquare in a Partition must be connected to all other GridSquares in the Partition
        through the traversable_neighbor list. 

        PRE: self.current_path has been set, so GridSquares have had their traversable_neighbors removed.'''
        self.partitions = []
        for n in self.inner_grid.values():
            n.prepare_for_partitioning()
        for n in self.inner_grid.values():
            if not n.been_partitioned:
                new_partition = set()
                self.travel_partition(n, new_partition)
                # print(new_partition)
                self.partitions.append(frozenset(new_partition))
        #print('partitions generated', self.partitions)
        


def graph_print(*args):
    pass
#print=graph_print

class GridGraph(Graph):
    ''' A Graph where each Node can be described with (x,y) coordinates.

    This is not necessarily a rectangle (see below).

    '''

    def __init__(self, node_list):
        for n in node_list:
            self[n.vec()] = n

if __name__ == '__main__':
    pass
