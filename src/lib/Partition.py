'''
Created on Mar 9, 2016

@author: charper
'''
from collections import Counter

import logging
from lib import lib_dbg_filehandler, lib_consolehandler, lib_inf_filehandler 
module_logger=logging.getLogger(__name__)
module_logger.addHandler(lib_inf_filehandler)
module_logger.addHandler(lib_dbg_filehandler)
module_logger.addHandler(lib_consolehandler)
linf, ldbg, ldbg2 = module_logger.info, module_logger.debug, module_logger.debug
ldbg('init:'+__name__)


from lib.Graph import Graph
from lib.Geometry import MultiBlock, Point
from lib.util import UniqueColorGenerator


class Partition(Graph):
        
    def travel_partition(self, n):
        '''Travel the partition to discover all Nodes.
        
        TODO: accumulate some simple rule info as we go?'''
        if n.key() in self:
            return
        
        self[n.key()]=n
        
        for e in n.traversable_edges():
            if e.nodes not in self.edges:
                self.edges[e.nodes]=e
            self.travel_partition(e.traverse_from_node(n))

    def get_rule_shapes(self):
        if self.rule_shapes is not None and len(self.rule_shapes)==0:
            raise Exception('ruleshapes')
        if self.rule_shapes is None:
            self.rule_shapes=[]
            self.rule_shape_nodes
            for n in self.values():
                cur_shape=n.rule_shape
                if cur_shape:
                    self.total_rule_shape_points+=len(cur_shape)
                    self.rule_shapes.append(n.rule_shape)
        return self.rule_shapes
    
    def can_be_composed_of(self,rule_shapes, partition_multiblock, depth_counter):
        cur_multiblock=rule_shapes[depth_counter]
        t='\t'*depth_counter
        
        #ldbg2(t,'partition_multiblock', partition_multiblock)
        #ldbg2(t,'cur_multiblock', cur_multiblock)
        found_solution=False
        
        for cur_shape in cur_multiblock.rotations:
            
            #ldbg2('    cur_shape',cur_shape)
            # Is the shape bigger than the partition?
            if not partition_multiblock.could_contain(cur_shape):
                #ldbg2('            %s can''t contain %s', partition_multiblock, cur_shape)
                continue
            
            # Put the shape in the lower-left corner
            cur_shape.set_offset(partition_multiblock.offset_point())
            #ldbg2('    cur_shape.offset_point', cur_shape.offset_point())
            
            max_shift_point=partition_multiblock.upper_right()-cur_shape.upper_right()
            #ldbg2('    max_shift_point', max_shift_point)
            
            # TODO: Change to MultiBlock yield?
            for y in range(max_shift_point.y+1):
                for x in range(max_shift_point.x+1):
                    # Shift all the shape's Points
                    cur_shape.set_offset(Point((x,y)))
                    
                    abs_points=cur_shape.get_absolute_point_set()
                    #ldbg2('        abs_points', abs_points)
                    '''There are now several possibilities:
                    1. The shifted points completely cover the partition points
                        We're done no matter what. If the last shape has been placed then
                        this is a solution. If not, then we ran out of space.
                    2. The shifted points are a proper subset of the partition points.
                        This is fine, pass the remaining points back to see if further shapes can fill them
                    3. The shifted points are not a subset of the partition points, ie.
                        some lie outside the partition points.
                        Invalid, discard and move on
                    
                    '''
                    # If any point in cur_shape lies outside the partition points, this is not a solution
                    # TODO: Change to yield? No reason to check all points, just need first violation
                    outside_points=abs_points - partition_multiblock
                    if outside_points:
                        #ldbg2('            !!outside_points', outside_points)
                        continue
                    # Return all the points in the partition that are left
                    remaining_partition_points=partition_multiblock - abs_points
                    #ldbg2('        remaining_partition_points', remaining_partition_points)
                    
                    # Haven't filled all our points yet...
                    if remaining_partition_points:
                        if depth_counter==len(rule_shapes)-1:
                            #ldbg2( '            still points')
                            raise Exception('still points')
                        else:
                            #ldbg2('            keep on truckin...')
                            new_partition=MultiBlock(remaining_partition_points,auto_shift_Q1=False)
                            #ldbg2('            new_partition', new_partition)
                            found_solution=self.can_be_composed_of(rule_shapes, new_partition, depth_counter+1)
                    # Filled all our points, are we at the end?
                    else:
                        if depth_counter==len(rule_shapes)-1:
                            found_solution=True
                        else:
                            # Should not happen till we start implementing SubtractionSquare 
                            raise Exception('Filled too soon')
                            return False
                    if found_solution:
                        #ldbg2('\t'*(depth_counter)+'FOUND SOLUTION!!', cur_shape)
                        sol_pts=cur_shape.get_absolute_point_set()
                        self.solution_shapes.append(sol_pts)
                        return True
        return False
    
    def has_shape_violation(self):
        
        if self.shape_violation is not None:
            raise Exception('Violation already checked')
            return self.shape_violation
        self.solution_shapes=[]
        rule_shapes=self.get_rule_shapes()
        #ldbg2('rule_shapes', rule_shapes)
        
        if self.total_rule_shape_points != len(self):
            self.shape_violation=True
            return True
        
        partition_multiblock=MultiBlock(self.keys(),name='partition_multiblock',auto_shift_Q1=False)
        
        self.shape_violation = not self.can_be_composed_of(rule_shapes,partition_multiblock, 0)
        return self.shape_violation
    
    def has_color_violation(self):
        
        if self.color_violation is not None:
            raise Exception('Violation already checked')
            return self.color_violation
        
        distinct_rule_colors = Counter([n.rule_color for n in self.values() if n.rule_color])
        #ldbg2('distinct_rule_colors', distinct_rule_colors)
        
        # Only 1 rule_color allowed per Partition
        self.color_violation = len(distinct_rule_colors)>1
            
        return self.color_violation
    
    def has_sun_violation(self):
        '''TODO: This logic is far from complete, but works for simple puzzles 
        The rule suns will actually count other objects with the same color as
        a "buddy", so far I've seen "Rule Shapes" and normal "Rule Colors" count.
        '''
        if self.sun_violation is not None:
            raise Exception('Violation already checked')
            return self.sun_violation
        
        rule_sun_colors = Counter([n.sun_color for n in self.values() if n.sun_color])

        # Every sun needs a buddy...
        self.sun_violation = any(cnt != 2 for cnt in rule_sun_colors.values())
        return self.sun_violation
    
    def __init__(self, first_node):
        '''
        '''
        Graph.__init__(self)
        
        self.travel_partition(first_node)
        self.shape_violation=None
        self.rule_shapes=None
        self.solution_shapes=[]
        self.total_rule_shape_points=0
        self.color_violation=None
        self.sun_violation=None
    
    
    def solution_shape_to_squares(self):
        '''Yield the set of Squares corresponding to each
        "Solution Shape".
        '''
        for solution_shape in self.solution_shapes:
            squares=set([self[key] for key in solution_shape])
            yield squares
            
    def solution_shapes_to_edges(self):
        '''Yield sets of Edges for each Solution Shape.
         
        A "Solution Shape" is a set of Points that correspond to
        a sub-Partition of this Partition. Note that these Points
        are not necessarily all neighbors, but return the Edges
        corresponding to those that are.
        
        # TODO: Also yield Square with Rule Shape corresponding to Solution Shape?
        '''
        
        # Create a temporary set of all Edges in this Partition,
        # (Actually Edge keys, which is a frozenset of two Squares,
        # but the squares are what we want anyways)
        edges_to_find=set(self.edges)

        for squares in self.solution_shape_to_squares():
            ldbg('Looking for Edges in solution shape:'+' '.join(s.sym for s in squares))
            # Find all edges that are in this shape -> The Edge's Squares are both in this
            # Solution Shape
            edges_in_shape=set([e for e in edges_to_find if e.issubset(squares)])
            
            # Finished looping over edges_to_find, remove what we found
            edges_to_find = edges_to_find - edges_in_shape
            yield edges_in_shape
            
            if not edges_to_find:
                # Will only happen if Partition is composed of 1 Rule Shape
                ldbg('    !!!found all edges!!!')
                break


if __name__=='__main__':
    
    exit(0)
    
    
    
    