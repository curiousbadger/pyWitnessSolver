'''
Created on Feb 24, 2016

@author: charper
'''
#TODO: Hack...
from ast import literal_eval

import logging
from lib import lib_dbg_filehandler, lib_consolehandler, lib_inf_filehandler
module_logger=logging.getLogger(__name__)
#module_logger.addHandler(lib_dbg_filehandler)
module_logger.addHandler(lib_inf_filehandler)
module_logger.addHandler(lib_consolehandler)
linf, ldbg = module_logger.info, module_logger.debug

from lib.util import simplePickler, WastedCounter, MasterUniqueNumberGenerator

from lib.GraphImage import GraphImage


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

        self._filtered_paths = simplePickler(
            self.filtered_paths_filename())

    def filtered_paths_filename(self):
        return self.paths_filename() + '_filtered'

    def paths_filename(self):
        return '%s_%s' % (self.puzzle_name, super().paths_filename())
    

    def filter_paths(self, overwrite=False, expecting_filtered=False):
        '''TODO: Hacked to remove pairs (Edges) or indiv Nodes
        
        Filter paths to those containing segments bounding adjacent, differing rule_colors'''
        
        if not self.paths:
            self.load_paths()
        
        if self._filtered_paths.file_exists():
            if not overwrite:
                self.potential_paths = self._filtered_paths.load()
                print('Skipping filter_paths...')
                return
            else:
                print('Overwriting filter_paths_colors_only...')
                
        # get a list of all boundaries between adjacent differing colors
        color_boundaries = frozenset(s.different_color_boundaries for s in self.inner_grid.values(
        ) if s.different_color_boundaries)
        
        # TODO: Hack to remove pairs (Edges) or indiv Nodes
        must_travel_nodes = frozenset(self.must_travel_nodes | self.must_travel_edges | color_boundaries)
        linf('must_travel_nodes '+str(must_travel_nodes))
        
        if not must_travel_nodes:
            if expecting_filtered:
                raise Exception('No must_travel nodes!')
            linf('No must_travel_nodes, skipping...')
            self.potential_paths=self.paths
            return
        
        self.potential_paths = []
        
        print('Attempting to filter:',len(self.paths),'total paths')
        paths_searched=0
        # iterate over each path
        for path in self.paths:
            
            # TODO: Hack...
            if type(path)==str:
                le_path=literal_eval(path)
            else:
                le_path=path
            #ldbg(path)
            #ldbg(le_path)
            
            '''Build a copy of the nodes we have to travel, as soon as we've hit
            all of them, we're done, this is a potential path.
            '''
            must_travel_copy=set(must_travel_nodes)
            for i in range(len(le_path)-1):
                seg=frozenset(le_path[i:i+2])
                
                # TODO: Hack to remove pairs (Edges) or indiv Nodes
                # Remove Edge
                must_travel_copy -= frozenset([seg])
                # Remove individual Nodes
                must_travel_copy -= seg
                if not must_travel_copy:
                    self.potential_paths.append(path)
                    break
            
            paths_searched+=1
            if not paths_searched % 50000:
                print(
                    ('Filtered %.2g%% paths: %d, paths found: %d') % (
                        100 * paths_searched / len(self.paths), 
                        paths_searched, 
                        len(self.potential_paths)
                    )
                )
            
        if not self.potential_paths and expecting_filtered:
            raise Exception('No filtered paths')
        
        linf('Filtered %d paths to %d' % \
            (len(self.paths), len(self.potential_paths)))
            
        self._filtered_paths.dump(self.potential_paths)
        
    def has_violations(self):
        # Innocent until proven guilty ;)
        violation = False
        
        '''We could break after each of these, but maybe we want to see where the
        violation occurs, or check other violations just for fun?'''
        
        if self.find_any_sun_violation():
            violation = True
            return True
        
        if self.find_any_color_violation():
            violation = True
            return True
            
        if self.find_any_shape_violation():
            violation = True
            return True

        return violation
    
    def solve(self, break_on_first=False, render_all=False, force_paths=None, force_check_all_paths=False):
        if not self.finalized:
            raise Exception('Attempting to solve unfinalized Grid!')
        
        ''' Iterate over every potential path and check each GridSquare
        with a rule for violations.
        '''
        # Auto-load paths if they have been previously generated
        if not self.paths:
            self.generate_paths()
        if not self.potential_paths or force_check_all_paths:
            if not self.potential_paths:
                print('WARNING: No filtered paths found')
            if force_check_all_paths:
                print('WARNING: Force check all paths')
            self.potential_paths = self.paths
            if not self.potential_paths:
                raise Exception('Unable to find any paths')
        
        if force_paths:
            print('WARNING: Forcing pre-set paths:', force_paths)
            self.potential_paths=force_paths
            
        print('Checking',len(self.potential_paths),'paths...')
        paths_searched=0
        for p in self.potential_paths:
            
            # TODO: Hack... Use Path class instead of OrderededDict and encapsulate efficient search/serialization
            if type(p)==str:
                p=literal_eval(p)
            #print('Evaluating:\n'+str(p))
            self.set_current_path(p)
            
            solution = not self.has_violations()
            
            if solution:
                self.solutions.append(p)
                linf('Found solution!'+str(p))
                self.render_solution()
                if break_on_first:
                    break
            if render_all:
                self.render_solution('render_all_'+(MasterUniqueNumberGenerator.get()))
            
            paths_searched+=1
            if not paths_searched % 50000:
                print(
                    ('Searched: %.2g%% paths: %d, paths found: %d') % (
                        100 * paths_searched / len(self.potential_paths), 
                        paths_searched, 
                        len(self.solutions)
                    )
                )
        print('Found', len(self.solutions), 'total solutions!')

