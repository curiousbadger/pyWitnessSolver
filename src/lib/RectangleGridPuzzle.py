'''
Created on Feb 24, 2016

@author: charper
'''

from lib.GraphImage import GraphImage
from lib.util import simplePickler, WastedCounter, MasterUniqueNumberGenerator
import unittest
import cProfile

#TODO: Hack...
from ast import literal_eval


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
    
    # TODO: Decorator?
    def filter_paths_setup(self, overwrite=False):
        if not self.paths:
            self.load_paths()

        
       
    def filter_paths_colors_only(self, overwrite=False, expecting_filtered=False):
        '''TODO: Currently only works for RectangleGridPuzzles with rule_color GridSquares.
        
        Filter paths to those containing segments bounding adjacent, differing rule_colors'''
        
        self.filter_paths_setup(overwrite)
        
        if self.filtered_paths_pickler.file_exists():
            if not overwrite:
                self.potential_paths = self.filtered_paths_pickler.load()
                print('Skipping filter_paths_colors_only...')
                return
            else:
                print('Overwriting filter_paths_colors_only...')
                
        # get a list of all boundaries between adjacent differing colors
        color_boundaries = frozenset(s.different_color_boundaries for s in self.inner_grid.values(
        ) if s.different_color_boundaries)

        print('color_boundaries',color_boundaries)
        self.potential_paths = []
        
        print('Attempting to filter:',len(self.paths),'total paths')
        
        # iterate over each path
        for path in self.paths:
            
            # TODO: Hack...
            le_path=literal_eval(path)
            # for our purposes, path direction doesn't matter, only which segments (Node-Node) were traversed
            # if the path contains all of the segments we know MUST be
            # traversed, append it
            cb_copy=set(color_boundaries)
            for i in range(len(le_path)-1):
                seg=frozenset(le_path[i:i+2])
                if seg in cb_copy:
                    cb_copy.remove(seg)
                if len(cb_copy)==0:
                    self.potential_paths.append(path)
                    break
                    
        self.filter_paths_cleanup(expecting_filtered)

    def filter_paths_cleanup(self, expecting_filtered):
        if not self.potential_paths and expecting_filtered:
            raise Exception('No filtered paths')
        
        print('Filtered', len(self.paths),
              'paths to', len(self.potential_paths))
        self.filtered_paths_pickler.dump(self.potential_paths)
        
    def has_violations(self):
        # Innocent until proven guilty ;)
        violation = False
        
        '''We could break after each of these, but maybe we want to see where the
        violation occurs?'''
        if self.find_any_shape_violation():
            violation = True
            
        if self.find_any_color_violation():
            violation = True
        else:
            pass
            
        if self.find_any_sun_violation():
            violation = True
            
        return violation
    
    def solve(self, break_on_first=False, render_all=False, force_paths=None):
        
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
        
        if force_paths:
            print('WARNING: Forcing single-path solve', force_paths)
            self.potential_paths=force_paths
            
        print('Checking',len(self.potential_paths),'paths...')
        for p in self.potential_paths:
            
            # TODO: Hack... Use Path class instead of OrderededDict and encapsulate efficient search/serialization
            p=literal_eval(p)
            #print('Evaluating:\n'+str(p))
            self.set_current_path(p)
            
            solution = not self.has_violations()
            
            if solution:
                self.solutions.append(p)
                print('Found solution!', p)
                self.render_solution()
                if break_on_first:
                    break
            if render_all:
                self.render_solution('render_all_'+(MasterUniqueNumberGenerator.get()))
        print('Found', len(self.solutions), 'total solutions!')

