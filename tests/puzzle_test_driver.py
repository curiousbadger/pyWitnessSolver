import os
import glob
from shutil import copyfile
from tests import puzzle_definitions

from tests.PuzzleTest import PuzzleTest

from lib.util import defaultValueServer
from lib.GraphImage import chImg

img_dir, img_ext = defaultValueServer.get_directory_extension_pair('image')
solution_img_dir = defaultValueServer.get_directory('solution')
def clear_image_directory():
    ''' Delete all .png images in the img/example dir '''
    search_pattern = os.path.join(img_dir, '*' + img_ext)
    r = glob.glob(search_pattern)
    for f in r:
        os.remove(f)
def combine_images():
    '''Combine images side-by side '''
    solutions_combine_list=[
        ('Bunker_2_unsolved_combined.jpg', 'Bunker2_unsolved.jpg', 'Bunker2_4x4RectGridGraph.png'),
        ('Bunker_2_solved_combined.jpg', 'Bunker2_solved.jpg','Bunker2_4x4RectGridGraph0.png')
    ]
    solutions_combine_list=[[os.path.join(solution_img_dir, i) for i in e] for e in solutions_combine_list]
    #print('solutions_combine_list', solutions_combine_list)
    for combined, orig, generated in solutions_combine_list:
        print('combined, img_list', combined, [orig,generated])
        chImg.combine_horizontal(combined, [orig,generated])
if __name__ == '__main__':
    clear_image_directory()
    t=PuzzleTest(puzzle_definitions.Bunker2)
    
    t.setUp()
    t.testSolvePuzzle()
    combine_images()
    
    exit(0)
    