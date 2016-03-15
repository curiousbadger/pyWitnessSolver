'''
Created on Feb 14, 2016

@author: charper
'''
import cProfile, pstats, io
from lib.GraphImage import GraphImage


if __name__ == '__main__':
    pr = cProfile.Profile()
    pr.enable()
    # ... do something ...
    gi=GraphImage(5,5)
    gi.render()
    pr.disable()
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print( s.getvalue())
