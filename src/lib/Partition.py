'''
Created on Mar 9, 2016

@author: charper
'''
from collections import Counter

from lib.Graph import Graph
from lib.Geometry import MultiBlock, Point
from lib.util import UniqueColorGenerator


class Partition(Graph):
    cg=UniqueColorGenerator()
    
    def travel_partition(self, n):
        if n.vec() in self:
            return
        
        self[n.vec()]=n
        for e in n.traversable_edges():
            if e.nodes not in self.edges:
                self.edges[e.nodes]=e
            self.travel_partition(e.traverse_from_node(n))

    def has_sun_violation(self):
        
        if self.sun_violation is not None:
            return self.sun_violation
        
        for col in [n.sun_color for n in self.values() if n.sun_color]:
            if col not in self.color_counter:
                self.color_counter[col]=1
            else:
                self.color_counter[col]+=1
        # Every sun needs a buddy...
        self.sun_violation = any(cnt != 2 for cnt in self.color_counter.values())
        return self.sun_violation
    
    def get_rule_shapes(self):
        if self.rule_shapes is not None and len(self.rule_shapes)==0:
            raise Exception('ruleshapes')
        if self.rule_shapes is None:
            self.rule_shapes=[]
            for n in self.values():
                cur_shape=n.rule_shape
                if cur_shape:
                    self.total_rule_shape_points+=len(cur_shape)
                    self.rule_shapes.append(n.rule_shape)
        return self.rule_shapes
    
    def can_be_composed_of(self,rule_shapes, partition_multiblock, depth_counter):
        cur_multiblock=rule_shapes[depth_counter]
        print('partition_multiblock', partition_multiblock)
        print('cur_multiblock', cur_multiblock)
        found_solution=False
        
        for cur_shape in cur_multiblock.rotations:
            
            print('    cur_shape',cur_shape)
            # Is the shape bigger than the partition?
            if not partition_multiblock.could_contain(cur_shape):
                print('            %s can''t contain %s', partition_multiblock, cur_shape)
                continue
            
            # Put the shape in the lower-left corner
            cur_shape.set_offset(partition_multiblock.offset_point())
            print('    cur_shape.offset_point', cur_shape.offset_point())
            
            max_shift_point=partition_multiblock.upper_right()-cur_shape.upper_right()
            print('    max_shift_point', max_shift_point)
            
            # TODO: Change to MultiBlock yield?
            for y in range(max_shift_point.y+1):
                for x in range(max_shift_point.x+1):
                    
                    cur_shape.set_offset(Point((x,y)))
                    
                    abs_points=cur_shape.get_absolute_point_set()
                    print('        abs_points', abs_points)
                
                    outside_points=abs_points - partition_multiblock
                    if outside_points:
                        print('            !!outside_points', outside_points)
                        continue
                    # Return all the points in the partition that are left
                    remaining_partition_points=partition_multiblock - abs_points
                    print('        remaining_partition_points', remaining_partition_points)
                    
                    # Haven't filled all our points yet...
                    if remaining_partition_points:
                        if depth_counter==len(rule_shapes)-1:
                            print( '            still points')
                            raise Exception('still points')
                        else:
                            print('            keep on truckin...')
                            new_partition=MultiBlock(remaining_partition_points,auto_shift_Q1=False)
                            print('            new_partition', new_partition)
                            found_solution=self.can_be_composed_of(rule_shapes, new_partition, depth_counter+1)
                    # Filled all our points, are we at the end?
                    else:
                        if depth_counter==len(rule_shapes)-1:
                            found_solution=True
                            
                        else:
                            raise Exception('Filled too soon')
                            return False
                    if found_solution:
                        print('            FOUND SOLUTION!!', cur_shape)
                        self.solution_shapes.append(cur_shape)
                        return True
        return False
        
    def has_shape_violation(self):
        
        if self.shape_violation is not None:
            return self.shape_violation
        self.solution_shapes=[]
        rule_shapes=self.get_rule_shapes()
        #print('rule_shapes', rule_shapes)
        if self.total_rule_shape_points != len(self):
            return True
        partition_multiblock=MultiBlock(self.keys(),name='partition_multiblock',auto_shift_Q1=False)
        
        self.shape_violation = not self.can_be_composed_of(rule_shapes,partition_multiblock, 0)
        return self.shape_violation
    
    def __init__(self, first_node=None):
        '''
        '''
        Graph.__init__(self)
        if first_node:
            self.travel_partition(first_node)
        self.shape_violation=None
        self.rule_shapes=None
        self.solution_shapes=[]
        self.total_rule_shape_points=0
        self.color_violation=None
        self.sun_violation=None
        self.color_counter=Counter()
        
    def get_img_rects(self):
        for s in self.solution_shapes:
            col=Partition.cg.get()
            print('sol_shape', s)
            for p in s.get_absolute_point_set():
                print('p', p)
                n=self[p]
                print('n', n)
                #exit(0)
                yield p,col

def pass_print(*args):
    pass
print=pass_print
if __name__=='__main__':
    pass
    
    
    