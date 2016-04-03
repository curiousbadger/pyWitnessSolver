'''
Created on Apr 2, 2016

@author: charper

A list of (hopefully) low cost functions that return a dictionary of attributes
describing a puzzle setup.

TODO: Let PuzzleTest instantiate Multiblock items during setUp()


'''

from src.lib.Geometry import Rectangle,MultiBlock

def MountainCabinet0():
    '''The purple puzzle inside the Mountain that is squished inside all the cabinets and drawers that you can't see very well'''
    
    puzzle_dimensions = Rectangle.get_rectangle(6,6)
    inner_dimmensions = puzzle_dimensions.grow_upper_right([-1,-1])
    
    entrance_exit_node_map={ inner_dimmensions.lower_left: 'entrance', 
        inner_dimmensions.upper_right:'exit'}
    
    Ishape4_0 = MultiBlock([(0,0), (1,0), (2,0), (3,0)], 'Ishape4_0')
    Ishape4_1 = MultiBlock([(0,0), (0,1), (0,2), (0,3)], 'Ishape4_1')
    
    node_to_rule_map={ 
        (0,0):('distinct color','white') , 
        (1,4):('distinct color','white') , 
        
        (4,0):('distinct color','black') , 
        (2,4):('distinct color','black') , 
        (3,2):('distinct color','black') , 
        
        (4,2):('shape', Ishape4_0) , 
        (2,2):('shape', Ishape4_1) , 
    }
    
    expected_solutions = [ 
        #[(0,0),(0,1),(0,2),(1,2),(2,2),(3,2),(4,2),(4,1),(4,0),(5,0),(5,1),(5,2),(5,3),(5,4),(4,4),(4,3),(3,3),(2,3),(1,3),(0,3),(0,4),(0,5),(1,5),(2,5),(2,4),(3,4),(3,5),(4,5),(5,5)]
    ]
    
    puzzle_definition = {
        'puzzle_dimensions':puzzle_dimensions.get_dimensions(), 
        'entrance_exit_node_map':entrance_exit_node_map, 
        'node_to_rule_map':node_to_rule_map, 
        'expected_solutions':expected_solutions, 
        'overwrite_filtered_paths':False , 
        'break_on_first_solution':True , 
    }
    return puzzle_definition
    # END   MountainCabinet0 --------------------------------------------------------

def MountainCabinet1():
    '''This one is laying flatter and is on the right side of the central "junk" column'''

    puzzle_name=MountainCabinet1.__name__
    description=MountainCabinet1.__doc__
    
    puzzle_dimensions = Rectangle.get_rectangle(6,6)
    inner_dimmensions = puzzle_dimensions.grow_upper_right([-1,-1])
    
    entrance_exit_node_map={ inner_dimmensions.lower_left: 'entrance', 
        inner_dimmensions.upper_right:'exit'}
    
    Ishape2_0 = MultiBlock([(0,0), (1,0)], 'Ishape2_0')
    Ishape3_1 = MultiBlock([(0,0), (0,1), (0,2)], 'Ishape3_1')
    
    node_to_rule_map={ 
        (0,4):('distinct color','white') , 
        (4,3):('distinct color','white') , 
        
        (0,1):('distinct color','black') , 
        (4,0):('distinct color','black') , 
        
        (2,2):('shape', Ishape2_0) , 
        (2,3):('shape', Ishape3_1) , 
    }
    
    expected_solutions = [ 
        
    ]
    
    puzzle_definition = { 
        'puzzle_name':puzzle_name, 
        'description':description, 
        'puzzle_dimensions':puzzle_dimensions.get_dimensions(), 
        'entrance_exit_node_map':entrance_exit_node_map, 
        'node_to_rule_map':node_to_rule_map, 
        'expected_solutions':expected_solutions, 
        'overwrite_filtered_paths':False , 
        'break_on_first_solution':True , 
    }
    return puzzle_definition
    # END   MountainCabinet1 -------------------------------------------------------- 

