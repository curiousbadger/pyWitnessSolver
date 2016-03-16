'''
Created on Feb 26, 2016

@author: charper
'''
from math import hypot
from lib.util import MasterUniqueColorGenerator

class Point(tuple):
    
    @staticmethod
    def get_subtraction_vector(point_list):
        '''Given a list of points find the leftmost x and lowest y value. '''
        return Point((min([p.x for p in point_list]),min([p.y for p in point_list])))
    
    @staticmethod
    def get_Q1_shifted(point_list):
        subtraction_vector=Point.get_subtraction_vector(point_list)
        return [p-subtraction_vector for p in point_list],subtraction_vector
    def __new__(cls,p):
        return tuple.__new__(cls, tuple(p))

    @property
    def x(self): return self[0]
    @property
    def y(self): return self[1]
    
    def __sub__(self,other): return Point([self.x-other.x,self.y-other.y])
    
    def __add__(self,other): return Point([self.x+other.x,self.y+other.y])
    def __mul__(self,other): return Point([self.x*other.x,self.y*other.y])
    def __repr__(self): return '(%d,%d)' % (self.x,self.y)
    
    
    def strict_left(self, other):
        return self.x < other.x
    def strict_below(self,other):
        return self.y < other.y
    def is_vertical_with(self,other):
        return self.x==other.x
    def is_horizontal_with(self,other):
        return self.y==other.y
    
    def __cmp__(self, other):
        raise Exception('cmp',self,other)
        ''' A point is considered less than another if it's x coordinate is lower, else if it's y is lower '''
        if self.x==other.x:
            if self.y < other.y: return -1
            elif self.y > other.y: return 1
            else: return 0 
        else:
            if self.x < other.x: return -1
            elif self.x > other.x: return 1
            else: return 0
    
    def scaled(self,scalar):
        return Point([self.x*scalar,self.y*scalar])
    def dist(self,other): return hypot(self.x-other.x, self.y-other.y)
    
    def max_dimension(self):
        return max(d for d in self)
    def as_int_tuple(self):
        return tuple([int(d) for d in self])
class Rectangle(tuple):
    '''A Rectangle implemented as a set of 4 points.
    
    Points need to be passed in order:
    lower left, lower right, upper right, upper left
    
    TODO: No need to use all 4 points. Change implementation
    to use a Point at lower-left and then a Point representing
    width,height '''
    @staticmethod
    def get_rectangle_points(w, h):
        pl = [Point(p) for p in [[0, 0], [w, 0], [w, h], [0, h]]]
        return pl
    @staticmethod
    def get_sqare_points(w):
        return Rectangle.get_rectangle_points(w, w)
    
    def __new__(cls, p, *args, **kwds):
        return tuple.__new__(cls, tuple(p))
    
    def __init__(self,p,offset=None,color='orange'):
        self.offset=Point(offset) if offset else Point([0,0])
        
        #TODO: Needed here?
        self.color=color
   
    # TODO: __add__ and get_bounding_rectangle are begging to be combined...
    def __add__(self,other):
        # Given 2 rectangles, return the smallest Rectangle that includes all of both
        all_points=list(self)+list(other)

        nll=Point([min([p.x for p in all_points]),min([p.y for p in all_points])])
        nlr=Point([max([p.x for p in all_points]),min([p.y for p in all_points])])
        nur=Point([max([p.x for p in all_points]),max([p.y for p in all_points])])
        nul=Point([min([p.x for p in all_points]),max([p.y for p in all_points])])
        
        return Rectangle([nll,nlr,nur,nul])
    
    @staticmethod
    def get_bounding_rectangle(point_list):
        all_points=point_list
        # Given a set of coordinates, return the smallest rectangle that contains all points
        nll=Point([min([p.x for p in all_points]),min([p.y for p in all_points])])
        nlr=Point([max([p.x for p in all_points]),min([p.y for p in all_points])])
        nur=Point([max([p.x for p in all_points]),max([p.y for p in all_points])])
        nul=Point([min([p.x for p in all_points]),max([p.y for p in all_points])])
        
        return Rectangle([nll,nlr,nur,nul])

    def abs_coords(self,scalar=1):
        return Rectangle([Point(p+self.offset).scaled(scalar) for p in self],(0,0),self.color)
    
    @property
    def lower_left(self): return self[0]+self.offset
    @property
    def lower_right(self): return self[1]+self.offset
    @property
    def upper_right(self): return self[2]+self.offset
    @property
    def upper_left(self): return self[3]+self.offset
    
    def width(self): return self[1].x-self[0].x
    def height(self): return self[3].y-self[0].y
    
    def get_dimensions(self):
        return Point([self.width(),self.height()])
    
    def could_contain(self, other):
        return not (self.width()<other.width() or self.height()<other.height())
    # TODO: Mixes absolute and relative through properties
    def __repr__(self):
        return 'Rectangle: %s to %s offset: %s color: %s' % (self.lower_left,self.upper_right,self.offset,self.color) 

