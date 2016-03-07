'''
Created on Feb 27, 2016

@author: charper
'''
from lib.Node import Node
import itertools
from lib.util import MasterUniqueNumberGenerator
    
class Edge(object):
    '''
    An Edge or link between 2 Nodes
    '''
    def __init__(self, node_list):
        self.hash_int=MasterUniqueNumberGenerator.get()
        # Node order doesn't matter
        self.nodes=frozenset(node_list)
        # But it's nice to be able to tell them apart ;)
        a,b=self.a,self.b=node_list
        
    def __hash__(self):
        return self.nodes
    
    def traverse_from_node(self,from_node):
        ''' Maybe overkill, but if we ever want to do something fancy when a Path is traveling through us,
        this is the place.
        '''
        return self.b if from_node==self.a else self.a
    
if __name__=='__main__':
    nl=[Node() for i in range(2)]
    e=Edge(nl)
    a,b=e.nodes
    a.sym,b.sym='a','b'
    print(a,b)
    print(e.traverse_from_node(a))