def MountainLeft4():
    '''This is the first one where it's off-centered and tilted'''
    
    puzzle_dimensions = Rectangle.get_rectangle(6,6)
    inner_dimmensions = puzzle_dimensions.grow_upper_right([-1,-1])
    
    entrance_exit_node_map={ inner_dimmensions.lower_left: 'entrance', 
        inner_dimmensions.upper_right:'exit'}
    
    Ishape3_0 = MultiBlock([(0,0), (0,1), (0,2)], 'Ishape3_0', can_rotate=True)
    Ishape3_1 = MultiBlock([(0,0), (1,0), (2,0)], 'Ishape3_1')
    LShape4 = MultiBlock([(0,0),(0,1),(0,2),(1,0)], 'LShape4', can_rotate=True)
    
    node_to_rule_map={ 
        (0,0):('shape', Ishape3_0) , 
        (4,0):('shape', Ishape3_1) ,
        (2,4):('shape', LShape4) ,
    }
    
    expected_solutions = [ 
        
    ]
    
    path_edges_to_sever = [
        ((2,3), (2,4)) ,
        ((3,3), (4,3)) ,
    ]
    
    puzzle_definition={
        'puzzle_dimensions':puzzle_dimensions.get_dimensions(),
        'entrance_exit_node_map':entrance_exit_node_map,
        'node_to_rule_map':node_to_rule_map,
        'expected_solutions':expected_solutions,
        'path_edges_to_sever':path_edges_to_sever ,
        'overwrite_filtered_paths':False ,
        'break_on_first_solution':True ,
    }
    return puzzle_definition
    # END   MountainLeft4 --------------------------------------------------------
    
def MountainLeft5():
    '''This is the first one that is sloooowly tracking diagonally.
    
    Who repairs these things?'''
    
    puzzle_dimensions = Rectangle.get_rectangle(5,5)
    inner_dimmensions = puzzle_dimensions.grow_upper_right([-1,-1])
    
    entrance_exit_node_map={ inner_dimmensions.lower_left: 'entrance', 
        inner_dimmensions.upper_right:'exit'}
    
    node_to_rule_map={ 
        (0,0):('distinct color','black') , 
        (1,0):('distinct color','black') , 
        (2,2):('distinct color','black') , 
        
        (1,1):('distinct color','white') , 
        (2,3):('distinct color','white') , 
        (3,3):('distinct color','white') , 
        
        (0,3):('sun color','purple') , 
        (3,0):('sun color','purple') , 
    }
    
    expected_solutions = [
    ]
    force_paths = [
    ]
    path_edges_to_sever = [
        ((2,0), (2,1)) ,
        ((3,1), (3,2)) ,
        ((0,4), (1,4)) ,
        ((3,3), (4,3)) ,                      
    ]
    
    puzzle_definition = {
        'puzzle_dimensions':puzzle_dimensions.get_dimensions(), 
        'entrance_exit_node_map':entrance_exit_node_map, 
        'node_to_rule_map':node_to_rule_map, 
        'expected_solutions':expected_solutions, 
        'force_paths':force_paths,
        'path_edges_to_sever':path_edges_to_sever ,
        'overwrite_filtered_paths':False , 
        'break_on_first_solution':False , 
    }
    return puzzle_definition
    # END   MountainLeft5 --------------------------------------------------------    

def MountainLeft6():
    '''This one tracks in proportion to the current path you're drawing.
    
    Crazy!'''
    
    puzzle_dimensions = Rectangle.get_rectangle(5,5)
    inner_dimmensions = puzzle_dimensions.grow_upper_right([-1,-1])
    
    entrance_exit_node_map={ inner_dimmensions.lower_left: 'entrance', 
        inner_dimmensions.upper_right:'exit'}
    
    Ishape3 = MultiBlock([(0,0), (1,0), (2,0)], 'Ishape3')
    LShape3 = MultiBlock([(0,0),(0,1),(1,1)], 'LShape3')
    
    node_to_rule_map={ 
        (1,0):('shape', Ishape3) , 
        (1,3):('shape', LShape3) ,
    }
    
    expected_solutions = [
    ]
    
    path_edges_to_sever = [
    ]
    
    must_travel_nodes = [
        (4,3)
    ]
    puzzle_definition={
        'puzzle_dimensions':puzzle_dimensions.get_dimensions(),
        'entrance_exit_node_map':entrance_exit_node_map,
        'node_to_rule_map':node_to_rule_map,
        'expected_solutions':expected_solutions,
        'path_edges_to_sever':path_edges_to_sever ,
        'must_travel_nodes': must_travel_nodes,
        'overwrite_all_paths':True,
        'overwrite_filtered_paths':True ,
        'expecting_filtered_paths':True, 
        'break_on_first_solution':False ,
    }
    return puzzle_definition
    # END   MountainLeft6 --------------------------------------------------------

