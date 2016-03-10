'''
Created on Feb 24, 2016

@author: charper
'''
import os
from lib.Graph import RectGridGraph
from lib.Geometry import MultiBlock
from lib.GraphImage import GraphImage
from lib.util import simplePickler, WastedCounter
import unittest
import cProfile
import pstats
import io
from _collections import deque


class PuzzleConfiguration(object):
    '''Contains info about a puzzle.

    Dimensions
    Entrance/Exit Nodes
    SquareModifiers
    '''

    def __init__(self):
        pass


class RectangleGridPuzzle(GraphImage):
    '''
    Models a rectangular (m*n) Grid puzzle. 

    Eventually most of this should be moved to the Puzzle base class.
    TODO: I don't want this to inherit from GraphImage. Should be able
    to solve Puzzles without the need for Image rendering (ie Pillow 
    library), text is enough.
    '''

    def __init__(self, gx, gy, puzzle_name):
        self.puzzle_name = puzzle_name
        super().__init__(gx, gy)

        self.filtered_paths_pickler = simplePickler(
            self.filtered_paths_filename())

    def filtered_paths_filename(self):
        return self.paths_filename() + '_filtered'

    def paths_filename(self):
        return '%s_%s' % (self.puzzle_name, super().paths_filename())
    
    def filter_paths(self, overwrite=False, expecting_filtered=False):
        '''filter paths to those containing segments bounding adjacent differing colors'''
        if not self.paths:
            self.load_paths()

        if self.filtered_paths_pickler.file_exists():
            if not overwrite:
                self.potential_paths = self.filtered_paths_pickler.load()
                print('Skipping filter_paths...')
                return
            else:
                print('Overwriting filter_paths...')
        
        # get a list of all boundaries between adjacent differing colors
        color_boundaries = frozenset(s.different_color_boundaries for s in self.inner_grid.values(
        ) if s.different_color_boundaries)
#         for s in self.inner_grid.values():
#             if s.different_color_boundaries:
#                 print('square',s,'different_color_boundaries',s.different_color_boundaries)
        print('color_boundaries',color_boundaries)
        self.potential_paths = []
        
        print('Attempting to filter:',len(self.paths),'total paths')
        
        # iterate over each path
        for path in self.paths:
            # for our purposes, path direction doesn't matter, only which segments (Node-Node) were traversed
            # if the path contains all of the segments we know MUST be
            # traversed, append it
            cb_copy=set(color_boundaries)
            for i in range(len(path)-1):
                seg=frozenset(path[i:i+2])
                if seg in cb_copy:
                    cb_copy.remove(seg)
                if len(cb_copy)==0:
                    self.potential_paths.append(path)
                    break
                    

        if not self.potential_paths and expecting_filtered:
            #print(sorted_path_segs)
            raise Exception('No filtered paths')

        print('Filtered', len(self.paths),
              'paths to', len(self.potential_paths))
        self.filtered_paths_pickler.dump(self.potential_paths)

    def solve(self, break_on_first=False):
        
        ''' Iterate over every potential path and check each GridSquare
        with a rule for violations. 
        '''
        # Auto-load paths if they have been previously generated
        if not self.paths:
            self.generate_paths()
        if not self.potential_paths:
            self.potential_paths = self.paths
            if not self.potential_paths:
                raise Exception('Unable to find any paths')

        print('Checking',len(self.potential_paths),'paths...')
        for p in self.potential_paths:
#             if frozenset(p)==set([(0, 1), (3, 2), (0, 0), (1, 3), (3, 3), (3, 0), (3, 1), (2, 1), (2, 0), (2, 3), (2, 2), (0, 3), (0, 2)]):
#                 print('foo')
#                 print('self.current_path', self.current_path)
#                 print('p', p)
#             self.render_solution('oops')
            #print('evaluating potential_path:', p)
            self.set_current_path(p)
#             if frozenset(p)==set([(0, 1), (3, 2), (0, 0), (1, 3), (3, 3), (3, 0), (3, 1), (2, 1), (2, 0), (2, 3), (2, 2), (0, 3), (0, 2)]):
# #                 for e in self.inner_grid.edges.values():
# #                     print('con',e.short_str())
#                 print('self.current_path', self.current_path)
            
            # Innocent until proven guilty ;)
            solution = True

            if self.find_any_shape_violation():
                solution = False

            # TODO: Wrap in find_any_color_violation()
            # Should use Partition class to count distinct rule_colors during creation
            # sloppy to check every Node with rule color...
            for n in self.inner_grid.values():                
                if n.has_rule_color:
                    if self.check_colors(n, n.rule_color):
                        solution = False
                        break

            if solution:
                self.solutions.append(p)
                print('Found solution!', p)
                #self.render_solution()
                if break_on_first:
                    break
            #self.render_solution()
            #exit(0)
        print('Found', len(self.solutions), 'total solutions!')