class MultiBlock(set):
    MultiBlockColorGenerator=MasterUniqueColorGenerator
    def could_contain(self,other):
        return self.bounding_rectangle.could_contain(other.bounding_rectangle)
    def rotate(self,angle):
        '''
        In general if:
        R=| cos(t) -sin(t) |
          | sin(t)  cos(t) |
        and the point we want to rotate is:
        P=| x |
          | y |
        Then the new coordinates are the matrix product R*P
        So our new points are:
        transformedX = x * cos(t) - y * sin(t)
        transformedY = x * sin(t) + y * cos(t)
        
        Luckily we get to deal with 3 angles divisible by pi/2, so they collapse into:

        angle=0 -> t=pi/2    -> sin(t)=1, cos(t)=0
        angle=1 -> t=pi      -> sin(t)=0, cos(t)=-1
        angle=2 -> t=3*pi/4  -> sin(t)=-1, cos(t)=0

        Rotate all the points by the given angle. This will usually result in 
        negative x or y values. These points are all relative, so shift them 
        as little as possible to put the lowest point at y=0 and the leftmost 
        point at x=0
        '''
        new_points=[]
        for p in self.point_list:
            s,c=[(1,0),(0,-1),(-1,0)][angle]
            new_point=Point((p.x*c-p.y*s,p.x*s+p.y*c))
            new_points.append(new_point)
        
        new_points_shifted,subtraction_vector=Point.get_Q1_shifted(new_points)

        return new_points_shifted

    '''A MultiBlock is the underlying shape for the MultiBlockSquare.
    
    A MultiBock is composed of one or more (usually contiguous) 1-unit squares.
    For the purposes of puzzle solving it is best to consider them as a set of
    "Virtual Squares" that need to be perfectly bounded within a sub-section
    of the Grid. Or conversely, there cannot be any Square within the Path-bounded 
    sub-section that is not "filled" by a Virtual Square from a MultiBlock. 
    
    Virtual Squares within a sub-section need not all come from the same MultiBlock. 
    Indeed they often won't, and in that case they need to fit together. However, a
    MultiBlock cannot usually be "broken up", it must retain it's original shape,
    but some do have gaps or holes.
    
    It's kind of like Tetris.
    
    '''
    def __init__(self, point_list,name=None,auto_shift_Q1=True,color=None,can_rotate=False):
        '''PRE: Each Point has been assigned it's relative coordinates within the
        MultiBlock.
        
        '''
        self.name=name
        self.color=color
        self.point_list=[Point(p) for p in point_list]
        #print('MultiBlock self.point_list',self.point_list)
        if auto_shift_Q1:
            self.point_list,self.last_offset=Point.get_Q1_shifted(self.point_list)
        for p in self.point_list:
            self.add(p)
        self.bounding_rectangle=Rectangle.get_bounding_rectangle(self.point_list)
        
        self.can_rotate=can_rotate
        self.last_rotation=-1
        self.rotations=[self]
        if self.can_rotate:
            for i in range(3):
                new_points=self.rotate(i)
                new_name='%s_r%d' % (self.name, i+1)
                r_shape=MultiBlock(new_points,name=new_name,color=color,can_rotate=False)
                self.rotations.append(r_shape)
    
    def offset_point(self):
        return self.bounding_rectangle.offset
    
    def upper_right(self):
        return self.bounding_rectangle.upper_right
    
    def set_offset(self, new_offset):       
        self.bounding_rectangle.offset = new_offset

    def get_absolute_point_set(self):
        op=self.offset_point()
        return set([p+op for p in self])
    
    @staticmethod
    def yield_all_arrangements(partition, shape):
        shape_rect=shape.bounding_rectangle
        p_rect=partition.bounding_rectangle
        #print('shape', shape)
        #print('partition', partition)
        # Can we fit inside this partition at all?
        if not p_rect.could_contain(shape_rect):
            return None
        max_shift_point=p_rect.upper_right-shape_rect.upper_right
        #print('max_shift_point',max_shift_point)
        for y in range(max_shift_point.y+1):
            for x in range(max_shift_point.x+1):
                shift_vector=Point((x,y))
                # Shift all the shape's Points
                shifted_points=frozenset([p+shift_vector for p in shape])
                #print('shifted_points',shifted_points)
                
                outside_points=shifted_points - partition
                if outside_points:
                    #print('outside_points', outside_points)
                    continue
                # Return all the points in the partition that are left
                remaining_partition_points=partition - shifted_points
                #print('remaining_partition_points',remaining_partition_points)
                yield remaining_partition_points,shift_vector
    

    def yield_rotations(self):
        for rotation in self.rotations:
            self.last_rotation=(self.last_rotation+1) % len(self.rotations)
            yield rotation
            
    def compose(self, partition):
        '''Given a partition, return all possible locations this shape could occupy
        within that partition'''
        
        for rotation in self.rotations:
            self.last_rotation= (self.last_rotation+1) % len(self.rotations)
            for rp,sv in MultiBlock.yield_all_arrangements(partition, rotation):
                #self.last_offset=sv
                yield rp,sv
        return
    
    def get_color(self):
        if not self.color:
            self.color=MultiBlock.MultiBlockColorGenerator.get()
        return self.color
    def get_last_rotation(self):
        return self.rotations[self.last_rotation]
    def __repr__(self):
        if self.name: return self.name + self.point_str()
        return ''.join([str(p) for p in self.point_list])
    def point_str(self):
        return ''.join([str(p) for p in self.point_list]) +' ofst:'+ str(self.offset_point())

    def part_off(self):
        return self.__repr__()+' '+str(self.last_offset)