def MountainLeft8():
    '''This one SPINS in proportion to the current path you're drawing.
    
    DOUBLE Crazy!'''
    
    puzzle_dimensions = Rectangle.get_rectangle(5,5)
    inner_dimmensions = puzzle_dimensions.grow_upper_right([-1,-1])
    
    entrance_exit_node_map={ inner_dimmensions.lower_left: 'entrance', 
        inner_dimmensions.upper_right:'exit'}
    
    node_to_rule_map={
    }
    
    expected_solutions = [ 
    ]
    
    path_edges_to_sever = [
    ]
    must_travel_nodes = [
        (1,2)
    ]
    must_travel_edges = [
        ((2,1), (3,1)) ,
        ((2,4), (3,4)) ,
        ((4,2), (4,3)) ,
    ]
    puzzle_definition={
        'puzzle_dimensions':puzzle_dimensions.get_dimensions(),
        'entrance_exit_node_map':entrance_exit_node_map,
        'node_to_rule_map':node_to_rule_map,
        'expected_solutions':expected_solutions,
        'path_edges_to_sever':path_edges_to_sever ,
        'must_travel_nodes': must_travel_nodes,
        'must_travel_edges': must_travel_edges,
        'overwrite_all_paths':True,
        'overwrite_filtered_paths':True ,
        'expecting_filtered_paths':True, 
        'break_on_first_solution':True ,
    }
    return puzzle_definition
    # END   MountainLeft8 --------------------------------------------------------

def MountainRight1():
    '''Second puzzle on Right with Colors and MustTravel hexagons'''
    
    puzzle_dimensions = Rectangle.get_rectangle(5,5)
    inner_dimmensions = puzzle_dimensions.grow_upper_right([-1,-1])
    
    entrance_exit_node_map={ inner_dimmensions.lower_left: 'entrance', 
        inner_dimmensions.upper_right:'exit'}
    
    node_to_rule_map={
    }
    
    expected_solutions = [ 
    ]
    
    path_edges_to_sever = [
    ]
    must_travel_nodes = [
        (1,2)
    ]
    must_travel_edges = [
        ((2,1), (3,1)) ,
        ((2,4), (3,4)) ,
        ((4,2), (4,3)) ,
    ]
    puzzle_definition={
        'puzzle_dimensions':puzzle_dimensions.get_dimensions(),
        'entrance_exit_node_map':entrance_exit_node_map,
        'node_to_rule_map':node_to_rule_map,
        'expected_solutions':expected_solutions,
        'path_edges_to_sever':path_edges_to_sever ,
        'must_travel_nodes': must_travel_nodes,
        'must_travel_edges': must_travel_edges,
        'overwrite_all_paths':False,
        'overwrite_filtered_paths':False,
        'expecting_filtered_paths':True, 
        'break_on_first_solution':True ,
        'copy_to_solutions':True
    }
    return puzzle_definition
    # END   MountainLeft8 --------------------------------------------------------

