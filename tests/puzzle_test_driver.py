import os
import glob
from shutil import copyfile
import puzzle_definitions

from PuzzleTest import PuzzleTest

from lib.util import defaultValueServer
from lib.GraphImage import chImg

img_dir, img_ext = defaultValueServer.get_directory_extension_pair('image')
solution_img_dir = defaultValueServer.get_directory('solution')
example_img_dir = defaultValueServer.get_directory('example')


def clear_image_directory():
    ''' Delete all .png images in the img/example dir '''
    search_pattern = os.path.join(img_dir, '*' + img_ext)
    r = glob.glob(search_pattern)
    for f in r:
        os.remove(f)


def combine_images():
    '''Combine images side-by side '''
    solutions_combine_list = [
        ('Bunker2_unsolved_combined.jpg',
         'Bunker2_unsolved.jpg', 'Bunker2_4x4RectGridGraph.png'),
        ('Bunker2_solved_combined.jpg', 'Bunker2_solved.jpg',
         'Bunker2_4x4RectGridGraph0.png'),

        ('Bunker6_unsolved_combined.jpg',
         'Bunker6_unsolved.jpg', 'Bunker6_5x5RectGridGraph.png'),
        ('Bunker6_solved_combined.jpg', 'Bunker6_solved.jpg',
         'Bunker6_5x5RectGridGraph0.png'),

        ('Bunker7_unsolved_combined.jpg',
         'Bunker7_unsolved.jpg', 'Bunker7_5x5RectGridGraph.png'),
        ('Bunker7_solved_combined.jpg', 'Bunker7_solved.jpg',
         'Bunker7_5x5RectGridGraph0.png'),

        ('Bunker8_unsolved_combined.jpg',
         'Bunker8_unsolved.jpg', 'Bunker8_6x5RectGridGraph.png'),
        ('Bunker8_solved_combined.jpg', 'Bunker8_solved.jpg',
         'Bunker8_6x5RectGridGraph0.png'),

        ('Shape3_unsolved_combined.jpg',
         'Shape3_unsolved.jpg', 'Shape3_3x3RectGridGraph.png'),
        ('Shape3_solved_combined.jpg', 'Shape3_solved.jpg',
         'Shape3_3x3RectGridGraph0.png'),

        ('TrehouseUnkown0_unsolved_combined.jpg',
         'treehouse_unsolved.jpg', 'testTreehouse0_6x6RectGridGraph.png'),
        ('TrehouseUnkown0_solved_combined.jpg', 'treehouse_solved.jpg',
         'testTreehouse0_6x6RectGridGraph0.png'),

    ]
    solutions_combine_list = [
        [os.path.join(solution_img_dir, i) for i in e] for e in solutions_combine_list]
    #print('solutions_combine_list', solutions_combine_list)
    for combined, orig, generated in solutions_combine_list:
        #print('combined, img_list', combined, [orig,generated])
        chImg.combine_horizontal(combined, [orig, generated])

    examples_combine_list = [
        ('SimpleColorDemo_4x3RectGridGraph_combined.png',
         'SimpleColorDemo_4x3RectGridGraph.png', 'SimpleColorDemo_4x3RectGridGraph0.png'),

    ]
    examples_combine_list = [
        [os.path.join(example_img_dir, i) for i in e] for e in examples_combine_list]
    #print('examples_combine_list', examples_combine_list)
    for combined, orig, generated in examples_combine_list:
        #print('combined, img_list', combined, [orig,generated])
        chImg.combine_horizontal(combined, [orig, generated])


def test_all():
    for name, data in inspect.getmembers(puzzle_definitions, inspect.isfunction):
        if name == '__builtins__':
            continue
        print('%s :' % name, repr(data))

        t = PuzzleTest(data)
        t.setUp()
        t.testSolvePuzzle()
        break


def test_single(test_func):
    t = PuzzleTest(test_func)
    t.setUp()
    t.testSolvePuzzle()
if __name__ == '__main__':
    import inspect
    clear_image_directory()
    test_single(puzzle_definitions.MountainQuadFloorTopLeftSubPuzzle)

    combine_images()

    exit(0)
