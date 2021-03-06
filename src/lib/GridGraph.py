'''
Created on Mar 23, 2016

@author: charper
'''

import itertools
from collections import OrderedDict

import logging
from lib import lib_dbg_filehandler, lib_consolehandler, lib_inf_filehandler
module_logger=logging.getLogger(__name__)
module_logger.addHandler(lib_dbg_filehandler)
module_logger.addHandler(lib_inf_filehandler)
#module_logger.addHandler(lib_consolehandler)
linf, ldbg = module_logger.info, module_logger.debug
ldbg('init:'+__name__)


from lib.util import simplePickler, UniqueStringGenerator

from lib.Graph import Graph

from lib.Node import GridNode, GridSquare
from lib.Edge import OuterEdge, InnerEdge


class GridGraph(Graph):
    ''' A Graph where each Node can be described with (x,y) coordinates.

    This is not necessarily a rectangle (see below).

    '''

    def __init__(self, node_list):
        for n in node_list:
            self[n.key()] = n


from lib.Partition import Partition


class RectGridGraph(Graph):
    '''A Graph laid out in a rectangular gx*gy grid.

    The "interior squares" are  the locations between any 4 Nodes connected
    in a ring. These also form Graphs, where the Edges are defined by
    the "outer" Edges which have NOT been traversed by a Path (the line).
    '''

    def __init__(self, gx, gy, is_outer=True, auto_assign_edges=True):
        # TODO: Ugh, everything is turning into RectGridGraph :(
        self.gx = gx
        self.gy = gy
        Graph.__init__(self)
        
        self.is_outer = is_outer

        # Create the list of Nodes
        node_list = []
        for y in range(gy):
            for x in range(gx):
                #print (x,y)
                # "Outer" vs "Inner" Nodes have different behaviour, though currently Inner is a sub-class
                if self.is_outer:
                    n = GridNode(x, y, gx, gy)
                else:
                    n = GridSquare(x, y, gx, gy)
                node_list.append(n)

        self.set_nodes(node_list)

        ''' Setup a list of sorted keys for when we want to iterate in order
        The sort key is just the GridNode vector reversed (y,x) so that we can return
        the lowest row left-right then continue up.
        '''
        self.sorted_keys = sorted(self.keys(), key=lambda k: (k[1], k[0]))
        
        # Assign 90 degree Edges to all nodes
        # TODO: Move this out of __init__
        if auto_assign_edges:
            self.assign_edges()

        '''BEGIN: Outer-Grid specific setup '''
        if is_outer == True:
            
            
            # initialize the "inner squares" grid
            self.inner_grid = RectGridGraph(gx - 1, gy - 1, is_outer=False, auto_assign_edges=auto_assign_edges)
            # TODO: Move this out of __init__
            if auto_assign_edges:
                self.associate_outer_to_inner()
                # some paths are best avoided...
                self.remove_path_dead_ends()
            
            # Assign each GridNode a unique symbol (if possible) within this
            # Graph
            self.assign_symbols()

        '''END: Outer-Grid specific setup '''
    '''END: __init__ '''

    def assign_edges(self):
        ''' Create Edge relationships between Nodes '''
        self.edges = dict()
        gx, gy = self.gx, self.gy
        # teach each node it's neighbors, mind the borders
        for y in range(gy):
            for x in range(gx):
                n = self[x, y]
                # Figure out which neighbors this Node has
                nbr = None
                nbr_list = []
                # add top neighbor unless this is the top row: y=gy-1
                if y < gy - 1:
                    nbr_list.append([self[x,y+1], 'upper'])
                # add bottom except y=0
                if y > 0:
                    nbr_list.append([self[x,y-1], 'lower'])
                # add right except x=0
                if x < gx - 1:
                    nbr_list.append([self[x+1,y], 'right'])
                # add left except x=0
                if x > 0:
                    nbr_list.append([self[x-1,y], 'left'])

                # Each node-neighbor pair corresponds to an Edge
                for nbr, direction in nbr_list:
                    # An Edge is a set of Nodes
                    node_set = frozenset([n, nbr])
                    # Have we already encountered this pair?
                    if node_set in self.edges:
                        cur_edge = self.edges[node_set]
                    else:
                        # Create a new Edge
                        if self.is_outer:
                            cur_edge = OuterEdge(node_set)
                        else:
                            cur_edge = InnerEdge(node_set)
                    # The address of each Edge is 2 Nodes
                    self.edges[node_set] = cur_edge
                    # Add the Edge to the Node's internal set of Edges as well
                    n.add_90_degree_edge(cur_edge, direction)

    def remove_path_dead_ends(self):
        # TODO: This only applies to low-left entrance, upper-right exit...
        gx, gy = self.gx, self.gy
        for y in range(gy):
            for x in range(gx):
                n = self[x, y]
                nbr = None
                # Remove left neighbor from top and bottom row
                if x > 0 and y in (0, gy - 1):
                    nbr = self[x - 1, y]
                # Remove bottom neighbor from left and right rows
                elif y > 0 and x in (0, gx - 1):
                    nbr = self[x, y - 1]
                if nbr:
                    e = self.get_edge(n, nbr)
                    # Cut the line
                    e.sever(n)

    def associate_outer_to_inner(self):
        ''' Teach the OuterEdges which corresponding InnerEdge runs
        "below" them, if any. '''

        for edge in self.edges.values():
            # Sort the nodes so that they are always in lower-upper or
            # left-right order
            n1, n2 = sorted(
                [outer_node for outer_node in edge.nodes], key=lambda x: x.pt)
            
            first_square, second_square = None, None

            # vertical segment, add left-right squares if they exist
            if n1.is_vertical_with(n2):
                if (n1.on_left_boundary or n2.on_left_boundary): continue
                if not n1.on_left_boundary:
                    first_square = self.inner_grid[
                        n1.x - 1, n1.y]
                if not n1.on_right_boundary:
                    second_square = self.inner_grid[n1.x, n1.y]

            # horizontal segment, add above-below squares
            elif n1.is_horizontal_with(n2):
                if not n1.on_lower_boundary:
                    first_square = self.inner_grid[
                        n1.x, n1.y - 1]
                if not n1.on_upper_boundary:
                    second_square = self.inner_grid[n1.x, n1.y]

            # If there is an Inner GridSquare on both sides of the edge,
            # tie it to the InnerEdge that runs "beneath" it
            if first_square and second_square:
                inner_edge = self.inner_grid.get_edge(
                    first_square, second_square)
                #print('edge', edge,'inner_edge', inner_edge)
                edge.set_inner_edge(inner_edge)

    def assign_symbols(self):
        '''Optional, should assign an ASCII string for visualization.'''

        usg = UniqueStringGenerator()
        for n, sym in zip(self.iter_all_sorted(), usg):
            n.sym = sym

    def get_edge_by_coordinates(self, n1_key, n2_key):
        n1,n2 = self[n1_key], self[n2_key]
        node_set=frozenset([n1,n2])
        return self.edges[node_set]
    
    def all_paths(self):
        if self._all_paths is None:
            all_paths_filename=self.paths_filename() + '_all'
            self._all_paths = simplePickler(all_paths_filename)
        return self._all_paths
    
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
        
        if self.finalized:
            raise Exception('Already finalized!')
        self.finalized=True
        
        ldbg('Finalizing Grid')
        for n in self.iter_all():
            n.finalize()
        for e in self.edges.values():
            e.assign_default_state()
            
        # Build lists of Nodes that have particular rules, since this shouldn't change once set (I think)?
        if self.is_outer:
            # Path Nodes with "must-travel" hexagons
            self.must_travel_nodes = frozenset(
                {n.key() for n in self.values() if n.must_travel})
            
            self.must_travel_edges = frozenset(
                {frozenset([n.key() for n in e]) for e in self.edges.values() if e.must_travel})
            
            self.rule_color_nodes = frozenset(
                {n for n in self.inner_grid.values() if n.rule_color})
            self.rule_shape_nodes = frozenset(
                {n for n in self.inner_grid.values() if n.rule_shape})
            self.rule_sun_nodes = frozenset(
                {n for n in self.inner_grid.values() if n.sun_color})
            
    def prepare_for_partitioning(self):
        self.partitions = []
        self.reset()

    def reset(self):
        self.color_generator().reset()
        for n in self.values():
            n.reset_node()

    def load_paths(self, overwrite=False):
        if self.paths:
            if not overwrite:
                return
            print('Warning: self.paths already loaded')

        #raise Exception('self.paths already loaded')
        self.paths = self.all_paths().load()

    def add_path(self, new_path, to_obj=True, to_db=False):
        if to_obj:
            # TODO: make path a set based class with ordering
            # self.paths.add(new_path)
            
            self.paths.add(new_path)
            if not len(self.paths) % 10000:
                print(len(self.paths))
        if to_db:
            pass

    def generate_paths(self, overwrite=False):
        '''Traverse all possible Paths.

        TODO: Early dead-end detection?
        '''
        if self.all_paths().file_exists():
            if not overwrite:
                print('Skipping path generation...')
                return
            else:
                print('overwriting:', self.all_paths().pickle_filename())

        # TODO: make path a set based class with ordering (OrderedDict?)
        self.paths = set()
        #self.paths = []
        path = OrderedDict()
        entrance_nodes = [n for n in self.values() if n.is_entrance]

        for n in entrance_nodes:
            self.travel(n, path)

        print('Done! found:', len(self.paths), 'total paths')
        self.all_paths().dump(self.paths)

    def travel(self, n, path):
        ''' Depth-first traversal of all possible paths
        
        TODO: Name is too generic, need other traversal algorithms
        TODO: Path should be Edges not Nodes'''
        # A node cannot be entered twice
        if n.key() in path:
            return
        # Append the new node to the new path
        new_path = OrderedDict(path)
        new_path[n.key()] = None

        # Are we done yet?
        if n.is_exit:
            finalized_path = str(list(new_path))
            if finalized_path in self.paths:
                return
            self.add_path(finalized_path, to_obj=True, to_db=False)

            # TODO: Assumes that there's only 1 exit
            return

        # head on down the line...
        for nxt in n.traversable_nodes(auto_cut=False):
            self.travel(nxt, new_path)

    def set_current_path(self, path):

        # Restore all traversable links between Squares
        if self.current_path:
            self.unset_current_path()

        self.color_generator().reset()
        self.partitions = []

        self.current_path = []

        ''' Traverse the path, removing neighbors from Squares accordingly
         For each Segment in the Path (technically an edge between Outer Nodes)'''
        for i in range(len(path) - 1):
            nodes = [self[n] for n in path[i:i + 2]]
            # Sever the link between 2 Squares (unless on Graph border)
            cur_edge = self.get_edge(*nodes)
            #ldbg2('cur_edge', cur_edge)
            cur_edge.sever_inner()

            self.current_path.append(cur_edge)

    def unset_current_path(self):
        # Reconnect any Edges severed by partitioning
        for p in self.partitions:
            for e in p.edges.values():
                e.connect()

        # Reconnect all edges severed by the Path
        for e in self.current_path:
            e.reset_inner()

    '''
    TODO: Refactor find_any_xxx_violation functions into a wrapper?
        The only thing different right now is which Node set they iterate over,
        and which Partition function they call.
        
        My gut feeling is that this can be handled better with smarter polymorphism
        is the Node class. Maybe each Node reveals what it needs to be "happy"?
     '''

    def find_any_color_violation(self):

        cur_rule_color_nodes = set(self.rule_color_nodes)
        if not cur_rule_color_nodes:
            return False

        violation = False
        while cur_rule_color_nodes:

            n = cur_rule_color_nodes.pop()
            current_partition = self.retreive_partition(n)
            if not current_partition:
                raise Exception('Unable to find partition for ', n)
            violation = current_partition.has_color_violation()
            # TODO: probably no need to check for further violations, but
            # leaving in while working out bugs
            if violation:
                break
            # No need to recheck these nodes...
            for partition_node in current_partition.values():
                if partition_node in cur_rule_color_nodes:
                    cur_rule_color_nodes.remove(partition_node)
        return violation

    def find_any_shape_violation(self):

        rule_shape_nodes = set(self.rule_shape_nodes)
        if not rule_shape_nodes:
            return False

        while rule_shape_nodes:
            violation = False
            n = rule_shape_nodes.pop()
            current_partition = self.retreive_partition(n)
            if not current_partition:
                raise Exception('Unable to find partition for ', n)
            violation = current_partition.has_shape_violation()
            # TODO: probably no need to check for further violations, but
            # leaving in while working out bugs
            if violation:
                break
            # No need to recheck these nodes...
            for partition_node in current_partition.values():
                if partition_node in rule_shape_nodes:
                    rule_shape_nodes.remove(partition_node)

        return violation

    def find_any_sun_violation(self):

        rule_sun_nodes = set(self.rule_sun_nodes)

        if not rule_sun_nodes:
            return False

        violation = False

        while rule_sun_nodes:
            n = rule_sun_nodes.pop()
            current_partition = self.retreive_partition(n)
            if not current_partition:
                raise Exception('Unable to find partition for ', n)
            violation = current_partition.has_sun_violation()
            # TODO: probably no need to check for further violations, but
            # leaving in while working out bugs
            if violation:
                break
            # No need to recheck these nodes...
            # TODO: set difference
            for partition_node in current_partition.values():
                if partition_node in rule_sun_nodes:
                    rule_sun_nodes.remove(partition_node)

        return violation

    def generate_partition(self, n):
        '''Return the Partition that contains this GridSquare.
        
        PRE: The Partition belonging to n has NOT been generated.'''
        if not self.partitions:
            self.partitions = []
            self.real_partitions = []
        # Sanity check
        if any([n in p for p in self.partitions]):
            raise Exception('Partition already generated for: %s', n)
        p = Partition(n)
        self.partitions.append(p)

        return p

    def retreive_partition(self, n):
        # Find the partition that contains this Node (for now just GridSquares)
        found_partition = None

        found_partitions=[ p for p in self.partitions if n.key() in p ]
        if len(found_partitions) == 1:
            return found_partitions[0]
        elif not found_partitions:
            return self.generate_partition(n)
        else:
            raise Exception('Bad number of Partitions returned: %s', found_partitions)
        for p in self.partitions:
            if n.key() in p:
                found_partition = p

        if not found_partition:
            found_partition = self.generate_partition(n)

        if found_partition is None:
            raise Exception('Unable to find partition for', n)
        return found_partition


if __name__ == '__main__':
    
    rgg = RectGridGraph(10, 10, auto_assign_edges=False)
    rgg.finalize()
    print(rgg.render_both())
    
    
    for k, e in rgg.edges.items():
        print('e', e, e.state_str())
        if e.inner_edge:
            print('    e.inner_edge', e.inner_edge, e.inner_edge.state_str())

    