def Bunker6():
    '''Simpler puzzle from first Bunker room.'''
    
    puzzle_dimensions = Rectangle.get_rectangle(5, 5)
    inner_dimmensions = puzzle_dimensions.grow_upper_right([-1,-1])
    
    entrance_exit_node_map={ inner_dimmensions.lower_left: 'entrance', 
        inner_dimmensions.upper_right:'exit'}
    
    node_to_rule_map={
        (0,0):('distinct color','aqua') , 
        (0,3):('distinct color','aqua') ,  

        (1,1):('distinct color','yellow') , 
        (1,2):('distinct color','yellow') , 
        
        (2,1):('distinct color','antiquewhite') , 
        (2,2):('distinct color','antiquewhite') ,  

        (3,0):('distinct color','red') ,
        (3,3):('distinct color','red') ,
    }
    
    force_paths = [
        [(0,0),(0,1),(0,2),(0,3),(0,4),(1,4),(1,3),(1,2),(1,1),(1,0),(2,0),(2,1),(2,2),(2,3),(2,4),(3,4),(3,3),(3,2),(3,1),(3,0),(4,0),(4,1),(4,2),(4,3),(4,4)]
    ]
    expected_solutions = [
        [(0,0),(0,1),(0,2),(0,3),(0,4),(1,4),(1,3),(1,2),(1,1),(1,0),(2,0),(2,1),(2,2),(2,3),(2,4),(3,4),(3,3),(3,2),(3,1),(3,0),(4,0),(4,1),(4,2),(4,3),(4,4)]
    ]
    
    puzzle_definition={ 
        'puzzle_dimensions':puzzle_dimensions.get_dimensions(),
        'entrance_exit_node_map':entrance_exit_node_map, 
        'node_to_rule_map':node_to_rule_map,
        'force_paths':force_paths,
        'expected_solutions':expected_solutions,
        'overwrite_filtered_paths':False ,
        'expecting_filtered_paths':True,
        'copy_to_solutions':True
    }
    return puzzle_definition

def Bunker7():
    '''Medium puzzle from first Bunker room.'''
    
    puzzle_dimensions = Rectangle.get_rectangle(5, 5)
    inner_dimmensions = puzzle_dimensions.grow_upper_right([-1,-1])
    
    entrance_exit_node_map={ inner_dimmensions.lower_left: 'entrance', 
        inner_dimmensions.upper_right:'exit'}
    
    node_to_rule_map={
        (0,0):('distinct color','aqua') , 
        (0,3):('distinct color','aqua') ,  

        (1,1):('distinct color','yellow') , 
        (2,1):('distinct color','yellow') , 
         
        (1,2):('distinct color','antiquewhite') ,
        (2,2):('distinct color','antiquewhite') ,  

        (3,0):('distinct color','red') ,
        (3,3):('distinct color','red') ,
    }
    
    force_paths = [
        [(0,0),(0,1),(1,1),(1,0),(2,0),(3,0),(3,1),(4,1),(4,2),(3,2),(2,2),(1,2),(0,2),(0,3),(1,3),(1,4),(2,4),(3,4),(3,3),(4,3),(4,4)]
    ]
    expected_solutions = [
        [(0,0),(0,1),(1,1),(1,0),(2,0),(3,0),(3,1),(4,1),(4,2),(3,2),(2,2),(1,2),(0,2),(0,3),(1,3),(1,4),(2,4),(3,4),(3,3),(4,3),(4,4)]
    ]
    
    puzzle_definition={ 
        'puzzle_dimensions':puzzle_dimensions.get_dimensions(),
        'entrance_exit_node_map':entrance_exit_node_map, 
        'node_to_rule_map':node_to_rule_map,
        'force_paths':force_paths,
        'expected_solutions':expected_solutions,
        'overwrite_filtered_paths':False,
        'expecting_filtered_paths':True,
        'copy_to_solutions':True
    }
    return puzzle_definition