class Test(unittest.TestCase):
    def setUp(self):
        """init each test"""
        
        self.pr = cProfile.Profile()
        self.pr.enable()
        print( "\n<<<---")
    
    def tearDown(self):
        """finish any test"""
        p = pstats.Stats (self.pr)
        p.strip_dirs()
        p.sort_stats ('cumtime')
        p.print_stats ()
        print('Wasted:', WastedCounter.get())
        #print "\n--->>>"
    def test2Ishapes(self):
        '''c d e f
            m n o
           8 9 a b
            j k l
           4 5 6 7
            g h i
           0 1 2 3'''
        # 4x4 Grid with a 3-block "I" shape in the center and one on the left
        g = RectangleGridPuzzle(4, 4, 'Ishape3test')
        Ishape3 = MultiBlock([(0, 0), (0, 1), (0, 2)], 'Ishape3')

        g.inner_grid[1, 1].set_rule_shape(Ishape3)
        g.inner_grid[0, 0].set_rule_shape(Ishape3)
        g.lower_left().is_entrance = True
        g.upper_right().is_exit = True
        g.finalize()
        g.generate_paths()
        g.load_paths()
        g.solve()
        print('g.solutions', g.solutions)
        exp_sols=[[(0,0), (0,1), (0,2), (0,3), (1,3), (1,2), (1,1), (1,0), (2,0), (2,1), (2,2), (2,3), (3,3)], [(0,0), (0,1), (0,2), (0,3), (1,3), (2,3), (2,2), (2,1), (2,0), (3,0), (3,1), (3,2), (3,3)], [(0,0), (1,0), (1,1), (1,2), (1,3), (2,3), (2,2), (2,1), (2,0), (3,0), (3,1), (3,2), (3,3)], [(0,0), (1,0), (2,0), (2,1), (2,2), (2,3), (3,3)]]
        exp_sols=set(frozenset(p) for p in exp_sols)
        actual_sols=set(frozenset(p) for p in g.solutions)
        missing_sol = exp_sols - actual_sols
        extra_solutions = actual_sols - exp_sols
        self.assertTrue(len(missing_sol)==0, 'Missing solutions:'+','.join(str(s) for s in missing_sol))
        self.assertTrue(len(extra_solutions)==0, 'Extra solutions:'+','.join(str(s) for s in extra_solutions))
        self.assertEqual(len(g.solutions), 4, g.solutions)
        #frozenset({(0, 1), (3, 2), (0, 0), (1, 3), (3, 3), (3, 0), (3, 1), (2, 1), (2, 0), (2, 3), (2, 2), (0, 3), (0, 2)})
    def testColor0(self):
        '''-------------------
        o p q r s t
         J K L M N
        i j k l m n
         E F G H I
        c d e f g h
         z A B C D
        6 7 8 9 a b
         u v w x y
        0 1 2 3 4 5
        ********************
        '''
        # Color Puzzle 1
        cp1 = RectangleGridPuzzle(6, 5, 'bunker_first_room_last_panel')
        # Initialize the entrance/exit Nodes
        cp1.lower_left().is_entrance = True
        cp1.upper_right().is_exit = True
 
        # Initialize the colored Squares
        square_grid = cp1.inner_grid
 
        square_grid[0, 1].set_rule_color('aqua')
        square_grid[0, 2].set_rule_color('aqua')
        square_grid[0, 3].set_rule_color('aqua')
 
        square_grid[1, 3].set_rule_color('white')
        square_grid[2, 3].set_rule_color('white')
        square_grid[3, 0].set_rule_color('white')
        square_grid[4, 0].set_rule_color('white')
 
        square_grid[2, 1].set_rule_color('red')
        square_grid[2, 2].set_rule_color('red')
 
        square_grid[4, 1].set_rule_color('yellow')
        square_grid[4, 2].set_rule_color('yellow')
        square_grid[4, 3].set_rule_color('yellow')
         
        cp1.finalize()
        override = False
        # Generate all possible paths
        cp1.generate_paths(override)
        # Filter paths (if possible)
        cp1.filter_paths(override, expecting_filtered=True)
        # Solve but do NOT break on first solution to make sure we don't find
        # multiples
        print(cp1.render_both())
        cp1.solve(False)
        expected_solution = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 4), (1, 3), (1, 2), (1, 1), (1, 0), (2, 0), (2, 1), (
            2, 2), (2, 3), (3, 3), (3, 2), (3, 1), (3, 0), (4, 0), (5, 0), (5, 1), (4, 1), (4, 2), (4, 3), (4, 4), (5, 4)]
        self.assertEqual(len(cp1.solutions), 1, 'Too many solutions:\n%s' % (
            '\n'.join([''.join(str(s)) for s in cp1.solutions])))
        sol = cp1.solutions[0]
        self.assertEqual(
            list(sol), expected_solution, 'Unexpected solution:\n%s' % (str(sol)))
        self.assertEqual(len(cp1.paths), 79384, 'path number')
        #cp1.render()

    def testShape0(self):
        pass

    # TODO: Path generation will take forever, need to work on early dead-end detection
    def xtest10x10(self):
        g = RectGridGraph(10, 10)
        g.lower_left().is_entrance = True
        g.upper_right().is_exit = True
        g.generate_paths()
        print(g.render_both())


