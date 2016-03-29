import cProfile

import glob
import os
import unittest
import pstats
import io


from lib.Geometry import MultiBlock
from lib.GraphImage import chImg
from lib.RectangleGridPuzzle import RectangleGridPuzzle
from lib.util import simplePickler, WastedCounter, defaultValueServer
from ast import literal_eval


class Test(unittest.TestCase):

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
        Ishape3_1 = MultiBlock([(0, 0), (0, 1), (0, 2)], 'Ishape3_1')
        Ishape3_2 = MultiBlock([(0, 0), (0, 1), (0, 2)], 'Ishape3_2')

        g.inner_grid[1, 1].set_rule_shape(Ishape3_1)
        g.inner_grid[0, 0].set_rule_shape(Ishape3_2)
        g.lower_left().is_entrance = True
        g.upper_right().is_exit = True
        g.finalize()
        g.generate_paths()
        g.load_paths()
        g.solve()
        print('g.solutions', g.solutions)
        expected_solutions = [[(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (1, 2), (1, 1), (1, 0), (2, 0), (2, 1), (2, 2), (2, 3), (3, 3)], [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (2, 3), (2, 2), (2, 1), (2, 0), (
            3, 0), (3, 1), (3, 2), (3, 3)], [(0, 0), (1, 0), (1, 1), (1, 2), (1, 3), (2, 3), (2, 2), (2, 1), (2, 0), (3, 0), (3, 1), (3, 2), (3, 3)], [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (2, 3), (3, 3)]]
        expected_solutions = set(frozenset(p) for p in expected_solutions)
        # print('expected_solutions:',len(expected_solutions))
        actual_sols = set(frozenset(p) for p in g.solutions)
        missing_solutions = expected_solutions - actual_sols
        extra_solutions = actual_sols - expected_solutions
        self.assertTrue(len(missing_solutions) == 0,
                        'Missing solutions:' + ','.join(str(s) for s in missing_solutions))
        self.assertTrue(len(extra_solutions) == 0,
                        'Extra solutions:' + ','.join(str(s) for s in extra_solutions))
        self.assertEqual(len(g.solutions), 4, g.solutions)
        #frozenset({(0, 1), (3, 2), (0, 0), (1, 3), (3, 3), (3, 0), (3, 1), (2, 1), (2, 0), (2, 3), (2, 2), (0, 3), (0, 2)})

    def testBunker8(self, overwrite=False):
        '''o p q r s t
            J K L M N
           i j k l m n
            E F G H I
           c d e f g h
            z A B C D
           6 7 8 9 a b
            u v w x y
           0 1 2 3 4 5 
           
           uvwx CBA FEJK pq LM HI up'''
        # Color Puzzle 1
        cp1 = RectangleGridPuzzle(6, 5, 'testBunker8')
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
        cp1.render()
        # Generate all possible paths
        cp1.generate_paths(overwrite)
        # Filter paths (if possible)
        cp1.filter_paths_colors_only(overwrite, expecting_filtered=True)
        # Solve but do NOT break on first first_solution to make sure we don't find
        # multiples
        print(cp1.render_both())
        cp1.solve(False)
        actual_solutions = cp1.solutions

        expected_solution = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 4), (1, 3), (1, 2), (1, 1), (1, 0), (2, 0), (2, 1), (
            2, 2), (2, 3), (3, 3), (3, 2), (3, 1), (3, 0), (4, 0), (5, 0), (5, 1), (4, 1), (4, 2), (4, 3), (4, 4), (5, 4)]

        first_solution = actual_solutions[0]
        self.assertEqual(
            list(first_solution), expected_solution, 'Unexpected first_solution:\n%s' % (str(first_solution)))
        self.assertEqual(len(actual_solutions), 1, 'Wrong number of solutions:%s' % (
            '\n'.join([''.join(str(s)) for s in actual_solutions])))
        self.assertEqual(len(cp1.paths), 79384, 'path number')

    def testBunker6(self, overwrite=False):
     
        # Color Puzzle 1
        cp1 = RectangleGridPuzzle(5, 5, 'testBunker6')
        # Initialize the entrance/exit Nodes
        cp1.lower_left().is_entrance = True
        cp1.upper_right().is_exit = True

        # Initialize the colored Squares
        square_grid = cp1.inner_grid

        square_grid[0, 0].set_rule_color('aqua')
        square_grid[0, 3].set_rule_color('aqua')
        
        square_grid[1, 1].set_rule_color('yellow')
        square_grid[1, 2].set_rule_color('yellow')
        
        square_grid[2, 1].set_rule_color('antiquewhite')
        square_grid[2, 2].set_rule_color('antiquewhite')

        square_grid[3, 0].set_rule_color('red')
        square_grid[3, 3].set_rule_color('red')

        cp1.finalize()
        cp1.render()
        # Generate all possible paths
        cp1.generate_paths(overwrite)
        # Filter paths (if possible)
        cp1.filter_paths_colors_only(overwrite, expecting_filtered=True)
        # Solve but do NOT break on first first_solution to make sure we don't find
        # multiples
        print(cp1.render_both())
        cp1.solve(False)
        
        
    def testMultipleShapesInPartition(self):
        g = RectangleGridPuzzle(5, 5, 'MultipleShapesInPartition')

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
        TshapeRight = MultiBlock(
            [(0, 0), (0, 1), (0, 2), (1, 1)], 'TshapeRight')
        Single0 = MultiBlock([(0, 1)], 'Single0')
        Single1 = MultiBlock([(0, 2)], 'Single1')
        Ishape3Vert = MultiBlock([(0, 0), (0, 1), (0, 2)], 'Ishape3Vert')