def Bunker8():
    '''Last puzzle in first Bunker room.'''
    
    puzzle_dimensions = Rectangle.get_rectangle(6, 5)
    inner_dimmensions = puzzle_dimensions.grow_upper_right([-1,-1])
    
    entrance_exit_node_map={ inner_dimmensions.lower_left: 'entrance', 
        inner_dimmensions.upper_right:'exit'}
    
    node_to_rule_map={
        (0,1):('distinct color','aqua') , 
        (0,2):('distinct color','aqua') , 
        (0,3):('distinct color','aqua') , 

        (1,3):('distinct color','white') , 
        (2,3):('distinct color','white') , 
        (3,0):('distinct color','white') , 
        (4,0):('distinct color','white') , 

        (2,1):('distinct color','red') , 
        (2,2):('distinct color','red') , 

        (4,1):('distinct color','yellow') , 
        (4,2):('distinct color','yellow') , 
        (4,3):('distinct color','yellow') , 
    }
    
    expected_solutions = [
        [(0,0),(0,1),(0,2),(0,3),(0,4),(1,4),(1,3),(1,2),(1,1),(1,0),(2,0),(2,1),(2,2),(2,3),(3,3),(3,2),(3,1),(3,0),(4,0),(5,0),(5,1),(4,1),(4,2),(4,3),(4,4),(5,4)]
    ]
    
    puzzle_definition={ 
        'puzzle_dimensions':puzzle_dimensions.get_dimensions(),
        'entrance_exit_node_map':entrance_exit_node_map, 
        'node_to_rule_map':node_to_rule_map, 
        'expected_solutions':expected_solutions, 
        'overwrite_filtered_paths':False ,
        'expecting_filtered_paths':True,
        'copy_to_solutions':True
    }
    return puzzle_definition

def ColorDemoMedium():
    '''ColorDemoMedium'''
    
    puzzle_dimensions = Rectangle.get_rectangle(4,4)
    inner_dimmensions = puzzle_dimensions.grow_upper_right([-1,-1])
    
    entrance_exit_node_map={ inner_dimmensions.lower_left: 'entrance', 
        inner_dimmensions.upper_right:'exit'}
    
    node_to_rule_map={ 
        (0,0):('distinct color','red') , 
        (0,1):('distinct color','red') , 
        
        (1,1):('distinct color','green') , 
        (1,2):('distinct color','green') , 
        (2,1):('distinct color','green') , 
        (0,2):('distinct color','green') , 

        (2,0):('distinct color','blue') , 
        (2,2):('distinct color','blue') , 
    }
    
    expected_solutions = [
        [(0,0),(0,1),(0,2),(1,2),(1,1),(1,0),(2,0),(2,1),(3,1),(3,2),(2,2),(2,3),(3,3)]
    ]
    
    puzzle_definition= {
        'puzzle_dimensions':puzzle_dimensions.get_dimensions(),
        'entrance_exit_node_map':entrance_exit_node_map,
        'node_to_rule_map':node_to_rule_map,
        'expected_solutions':expected_solutions,
        'overwrite_filtered_paths':False ,
        'copy_to_examples':True , 
    }
    return puzzle_definition

def Ishape3test():
    '''4x4 Grid with a 3-block "I" shape in the center and one on the left'''
    
    puzzle_dimensions = Rectangle.get_rectangle(4, 4)
    inner_dimmensions = puzzle_dimensions.grow_upper_right((-1,-1))
    
    Ishape3_0 = MultiBlock([(0, 0), (0, 1), (0, 2)], 'Ishape3_0')
    Ishape3_1 = MultiBlock([(0, 0), (0, 1), (0, 2)], 'Ishape3_1')
    
    entrance_exit_node_map={ inner_dimmensions.lower_left: 'entrance', 
        inner_dimmensions.upper_right:'exit'}
    
    node_to_rule_map={ 
        (1,1):('shape', Ishape3_0), 
        (0,0):('shape',Ishape3_1)}
    
    expected_solutions = [
        [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (1, 2), (1, 1), (1, 0), (2, 0), (2, 1), (2, 2), (2, 3), (3, 3)],
        [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (2, 3), (2, 2), (2, 1), (2, 0), (3, 0), (3, 1), (3, 2), (3, 3)], 
        [(0, 0), (1, 0), (1, 1), (1, 2), (1, 3), (2, 3), (2, 2), (2, 1), (2, 0), (3, 0), (3, 1), (3, 2), (3, 3)], 
        [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (2, 3), (3, 3)]
    ]
    
    puzzle_definition={
        'puzzle_dimensions':puzzle_dimensions.get_dimensions(), 
        'entrance_exit_node_map':entrance_exit_node_map, 
        'node_to_rule_map':node_to_rule_map, 
        'expected_solutions':expected_solutions,
    }
    return puzzle_definition
    # END   Ishape3test ---------------------------------------------------------------

if __name__ == '__main__':
    pass