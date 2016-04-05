'''
Created on Apr 2, 2016

@author: charper
'''
import os
import glob
import unittest
import shutil

from lib.util import defaultValueServer

from lib.RectangleGridPuzzle import RectangleGridPuzzle

class PuzzleTest(unittest.TestCase):

    def __init__(self, definition_function):
        ''' definition_function should return a dictionary of test attributes '''
        unittest.TestCase.__init__(self)
        
        self.puzzle_grid=None
        self.puzzle_dimensions=None
        self.puzzle_name=None
        self.description=None
        
        self.node_to_rule_map = dict()
        
        self.entrance_exit_node_map = []
        self.path_edges_to_sever = []
        
        self.must_travel_nodes = []
        self.must_travel_edges = []
        self.overwrite_all_paths=None
        self.force_check_all_paths=None
        self.overwrite_filtered_paths=None
        self.expecting_filtered_paths=None
        self.break_on_first_solution=None
        self.render_all_attempts=None
        
        self.force_paths = []
        self.expected_solutions = []
        self.generated_solutions = []
        self.missing_solutions = []
        self.extra_solutions = []
        
        self.copy_to_examples = None
        self.copy_to_solutions = None
        
        
        # Here's where the magic happens ;)
        self.definition_function=definition_function
        
    def setUp(self):
        # Get my list of attributes from the puzzle_definitions function
        self.puzzle_name=self.definition_function.__name__
        self.puzzle_description=self.definition_function.__doc__
        
        attrs=self.definition_function()
        for k, v in attrs.items():
            print(k,v)
            self.__dict__[k]=v
            
        # Initialize the Grid
        self.puzzle_grid = RectangleGridPuzzle(*self.puzzle_dimensions, self.puzzle_name)
        
        # TODO: Hack until Path is used
        self.expected_solutions = set(frozenset(p) for p in self.expected_solutions)
        
        # Setup entrance/exit Nodes
        og = self.puzzle_grid # But is this the REAL og?
        for node_key, val in self.entrance_exit_node_map.items():
            node=og[node_key]
            if val == 'entrance':
                node.is_entrance = True
            elif val == 'exit':
                node.is_exit = True
            else: raise ValueError(val)
        
        # Setup the rule Squares
        ig=self.puzzle_grid.inner_grid
        for node_key, rule in self.node_to_rule_map.items():
            node=ig[node_key]
            # TODO: Hack, should use polymorphic Rule class?
            rule_type, rule_value = rule
            if rule_type in ['shape']:
                node.set_rule_shape(rule_value)
            elif rule_type == 'distinct color':
                node.set_rule_color(rule_value)
            elif rule_type == 'sun color':
                node.set_rule_sun(rule_value)
            else: raise ValueError(rule_type)
        
        for node_list in self.path_edges_to_sever:
            n1_key, n2_key = node_list
            self.puzzle_grid.get_edge_by_coordinates(n1_key, n2_key).sever_both()
        
        for node_list in self.must_travel_edges:
            n1_key, n2_key = node_list
            self.puzzle_grid.get_edge_by_coordinates(n1_key, n2_key).must_travel=True    
        
        for node_key in self.must_travel_nodes:
            self.puzzle_grid[node_key].must_travel = True
            
        self.puzzle_grid.finalize()
        
    def testSolvePuzzle(self):
        
        pg=self.puzzle_grid
        # Render initial state
        pg.render()
        
        # Generate all possible paths
        pg.generate_paths(overwrite=self.overwrite_all_paths)
        
        # Filter paths (if possible)
        pg.filter_paths(
            overwrite=self.overwrite_filtered_paths, 
            expecting_filtered=self.expecting_filtered_paths)
    
        # Generate all solutions
        pg.solve(
            break_on_first=self.break_on_first_solution,
            # TODO: Completely separate rendering from solving? 
            render_all=self.render_all_attempts,
            force_paths=self.force_paths,
            force_check_all_paths=self.force_check_all_paths,
        )
        
        self.generated_solutions = set(frozenset(s) for s in pg.solutions)
    
        self.missing_solutions = self.expected_solutions - self.generated_solutions
        if self.expected_solutions:
            self.extra_solutions = self.generated_solutions - self.expected_solutions
        
        self.assertFalse(self.missing_solutions)
        self.assertFalse(self.extra_solutions)
        
        # Find the unsolved and first solved image
        img_dir, img_ext = defaultValueServer.get_directory_extension_pair('image')
        example_dir = defaultValueServer.get_directory('example')
        solution_dir = defaultValueServer.get_directory('solution')
        
        images_basename=self.puzzle_grid.images_basename()
        unsolved_img = os.path.join(img_dir, images_basename + img_ext)
        first_solved_img = os.path.join(img_dir, images_basename+'0' + img_ext)
        
        all_imgs = [unsolved_img, first_solved_img]
        if self.copy_to_examples:
            for i in all_imgs:
                shutil.copy(i, example_dir)
        if self.copy_to_solutions:
            for i in all_imgs:
                shutil.copy(i, solution_dir)