def compose_shapes(counter, shapes_list, partition, last_offset):
        print('START compose_shapes')
        print('    counter',counter)
        print('    partition',partition.part_off())
        print('    shapes_list',shapes_list)
        cur_shape = shapes_list[counter]

        # Remember the last offset, if we find a solution this helps with
        # rendering
        cur_shape.last_offset = partition.last_offset

        # Iterate over all possible positions this shape could occupy
        for remaining_partition_points, new_offset in cur_shape.compose(partition):

            # print('remaining_partition_points',remaining_partition_points)
            if not remaining_partition_points:
                # We filled up the partition, but have we placed all shapes?
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
                ret = compose_shapes(
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
    

def geom_print(*args):
    pass
#print=geom_print
if __name__=='__main__':
    ''' XXX
         X  '''
    TshapeDown = MultiBlock([(0, 1), (1, 1), (2, 1), (1, 0)], 'TshapeDown')
    p=Point([-5,-6])
    print(p.max_dimension())
    TshapeDown.set_offset(p)
    print('TshapeDown.bounding_rectangle', TshapeDown.bounding_rectangle)
    print(TshapeDown.bounding_rectangle.get_dimensions().max_dimension())
    exit(0)
    r3x3=MultiBlock([(x,y) for x in range(3) for y in range(3)])
    r3x2=MultiBlock([(x,y) for x in range(3) for y in range(2)])
    r2x3=MultiBlock([(x,y) for x in range(2) for y in range(3)])
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
    '''   X
        XXX'''
    LshapeUpRight=MultiBlock([(0,0),(1,0),(2,0),(2,1)])
    ''' X  
        XXX'''
    LshapeUpLeft=MultiBlock([(0,0),(1,0),(2,0),(0,1)])
    ''' XXX  
          X  '''
    LshapeDownRight=MultiBlock([(0,1),(1,1),(2,1),(2,0)])
    '''  X
        XXX '''
    TshapeUp=MultiBlock([(0,0),(1,0),(2,0),(1,1)],name='TshapeUp',color='red',can_rotate=True)
    ''' XX '''
    IshapeHoriz2=MultiBlock([(0,0),(1,0)])
    ''' X
        X'''
    IshapeVert2=MultiBlock([(0,0),(1,0)])
    Single0=MultiBlock([(0,0)])
    Single1=MultiBlock([(0,0)])
    
    ''' STS
        TTT '''
    
    
    shape_list=[LshapeUpRight,IshapeHoriz2]
    shape_list=[LshapeUpLeft,Single0,Single1]
    shape_list=[TshapeUp,Single0,Single1]
    
    
    partition=r2x3
    cs_ret=compose_shapes(0, shape_list, partition,None)
    print('cs_ret',cs_ret)
    for s in shape_list:
        print(s,'last_offset',s.last_offset)
#         for r in s.rotations:
#             print('r', r,r.point_str())
    
    exit(0)
    ishape3=[(0,0),(0,1),(0,2)]
    mb=MultiBlock(ishape3)
    print('r3x3',r3x3)
    for s in mb.compose(r3x3):
        print(s)
    
    exit(0)
    #test rotation
    lshape=MultiBlock([(0,0),(0,1),(0,2),(1,2)])
    for a in range(3):
        print(lshape.rotate(a))
        