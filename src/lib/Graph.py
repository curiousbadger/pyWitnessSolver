'''
Created on Feb 23, 2016

@author: charper
'''
from collections import defaultdict
import itertools
import os
import string

from lib.Geometry import MultiBlock
from lib.Node import GridNode, Rectangle, Point, GridSquare
from lib.util import simplePickler, UniqueColorGenerator,\
    MasterUniqueColorGenerator
from lib.util import sqliteDB
from _collections import OrderedDict, deque
from lib.Edge import Edge


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
        self.edges=None

    def set_nodes(self, node_list):
        for n in node_list:
            self[n.vec()]=n
    def color_generator(self):
        if not self._color_generator:
            self._color_generator = UniqueColorGenerator()
        return self._color_generator

    def all_path_filename(self):
        raise NotImplementedError
    
    def get_edge(self, na, nb):
        return self.edges[frozenset([na,nb])]

class GridGraph(Graph):
    ''' A Graph where each Node can be described with (x,y) coordinates.

    This is not necessarily a rectangle (see below).

    '''
    def __init__(self, node_list):
        for n in node_list:
            self[n.vec()] = n

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

        # Create the list of Nodes
        node_list=[]
        for y in range(gy):
            for x in range(gx):
                #print (x,y)
                # "Outer" vs "Interior" Nodes have different behaviour, though currently Inner is a sub-class
                if self.is_outer:
                    n = GridNode(x, y, gx, gy) 
                else:
                    n= GridSquare(x, y, gx, gy)
                node_list.append(n)
        
        self.set_nodes(node_list)
        
        ''' Setup a list of sorted keys for when we want to iterate in order
        The sort key is just the GridNode vector reversed (y,x) so that we can return
        the lowest row left-right then continue up.
        '''
        self.sorted_keys = sorted(self.keys(), key=lambda k: (k[1], k[0]))

        self.assign_neighbors()
        
        '''BEGIN: Outer-Grid specific setup '''
        if is_outer == True:

            # initialize the "inner squares" grid
            self.inner_grid = RectGridGraph(gx - 1, gy - 1, False)

            # Create mapping from Segment in a Path to bordering Squares
            self.create_edge_to_square_map()

            # Assign each GridNode a unique symbol (if possible) within this Graph
            self.assign_keys()
            
            # some paths are best avoided...
            self.remove_dead_ends()
        '''END: Outer-Grid specific setup '''
    '''END: __init__ '''

    def assign_neighbors(self):
        self.edges=dict()
        gx,gy=self.gx,self.gy
        # teach each node it's neighbors, mind the borders
        for y in range(gy):
            for x in range(gx):
                n = self[x, y]
                nbr=None
                nbr_list=[]
                # Figure out which neighbors this Node has
                # add top neighbor unless this is the top row: y=gy-1
                if y < gy - 1:
                    nbr_list.append(self[x, y + 1])
                # add bottom ex y=0
                if y > 0:
                    nbr_list.append(self[x, y - 1])
                # add right ex x=0
                if x < gx - 1:
                    nbr_list.append(self[x + 1, y])
                # add left ex x=0
                if x > 0:
                    nbr_list.append(self[x - 1, y])
#                 if n.vec()==(0,1):
#                     print('n',n,'nbr',nbr)
                
                # Each node-neighbor pair corresponds to an Edge 
                for nbr in nbr_list:
                    # Teach the node it's neighbor directly TODO: May just use Node.edges later?
                    n.add_neighbor(nbr)
                    # Order doesn't really matter for an Edge's Nodes, use a frozenset
                    node_set=frozenset([n,nbr])
                    # Have we already encountered this pair?
                    if node_set in self.edges:
                        #print('already created', node_set)
                        cur_edge=self.edges[node_set]
                    else:
                        cur_edge=Edge(node_set)
                    # The address of each Edge is 2 Nodes
                    self.edges[node_set]=cur_edge
                    # Add the Edge to the Node's internal set of Edges as well
                    n.edges.add(cur_edge)
    
    
    def remove_dead_ends(self):
        # TODO: This only applies to low-left entrance, upper-right exit...
        gx,gy=self.gx,self.gy
        for y in range(gy):
            for x in range(gx):
                n = self[x, y]
                nbr=None
                # Remove left neighbor from top and bottom row
                if x > 0 and y in (0, gy-1):
                    nbr=self[x - 1, y]
                # Remove bottom neighbor from left and right rows
                elif y > 0 and x in (0, gx-1):
                    nbr=self[x, y - 1]
                if nbr:
                    n.remove_traversable_no_err(nbr)
                      
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
    # Probably better to put that info in a sqliteDB, this is getting too
    # cumbersome
    def paths_filename(self):
        gx, gy = self.gx, self.gy
        return '%dx%dRectGridGraph' % (gx, gy)

    def all_path_filename(self):
        return self.paths_filename() + '_all'


    def finalize(self):
        print('Finalizing Grid:', str(self))
        for n in self.iter_all():
            n.finalize()

    def prepare_for_partitioning(self):
        self.reset()
        
    def reset(self):
        self.color_generator().reset()
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
            # self.paths.add(new_path)
            self.paths.append(list(new_path))
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
        path = OrderedDict()
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
        new_path = OrderedDict(path)
        new_path[n.vec()]=None

        # Are we done yet?
        if n.is_exit:
            self.add_path(new_path, to_obj=True, to_db=False)
            # TODO: Assumes that there's only 1 exit
            return

        # head on down the line...
        for nxt in n.neighbors:
            self.travel(nxt, new_path)
            
    def set_current_path(self, path):
        # Restore all traversable links between Squares
        self.prepare_for_partitioning()
        self.inner_grid.prepare_for_partitioning()
        self.current_path = []
        
        # Traverse the path, removing neighbors from Squares accordingly
        # For each Segment in the Path (technically an edge between Outer
        # Nodes)
        for i in range(len(path)-1):
            seg=frozenset(path[i:i+2])
            # Sever the link between 2 Squares (unless on Graph border)
            self.remove_inner_nbrs(seg)
            self.current_path.append(seg)
            
        
        for n in self.inner_grid.values():
            n.set_partition_neighbors()
            
    def remove_inner_nbrs(self, seg):
        '''For each Square on either side of the segment, remove it's neighbors
        TODO: Encapsulate in Edge class?
        '''
        sorted_seg = frozenset(seg)
        squares = self.outer_to_inner[sorted_seg]