# Alternate arrangement
#         [(0,0), (0,1), (1,1), (1,2), (2,2), (2,3), (1,3), (1,4), (2,4), (3,4), (4,4)]: # MultipleShapes soution
#         g.inner_grid[0, 0].set_rule_shape(TshapeUp)
#         g.inner_grid[1, 3].set_rule_shape(TshapeDown)
#         g.inner_grid[3, 1].set_rule_shape(TshapeLeft)

        g.inner_grid[0, 0].set_rule_shape(TshapeRight)
        g.inner_grid[1, 3].set_rule_shape(TshapeDown)
        g.inner_grid[3, 1].set_rule_shape(TshapeLeft)
        g.lower_left().is_entrance = True
        g.upper_right().is_exit = True
        g.generate_paths()
        g.load_paths()
        g.solve()
        self.assertEqual(len(g.solutions), 1, 'Wrong number of solutions: %s' % (
            '\n'.join([''.join(str(s)) for s in g.solutions])))
        actual_solution = g.solutions[0]

        expected_solution = [
            (0, 0), (1, 0), (1, 1), (2, 1), (2, 2), (3, 2), (3, 1), (4, 1), (4, 2), (4, 3), (4, 4)]

        self.assertEqual(
            list(actual_solution), expected_solution, 'Unexpected solution:\n%s' % (str(actual_solution)))

    def testSinglePartition(self):
        g = RectangleGridPuzzle(3, 4, 'testSinglePartition')
        Ishape3Vert = MultiBlock([(0, 0), (0, 1), (0, 2)], 'Ishape3Vert')
        Ishape2Vert = MultiBlock([(0, 0), (0, 1)], 'Ishape2Vert')
        #Ishape3Vert = MultiBlock([(0, 0), (0, 1), (0, 2)], 'Ishape3Vert')
        g.inner_grid[1, 2].set_rule_shape(Ishape2Vert)
        g.inner_grid[1, 1].set_rule_shape(Ishape3Vert)
        g.lower_left().is_entrance = True
        g.upper_right().is_exit = True
        g.generate_paths()
        g.load_paths()
        g.solve()
        for p in g.partitions:
            print('Real Partition', p)

    def testRotationShapes(self):
        ''' Put a rotatable TshapeUp in a 3x4 Grid (2x3 Squares) with 2 Singles.
            SS
            SS     T
            SS    TTT
            It would not fit normally, but if rotated on it's side it could        '''

        g = RectangleGridPuzzle(4, 5, 'testRotationShapes')

        '''  X
            XXX '''
        TshapeUp = MultiBlock(
            [(0, 0), (1, 0), (2, 0), (1, 1)], name='TshapeUp', can_rotate=True)
        TshapeDown = MultiBlock(
            [(0, 1), (1, 1), (2, 1), (1, 0)], 'TshapeDown', can_rotate=False)
