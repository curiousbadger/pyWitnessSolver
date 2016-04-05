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
#     def __eq__(self, other):
#         return self.__hash__()==other.__hash__()
    
    def __init__(self, node_set):
        
        # Node order doesn't matter
        self.nodes=frozenset(node_set)
        # But it's nice to be able to tell them apart ;)
        self.a,self.b=list(node_set)
        
        ''' The state_map answers the question:
        Can I travel from Node (key) to the other?'''
        self.state_map={self.a:True, self.b:True}
        
        self.default_state=None
        self.default_a_state=None
        self.default_b_state=None
        #self.been_traversed=False
        
        self.connected=True
        
    
    def __iter__(self):
        return iter(self.nodes)
    
    def assign_default_state(self):
        '''OuterEdge default_state is useful because when searching for paths 
        because there are certain Paths that will always result in a dead end.
        InnerEdge (GridSquare) default state is not as useful because they are either
        severed by the current Path or not. But when building Partitions we mostly
        want to get every possible GridSquare to check for rule violations, then it's
        on to the next Path, which means we have to reset the connection anyways.'''
        self.default_a_state=self.state_map[self.a]
        self.default_b_state=self.state_map[self.b]
        self.default_state={self.a:self.default_a_state, self.b:self.default_b_state}
        
    def set_default_state(self):
        self.state_map.update(self.default_state)
    
    def is_connected(self,from_node):
        raise NotImplemented
        
    def is_fully_connected(self):
        if self.connected and not (self.is_connected(self.a) and self.is_connected(self.b)):
            raise Exception('Connection state logic')
        return self.connected
        
    # TODO: Need to clearly differentiate sever and connect
    # sever for bi-directional, disconnect for uni-directional?
    def sever(self, from_node):
        self.state_map[from_node]=False
        
    def sever_both(self):
        self.sever(self.a)
        self.sever(self.b)
        
    def disconnect(self):
        raise NotImplemented
        
    def connect(self):
        if self.connected==True:
            # TODO: Use decorator
            WastedCounter.get()
        self.connected=True
        
    def repair(self, from_node):
        if self.state_map[from_node]==True:
            WastedCounter.get()
        self.state_map[from_node]=True
        
    def repair_both(self):
        self.connect()
        self.repair(self.a)
        self.repair(self.b)
    
    def sever_inner(self):
        if self.inner_edge:
            self.inner_edge.disconnect()
            
    def reset_inner(self):
        if self.inner_edge:
            self.inner_edge.connect()
            
    def state_str(self):
        return '|'.join([(str(k)+str(v)) for k,v in self.state_map.items()])
    def short_str(self):
        return '(%s%s--%s%s)' % (self.a.sym, '<' if self.is_connected(self.b) else ' ','>' if self.is_connected(self.a) else ' ', self.b.sym)
    
    
    def get_other_node(self,from_node):
        return self.b if from_node==self.a else self.a
    
    def traverse_from_node(self, from_node):
        ''' PRE: This Edge is traversable from from_node
            POST: The connection from from_node to other_node has been cut
                (or possibly both ways have been cut)'''
        #TODO: Sanity check
        if not self.is_connected(from_node):
            raise Exception('Edge not connected')
        self.disconnect(from_node)
        return self.get_other_node(from_node)

    def __repr__(self):
        return 'Edge:(%s)' % ','.join(str(n) for n in self.nodes)

class OuterEdge(Edge):

    def __init__(self, node_set):
        Edge.__init__(self, node_set)
        self.inner_edge=None
        self.must_travel=None
    
    def set_inner_edge(self, inner_edge):
        '''If this is an Edge between "outer" GridNodes, then this
        returns the Edge between the GridSquares on either side of
        this Edge '''
        self.inner_edge=inner_edge    
    
    def assign_default_state(self):
        return Edge.assign_default_state(self)
    
    def is_connected(self, from_node):
        return self.state_map[from_node]
    
    def is_fully_connected(self):
        return self.state_map[self.a] and self.state_map[self.b]
    
    def disconnect(self, from_node):
        self.sever(from_node)
        
class InnerEdge(Edge):
    
    def assign_default_state(self):
        # TODO: I'm not sure if InnerEdges would ever need this
        raise NotImplementedError
        self.default_state=self.connected
    
    def is_connected(self, from_node=None):
        return self.connected
    def sever_both(self):
        raise NotImplementedError
        self.connected=False
    def repair_both(self):
        raise NotImplementedError
    def connect(self):
        Edge.connect(self)
        for n in self.nodes:
            n.prepare_for_partitioning()
        
    def disconnect(self, from_node=None):
        self.connected=False
if __name__=='__main__':
    nl=[Node() for i in range(3)]
    na,nb,nc=nl
    for n in nl: n.finalize()
    e=Edge(nl[:2])
    a,b=e.nodes
    
    
    e.sever(a)
    print('e.state_str', e.state_str())
    
    e.assign_default_state()
    
    e.repair(a)
    print('e.state_str', e.state_str())
    e.set_default_state()
    print('e.state_str', e.state_str())