#         if not squares:
#             raise Exception('no squares', seg)
        # only do this if the segment is not on the border
        if len(squares) == 2:
            s1, s2 = squares
            #print('s1',s1,'s2',s2)
            s1.remove_traversable_no_err(s2)
            s2.remove_traversable_no_err(s1)
    
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
        
        partition=self.retreive_partition(n)
        #print('partition', partition)
        
        if any(n.different_color(p_nbr) for p_nbr in partition):
            return True
        return False
        
    def has_rule_shapes(self):
        return any(n.has_rule and n.has_rule_shape for n in self.inner_grid.values())
    
    def find_any_shape_violation(self):
        
        if not self.has_rule_shapes():
            return False
        
        violation = False
        
#         for n in self.inner_grid.values():
#             n.prepare_for_partitioning()
                
        for n in self.inner_grid.values():
            if n.has_rule_shape and not n.passed_rule_check:
                # TODO: probably no need to check for further violations, but leaving in while working out bugs
                violation = self.shape_violation_check(n)
                # print(n,'found shape violation')
                if violation:
                    break
        return violation

    def shape_violation_check(self, n):
        '''Returns True if n cannot reside in it's Partition.
        TODO: Invert so that each Partition with MultiBlock shapes checks all
        it's Nodes '''

        current_partition = self.retreive_partition(n)
        if not current_partition:
            raise Exception('Unable to find partition for ', n)

        #print('Checking GridSquare:', n, 'in partition', current_partition)

        # TODO: Make Partition a class that knows the rules, counts etc of it's Squares?
        # accumulate all MultiBlocks in this partition
        shapes = [n.rule_shape for n in current_partition if n.rule_shape]

        # calculate the sum of all points in all shapes
        num_shape_points = sum([len(n) for n in shapes])
        #print('shapes', shapes,'num_shape_points',num_shape_points)
        # get all points with the partition
        partition_points = [n.pt for n in current_partition]
        #print('partition_points', partition_points)
        # A set of points is a MultiBlock... (and a Grid and a Graph and
        # ugh...)
        partition_multiblock = MultiBlock(
            partition_points, name='partition_multiblock', auto_shift_Q1=True)
        #print('partition_multiblock', partition_multiblock)

        # Check the easy violations first

        '''If this partition doesn't have the same number of Squares as the 
        sum of the number of points in the shapes, there's no way they will
        fit.
        TODO: Until of course I add the blue "subtraction shapes"...
        '''
        if num_shape_points != len(partition_multiblock):
            return True

        return not self.compose_shapes(0, shapes, partition_multiblock, None)

    def compose_shapes(self, counter, shapes_list, partition, last_offset):
        #print('START compose_shapes')
        #print('    counter',counter)
        #print('    partition',partition.part_off())
        cur_shape = shapes_list[counter]

        # Remember the last offset, if we find a solution this helps with
        # rendering
        cur_shape.last_offset = partition.last_offset

        # Iterate over all possible positions this shape could occupy
        for remaining_partition_points, new_offset in cur_shape.compose(partition):

            # print('remaining_partition_points',remaining_partition_points)
            if not remaining_partition_points:
                if counter == len(shapes_list) - 1:
                    #print('Found solution!!')
                    return True
                else:
                    #print('Ran out of room')
                    return False
            elif counter < len(shapes_list) - 1:
                remaining_partition = MultiBlock(remaining_partition_points)
                remaining_partition.last_offset += partition.last_offset
                # print('remaining_partition.last_offset',remaining_partition.last_offset)
                ret = self.compose_shapes(
                    counter + 1, shapes_list, remaining_partition, new_offset)
                if ret == True:
                    return True
                else:
                    # print('counter',counter,'cur_shape',cur_shape)
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
            self.partitions = []
        new_partition = set()
        self.travel_partition(n, new_partition)
        finalized_new_partition = frozenset(new_partition)
        self.partitions.append(finalized_new_partition)

        # Optionally color partitions
        if auto_color == True:
            partition_color = self.color_generator().get()
            for n in finalized_new_partition:
                n.partition_color = partition_color
                # print(p,self.inner_grid[nvec].vec())

        return finalized_new_partition

    def retreive_partition(self, n):
        # Find the partition that contains this Node (for now just GridSquares)
        found_partition = None

        if not n.been_partitioned:
            found_partition = self.generate_partition(n)

        for p in self.partitions:
            if n in p:
                found_partition = p
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
# print=graph_print

if __name__ == '__main__':
    rgg=RectGridGraph(4,4)
    rgg.finalize()
    print(rgg.render_both())
    for k,v in rgg.edges.items():
        print('k,v',k,v)
#     for ie in rgg.inner_grid.edges:
#         print('ie',ie)
    fs=frozenset([rgg[0,0],rgg[0,1]])
#     print('fs', fs)
#     for k in rgg.edges.keys():
#         print(k)
#     for n in rgg.iter_sorted():
#         print(n,'n.edges',n.edges)
#     
    print(len(rgg.edges))
    print(max(len(n.edges) for n in rgg.values()))
    