def pass_print(*args):
    pass

if __name__ == '__main__':
    t=Test()
    
    t.setUp()
    t.test2Ishapes()
    t.testColor0()
    t.tearDown()
    #unittest.main()
  
    exit(0)
    # 4x4 Grid with a "T" shape and two singles
    g = RectangleGridPuzzle(5, 5, 'Tblock2Singles')

    '''  X
        XXX '''
    TshapeUp = MultiBlock([(0, 0), (1, 0), (2, 0), (1, 1)], 'TshapeUp')
    ''' XXX
         X  '''
    TshapeDown = MultiBlock([(0, 1), (1, 1), (2, 1), (1, 0)], 'TshapeDown')
    '''  X
        XX 
         X'''
    TshapeLeft = MultiBlock([(0, 1), (1, 0), (1, 1), (1, 2)], 'TshapeLeft')
    '''  X
         XX 
         X    '''
    TshapeRight = MultiBlock([(0, 0), (0, 1), (0, 2), (1, 1)], 'TshapeRight')
    Single0 = MultiBlock([(0, 1)], 'Single0')
    Single1 = MultiBlock([(0, 2)], 'Single1')
    Ishape3Vert = MultiBlock([(0, 0), (0, 1), (0, 2)], 'Ishape3Vert')
    g.inner_grid[0, 0].set_rule_shape(TshapeUp)
    g.inner_grid[1, 3].set_rule_shape(TshapeDown)
    #g.inner_grid[1, 0].set_rule_shape(Single0)
    #g.inner_grid[2, 0].set_rule_shape(Ishape3Vert)
    g.inner_grid[3, 1].set_rule_shape(TshapeLeft)
    
    g.lower_left().is_entrance = True
    g.upper_right().is_exit = True
    g.generate_paths()
    g.load_paths()
    g.solve()

    exit(0)
    # 4x4 Grid with a "T" shape
    g = RectangleGridPuzzle(5, 5, 'Tblock')
    Ishape3Vert = MultiBlock([(0, 0), (0, 1), (0, 2)], 'Ishape3Vert')
    Tblock = MultiBlock([(0, 1), (1, 1), (2, 1), (1, 0)], 'Tblock')

    # g.inner_grid[1,1].set_rule_shape(Ishape3)
    g.inner_grid[1, 2].set_rule_shape(Tblock)
    g.lower_left().is_entrance = True
    g.upper_right().is_exit = True
    g.generate_paths()
    g.load_paths()
    g.solve()

    exit(0)
    unittest.main()
    # g.render()
    #for p in g.partitions: print(p)
    exit(0)

    # Shape test
    g = RectangleGridPuzzle(6, 5, 'shape0')
    # Initialize the entrance/exit Nodes
    g.lower_left().is_entrance = True
    g.upper_right().is_exit = True

    g.generate_paths(True)
    g.load_paths()
    for i in range(1):
        p = g.paths[i + 10000]
        g.set_current_path(p)
        g.generate_all_partitions()
        g.render()

    # print(g.render_both())
    print(len(g.paths))