#         Single0 = MultiBlock([(0, 1)], 'Single0')
#         Single1 = MultiBlock([(0, 2)], 'Single1')
        ''' X
            X'''
        IshapeHoriz2 = MultiBlock([(0, 0), (1, 0)])
        #Ishape3Vert = MultiBlock([(0, 0), (0, 1), (0, 2)], 'Ishape3Vert')

        g.inner_grid[2, 3].set_rule_shape(TshapeUp)
        g.inner_grid[1, 1].set_rule_shape(TshapeDown)

        g.inner_grid[0, 3].set_rule_shape(IshapeHoriz2)

        g.lower_left().is_entrance = True
        g.upper_right().is_exit = True
        g.finalize()
        g.render()
        g.generate_paths()
        g.load_paths()
        g.solve()

        expected_solutions = [[(0, 0), (0, 1), (1, 1), (1, 2), (1, 3), (0, 3), (0, 4), (1, 4), (2, 4), (3, 4)], [
            (0, 0), (1, 0), (2, 0), (3, 0), (3, 1), (2, 1), (2, 2), (2, 3), (3, 3), (3, 4)]]
        expected_solutions = set(frozenset(p) for p in expected_solutions)
        # print('expected_solutions:',len(expected_solutions))
        actual_solutions = set(frozenset(p) for p in g.solutions)
        missing_solutions = expected_solutions - actual_solutions
        extra_solutions = actual_solutions - expected_solutions
        self.assertTrue(len(missing_solutions) == 0,
                        'Missing solutions:' + ','.join(str(s) for s in missing_solutions))
        self.assertTrue(len(extra_solutions) == 0,
                        'Extra solutions:' + ','.join(str(s) for s in extra_solutions))

    def testTreehouse0(self):

            # 4x4 Grid with a 3-block "I" shape in the center and one on the
            # left
        g = RectangleGridPuzzle(6, 6, 'testTreehouse0')
        Ishape2Vert = MultiBlock([(0, 0), (0, 1)], 'Ishape2Vert')
        '''   X
                XXX'''
        LshapeUpRight = MultiBlock(
            [(0, 0), (1, 0), (2, 0), (2, 1)], name='LshapeUpRight', can_rotate=True)
        ''' X  
                XXX'''
        LshapeUpLeft = MultiBlock(
            [(0, 0), (1, 0), (2, 0), (0, 1)], name='LshapeUpLeft', can_rotate=True)

        g.inner_grid[3, 0].set_rule_shape(Ishape2Vert)
        g.inner_grid[1, 1].set_rule_shape(LshapeUpRight)
        g.inner_grid[3, 2].set_rule_shape(LshapeUpLeft)

        g.inner_grid[4, 0].sun_color = 'purple'
        g.inner_grid[0, 3].sun_color = 'purple'

        g.inner_grid[4, 2].sun_color = 'green'
        g.inner_grid[1, 4].sun_color = 'green'

        g[2, 0].is_entrance = True
        g[3, 0].is_entrance = True

        g[2, 5].is_exit = True
        g[3, 5].is_exit = True

        g.finalize()

        # These took forever to generate. Think carefully before overwriting...
        overwrite_treehouse_paths = False
        g.generate_paths(overwrite_treehouse_paths)
        g.load_paths()
        g.solve(break_on_first=True)
        print('g.solutions', g.solutions)
        #exp_sols=[[(0,0), (0,1), (0,2), (0,3), (1,3), (1,2), (1,1), (1,0), (2,0), (2,1), (2,2), (2,3), (3,3)], [(0,0), (0,1), (0,2), (0,3), (1,3), (2,3), (2,2), (2,1), (2,0), (3,0), (3,1), (3,2), (3,3)], [(0,0), (1,0), (1,1), (1,2), (1,3), (2,3), (2,2), (2,1), (2,0), (3,0), (3,1), (3,2), (3,3)], [(0,0), (1,0), (2,0), (2,1), (2,2), (2,3), (3,3)]]
        #exp_sols=set(frozenset(p) for p in exp_sols)

        first_solution = g.solutions[0]
        self.assertIsNotNone(first_solution)
        #frozenset({(0, 1), (3, 2), (0, 0), (1, 3), (3, 3), (3, 0), (3, 1), (2, 1), (2, 0), (2, 3), (2, 2), (0, 3), (0, 2)})

    def testMoveableShapes(self):
        '''Same as testRuleShapeRendering with a different layout'''

        g = RectangleGridPuzzle(5, 5, 'testMoveableShapes')

        TshapeDown = MultiBlock(
            [(0, 1), (1, 1), (2, 1), (1, 0)], 'TshapeDown', can_rotate=False)
        TshapeRight = MultiBlock(
            [(0, 0), (0, 1), (0, 2), (1, 1)], 'TshapeRight')
        TshapeLeft = MultiBlock([(0, 1), (1, 0), (1, 1), (1, 2)], 'TshapeLeft')
        #Ishape3Vert = MultiBlock([(0, 0), (0, 1), (0, 2)], 'Ishape3Vert')

        g.inner_grid[1, 3].set_rule_shape(TshapeRight)
        g.inner_grid[0, 0].set_rule_shape(TshapeDown)
        g.inner_grid[3, 1].set_rule_shape(TshapeLeft)

        g.lower_left().is_entrance = True
        g.upper_right().is_exit = True
        g.finalize()
        g.render()
        g.generate_paths()
        g.load_paths()
        g.solve()

        expected_solutions = [
            [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2), (3, 2), (3, 1), (4, 1), (4, 2), (4, 3), (4, 4)]]
        expected_solutions = set(frozenset(p) for p in expected_solutions)

        print('expected_solutions:', expected_solutions)
        actual_solutions = set(frozenset(p) for p in g.solutions)
        print('actual_solutions', actual_solutions)
        missing_solutions = expected_solutions - actual_solutions
        extra_solutions = actual_solutions - expected_solutions
        self.assertTrue(len(missing_solutions) == 0,
                        'Missing solutions:' + ','.join(str(s) for s in missing_solutions))
        self.assertTrue(len(extra_solutions) == 0,
                        'Extra solutions:' + ','.join(str(s) for s in extra_solutions))

    def testRuleShapeRendering(self):
        ''' Put 3 Tshapes in a 5x5 Grid to demo rules_shape rendering.'''

        g = RectangleGridPuzzle(5, 5, 'testRuleShapeRendering')

        TshapeDown = MultiBlock(
            [(0, 1), (1, 1), (2, 1), (1, 0)], 'TshapeDown', can_rotate=False)
        TshapeRight = MultiBlock(
            [(0, 0), (0, 1), (0, 2), (1, 1)], 'TshapeRight')
        TshapeLeft = MultiBlock([(0, 1), (1, 0), (1, 1), (1, 2)], 'TshapeLeft')
        #Ishape3Vert = MultiBlock([(0, 0), (0, 1), (0, 2)], 'Ishape3Vert')

        g.inner_grid[1, 3].set_rule_shape(TshapeDown)
        g.inner_grid[0, 0].set_rule_shape(TshapeRight)
        g.inner_grid[3, 1].set_rule_shape(TshapeLeft)

        g.finalize()
        g.lower_left().is_entrance = True
        g.upper_right().is_exit = True
        g.render()
        g.generate_paths()
        g.load_paths()
        g.solve()

        expected_solutions = [
            [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2), (3, 2), (3, 1), (4, 1), (4, 2), (4, 3), (4, 4)]]
        expected_solutions = set(frozenset(p) for p in expected_solutions)

        print('expected_solutions:', expected_solutions)
        actual_solutions = set(frozenset(p) for p in g.solutions)
        print('actual_solutions', actual_solutions)
        missing_solutions = expected_solutions - actual_solutions
        extra_solutions = actual_solutions - expected_solutions
        self.assertTrue(len(missing_solutions) == 0,
                        'Missing solutions:' + ','.join(str(s) for s in missing_solutions))
        self.assertTrue(len(extra_solutions) == 0,
                        'Extra solutions:' + ','.join(str(s) for s in extra_solutions))

    def testVillageYellowDoorWindow(self):
        '''The puzzle on a door with a yellow window. 

        Once, opened looking through yellow window allows true colors
        of testVillageSunDoor to be solved '''
        g = RectangleGridPuzzle(6, 6, 'testVillageYellowDoorWindow')

        for i in range(5):
            # Top row all have Lshapes
            shape = MultiBlock(
                [(0, 0), (1, 0), (0, 1)], 'Lshape3_' + str(i), can_rotate=True)
            g.inner_grid[i, 4].set_rule_shape(shape)
            # Bottom row all have purple suns
            g.inner_grid[i, 0].sun_color = 'purple'

        # Last purple sun in middle
        g.inner_grid[2, 2].sun_color = 'purple'

        g.lower_left().is_entrance = True
        g.upper_right().is_exit = True

        g.finalize()
        g.render()
        g.generate_paths()
        g.load_paths()
        g.solve()

        # expected_solutions=[]
        #expected_solutions=set(frozenset(p) for p in expected_solutions)
