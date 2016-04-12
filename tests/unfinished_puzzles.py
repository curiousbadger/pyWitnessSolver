

def MountainQuadFloorPuzzle():
    '''TODO: Needs symmetric paths first?

    4 Shape sub-puzzles, then must solve a symmetry puzzle that is the
    combination of all of them. 

     *        **
    **        *
      *
      **      ***
              *

    **
    **        *** ***
      ***       * *
    '''
    puzzle_dimensions = Rectangle.get_rectangle(6, 6)
    inner_dimmensions = puzzle_dimensions.grow_upper_right([-1, -1])
    # Lower left sub-puzzle
    Square_lowleft = MultiBlock(
        (0, 0), (1, 0), (1, 1), (0, 1), 'Square_lowleft')
    Ibar3_lowleft = MultiBlock(
        (0, 0), (1, 0), (2, 0), 'Ibar3_lowleft')
    # Lower right
    LShapeReverse_low_right = MultiBlock(
        (0, 0), (1, 0), (1, 1), (1, 2), 'LShapeReverse_low_right', can_rotate=True)
    LShape_low_right = MultiBlock(
        (0, 0), (0, 1), (0, 2), (1, 0), 'LShape_low_right', can_rotate=True)
    # Upper right
    LShapeReverse_upper_right = MultiBlock(
        (0, 0), (1, 0), (1, 1), (1, 2), 'LShapeReverse_upper_right', can_rotate=False)
    VShapeUpRight_upper_right = MultiBlock(
        ((0, 0), (0, 1), (1, 1)), 'VShapeUpRight_upper_right')
    # Upper left
    VShapeDownRight_upper_left = MultiBlock(
        ((0, 0), (0, 1), (1, 0)), 'VShapeDownRight_upper_left')
    VShapeDownLeft_upper_left = MultiBlock(
        ((0, 0), (1, 0), (1, 1)), 'VShapeDownLeft_upper_left')
    entrance_exit_node_map = {inner_dimmensions.lower_left: 'entrance',
                              inner_dimmensions.upper_right: 'exit'}

#     Ishape3 = MultiBlock([(0,0), (0,1), (0,2)], 'Ishape3')
#     LShape3 = MultiBlock([(0,0),(0,1),(1,1)], 'LShape3')
#     Ishape2 = MultiBlock([(0,0), (0,1)], 'Ishape2')
    node_to_rule_map = {
        #(2,3):('shape',Ishape3),
    }

    expected_solutions = [
    ]
    path_edges_to_sever = [
    ]
    must_travel_nodes = [
    ]
    must_travel_edges = [
    ]

    puzzle_definition = {
        'puzzle_dimensions': puzzle_dimensions.get_dimensions(),
        'entrance_exit_node_map': entrance_exit_node_map,
        'node_to_rule_map': node_to_rule_map,
        'expected_solutions': expected_solutions,
        'path_edges_to_sever': path_edges_to_sever,
        'must_travel_nodes': must_travel_nodes,
        'must_travel_edges': must_travel_edges,
        'overwrite_all_paths': False,
        'overwrite_filtered_paths': False,
        'force_check_all_paths': False,
        'expecting_filtered_paths': True,
        'break_on_first_solution': False,
        'copy_to_solutions': True
    }
    return puzzle_definition
    # END   MountainQuadFloorPuzzle ------------------------------------------
