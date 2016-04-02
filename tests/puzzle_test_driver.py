import os
import glob
from tests import puzzle_definitions

from tests.PuzzleTest import PuzzleTest

from src.lib.util import defaultValueServer

def clear_image_directory():
    d, e = defaultValueServer.get_directory_extension_pair('image')
    search_pattern = os.path.join(d, '*' + e)
    r = glob.glob(search_pattern)
    for f in r:
        os.remove(f)


if __name__ == '__main__':
    clear_image_directory()
    t=PuzzleTest(puzzle_definitions.MountainLeft6)
    
    t.setUp()
    t.testSolvePuzzle()
    
    exit(0)
    