#         print('expected_solutions:',expected_solutions)
#         actual_solutions=set(frozenset(p) for p in g.solutions)
#         print('actual_solutions', actual_solutions)
#         missing_solutions = expected_solutions - actual_solutions
#         extra_solutions = actual_solutions - expected_solutions
#         self.assertTrue(len(missing_solutions)==0, 'Missing solutions:'+','.join(str(s) for s in missing_solutions))
#         self.assertTrue(len(extra_solutions)==0, 'Extra solutions:'+','.join(str(s) for s in extra_solutions))
    def testVillageSunDoor(self):
        '''After solving testVillageYellowDoorWindow, look through window to see true
        colors of all the suns in this puzzle '''
        g = RectangleGridPuzzle(5, 5, 'testVillageSunDoor')

        for i in range(4):
            # Top row all white
            g.inner_grid[i, 3].set_rule_sun('white')
            # Bottom row all red
            g.inner_grid[i, 0].set_rule_sun('red')

        g.inner_grid[0, 2].set_rule_sun('white')
        g.inner_grid[1, 2].set_rule_sun('white')

        g.inner_grid[0, 1].set_rule_sun('black')
        g.inner_grid[1, 1].set_rule_sun('black')
        g.inner_grid[2, 1].set_rule_sun('black')
        g.inner_grid[2, 2].set_rule_sun('black')

        g.inner_grid[3, 1].set_rule_sun('red')
        g.inner_grid[3, 2].set_rule_sun('red')

        g.lower_left().is_entrance = True
        g.upper_right().is_exit = True

        g.finalize()
        g.render()
        g.generate_paths()

        g.load_paths()
        force_paths = [
            '[(0, 0), (0, 1), (1, 1), (2, 1), (3, 1), (3, 2), (4, 2), (4, 3), (3, 3), (2, 3), (2, 2), (1, 2), (0, 2), (0, 3), (0, 4), (1, 4), (2, 4), (3, 4), (4, 4)]']
        g.solve(force_paths=None)

    def testVillageVentWall0(self):
        '''1 Rotatable Tshape, hexagon "must-travel" dots at all Path Nodes'''

        g = RectangleGridPuzzle(5, 5, 'testVillageVentWall0')

        TshapeUp = MultiBlock(
            [(0, 0), (1, 0), (2, 0), (1, 1)], name='TshapeUp', can_rotate=True)
        
        g.inner_grid[0, 1].set_rule_shape(TshapeUp)
        
        g.lower_left().is_entrance = True
        g.upper_right().is_exit = True

        g.finalize()
        g.render()
        
        g.generate_paths()
        g.load_paths()
        
        # Filter paths to those containing ALL path nodes (fill up the Grid)
        #paths_hack=[literal_eval(p) for p in g.paths]
        g.potential_paths=[p for p in g.paths if len(literal_eval(p))==g.gx*g.gy]
        g.solve()
        
    def testVillageVentWall1(self):
        '''1 Rotatable Tshape, on Single, hexagon "must-travel" dots at all Path Nodes'''

        g = RectangleGridPuzzle(5, 5, 'testVillageVentWall1')

        TshapeUp = MultiBlock(
            [(0, 0), (1, 0), (2, 0), (1, 1)], name='TshapeUp', can_rotate=True)
        Single0 = MultiBlock([(0, 0)], name='Single0')

        g.inner_grid[0, 1].set_rule_shape(TshapeUp)
        g.inner_grid[1, 1].set_rule_shape(Single0)
        
        g.lower_left().is_entrance = True
        g.upper_right().is_exit = True

        g.finalize()
        g.render()
        
        g.generate_paths()
        g.load_paths()
        
        # Filter paths to those containing ALL path nodes (fill up the Grid)
        #paths_hack=[literal_eval(p) for p in g.paths]
        g.potential_paths=[p for p in g.paths if len(literal_eval(p))==g.gx*g.gy]
        g.solve()
    
    def testVillageVentWall2(self):
        '''NOTE: Same as above with 1 extra single
        1 Rotatable Tshape, TWO Singles, hexagon "must-travel" dots at all Path Nodes'''

        g = RectangleGridPuzzle(5, 5, 'testVillageVentWall2')

        TshapeUp = MultiBlock(
            [(0, 0), (1, 0), (2, 0), (1, 1)], name='TshapeUp', can_rotate=True)
        Single0 = MultiBlock([(0, 0)], name='Single0')
        Single1 = MultiBlock([(0, 0)], name='Single1')

        g.inner_grid[0, 1].set_rule_shape(TshapeUp)
        g.inner_grid[1, 1].set_rule_shape(Single0)
        g.inner_grid[1, 0].set_rule_shape(Single1)
        
        g.lower_left().is_entrance = True
        g.upper_right().is_exit = True

        g.finalize()
        g.render()
        
        g.generate_paths()
        g.load_paths()
        
        # Filter paths to those containing ALL path nodes (fill up the Grid)
        #paths_hack=[literal_eval(p) for p in g.paths]
        g.potential_paths=[p for p in g.paths if len(literal_eval(p))==g.gx*g.gy]
        g.solve()

    def testVillageVentWall3(self):
        '''NOTE: Same as testVillageVentWall1 with two Tshapes instead of a single
        1 Rotatable Tshape, TWO Singles, hexagon "must-travel" dots at all Path Nodes'''

        g = RectangleGridPuzzle(5, 5, 'testVillageVentWall3')

        TshapeUp0 = MultiBlock(
            [(0, 0), (1, 0), (2, 0), (1, 1)], name='TshapeUp0', can_rotate=True)
        TshapeUp1 = MultiBlock(
            [(0, 0), (1, 0), (2, 0), (1, 1)], name='TshapeUp1', can_rotate=True)
        
        

        g.inner_grid[0, 1].set_rule_shape(TshapeUp0)
        g.inner_grid[1, 1].set_rule_shape(TshapeUp1)
        
        
        g.lower_left().is_entrance = True
        g.upper_right().is_exit = True

        g.finalize()
        g.render()
        
        g.generate_paths()
        g.load_paths()
        
        # Filter paths to those containing ALL path nodes (fill up the Grid)
        #paths_hack=[literal_eval(p) for p in g.paths]
        g.potential_paths=[p for p in g.paths if len(literal_eval(p))==g.gx*g.gy]
        g.solve()

    def testVillageVentWall4(self):
        '''NOTE: similar to previous with 2 Ishape3 blocks
        '''

        g = RectangleGridPuzzle(5, 5, 'testVillageVentWall4')

        Ishape3_0 = MultiBlock(
            [(0, 0), (0, 1), (0, 2)], name='Ishape3_0', can_rotate=True)
        Ishape3_1 = MultiBlock(
            [(0, 0), (0, 1), (0, 2)], name='Ishape3_1', can_rotate=True)
        
        

        g.inner_grid[0, 2].set_rule_shape(Ishape3_0)
        g.inner_grid[3, 2].set_rule_shape(Ishape3_1)
        
        
        g.lower_left().is_entrance = True
        g.upper_right().is_exit = True

        g.finalize()
        g.render()
        
        g.generate_paths()
        g.load_paths()
        
        # Filter paths to those containing ALL path nodes (fill up the Grid)
        #paths_hack=[literal_eval(p) for p in g.paths]
        g.potential_paths=[p for p in g.paths if len(literal_eval(p))==g.gx*g.gy]
        g.solve()
    def setUp(self, enable_profiler=True, clear_img_directory=True):
        self.enable_profiler = enable_profiler
        if self.enable_profiler:
            self.pr = cProfile.Profile()
            self.pr.enable()

        # Remove all images
        if clear_img_directory:
            d, e = defaultValueServer.get_directory_extension_pair('image')
            search_pattern = os.path.join(d, '*' + e)
            r = glob.glob(search_pattern)
            for f in r:
                #print (f)
                os.remove(f)

    def tearDown(self):
        if self.enable_profiler:
            s = io.StringIO()
            p = pstats.Stats(self.pr, stream=s)
            p.strip_dirs()
            p.sort_stats('tottime')
            p.print_stats()
            stats_output = [l for l in s.getvalue().split('\n') if l]

            for l in stats_output[2:20]:
                print(l)
            for l in stats_output[0:3]:
                print(l)

        if WastedCounter.get() > 1:
            print('Wasted:', WastedCounter.get())


def pass_print(*args):
    pass


def test_singles():
    t = Test()

    t.setUp(enable_profiler=True)

    
    t.testBunker8()
    t.testBunker6()

    #t.test2Ishapes()
#    t.testMultipleShapesInPartition()
    #t.testRotationShapes()
#     t.testSinglePartition()
#
#     t.testTreehouse0()

    #t.testRuleShapeRendering()
    #t.testMoveableShapes()

    #t.testVillageYellowDoorWindow()
    #t.testVillageSunDoor()
    
#     t.testVillageVentWall0()
#     t.testVillageVentWall1()
    #t.testVillageVentWall2()
#     t.testVillageVentWall3()
#     t.testVillageVentWall4()
    
    t.tearDown()

def test_all():
    unittest.main()

if __name__ == '__main__':

    
    test_singles()
    #test_all()


