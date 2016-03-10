'''
Created on Feb 27, 2016

@author: charper
'''
from lib.Node import Node
import itertools
from lib.util import MasterUniqueNumberGenerator, WastedCounter
    
class Edge(object):
    '''
    An Edge or link between 2 Nodes
    '''
    
#     def __hash__(self):
#         return self.nodes.__hash__()
#     
#     def __eq__(self, other):
#         return self.__hash__()==other.__hash__()
    
    def __init__(self, node_set):
        
        # Node order doesn't matter
        self.nodes=frozenset(node_set)
        self.a,self.b=list(node_set)
        # But it's nice to be able to tell them apart ;)

        a_dict={'other':None,'connected':True}
        
        b_dict={'other':a_dict,'connected':True}
        a_dict['other']=b_dict
        #self.state_map=
        self.state_map={self.a:a_dict, self.b:b_dict}
        
        self.default_state=None
        self.default_a_dict=None
        self.default_b_dict=None
        #self.been_traversed=False
        
        self.connected=True
        self.inner_edge=None
    
    def other_map_entry(self,n):
        return self.state_map[n]['other']
    
    
    def assign_default_state(self):
        '''TODO: Sloppy...
        OuterEdge default_state is useful because when searching for paths 
        because there are certain Paths that will always result in a dead end.
        InnerEdge (GridSquare) default state is not as useful because they are either
        severed by the current Path or not. But when building Partitions we mostly
        want to get every possible GridSquare to check for rule violations, then it's
        on to the next Path, which means we have to reset the connection anyways.'''
        self.default_a_dict=dict(self.state_map[self.a])
        self.default_b_dict=dict(self.state_map[self.b])
        self.default_state={self.a:self.default_a_dict, self.b:self.default_b_dict}
        
    def set_default_state(self):
        self.state_map.update(self.default_state)
    
    def is_connected(self,from_node):
        return self.state_map[from_node]['connected']
    
    
    def is_fully_connected(self):
        return self.state_map[self.a]['connected'] and self.state_map[self.b]['connected']
    
    def sever(self, from_node):
        self.state_map[from_node]['connected']=False
        
    def sever_both(self):
        self.connected=False
        return
        self.sever(self.a)
        self.sever(self.b)
        
    def connect(self, from_node):
        if self.state_map[from_node]['connected']==True:
            WastedCounter.get()
        self.state_map[from_node]['connected']=True
        
    def connect_both(self):
        self.connected=True
        return
        self.connect(self.a)
        self.connect(self.b)
    
    def sever_inner(self):
        if self.inner_edge:
            self.inner_edge.sever_both()
    def reset_inner(self):
        if self.inner_edge:
            self.inner_edge.connect_both()
            #self.inner_edge.set_default_state()
            
    def state_str(self):
        return '|'.join([(str(k)+str(v['connected'])) for k,v in self.state_map.items()])
    def short_str(self):
        return '(%s%s--%s%s)' % (self.a.sym, '<' if self.is_connected(self.b) else ' ','>' if self.is_connected(self.a) else ' ', self.b.sym)
    
    def set_inner_edge(self, inner_edge):
        '''If this is an Edge between "outer" GridNodes, then this
        returns the Edge between the GridSquares on either side of
        this Edge '''
        self.inner_edge=inner_edge
    
    def traverse_from_node(self,from_node):
        ''' Given one of the Edge's Nodes, return the other.
        
        Maybe overkill, but if we ever want to do something fancy when a Path is traveling through us,
        this is the place.
        '''
#         if from_node not in self.nodes:
#             raise Exception(str(self)+' does not have '+str(from_node))
        return self.b if from_node==self.a else self.a
    def get_other_node(self,from_node):
        return self.b if from_node==self.a else self.a
    def attempt_traversal(self, from_node):
        '''If this Edge is connected from from_node to the other, sever the connection
        and return the other node, else return None'''
        
        self.sever_both()
        return self.get_other_node(from_node)
        return None
        if self.is_connected(from_node):
            self.sever(from_node)
            return self.get_other_node(from_node)
        return None
        
    def __repr__(self):
        return 'Edge:(%s)' % ','.join(str(n) for n in self.nodes)

if __name__=='__main__':
    nl=[Node() for i in range(3)]
    na,nb,nc=nl
    for n in nl: n.finalize()
    e=Edge(nl[:2])
    a,b=e.nodes
    
    
    e.sever(a)
    print('e.state_str', e.state_str())
    
    e.assign_default_state()
    
    e.connect(a)
    print('e.state_str', e.state_str())
    e.set_default_state()
    print('e.state_str', e.state_str())