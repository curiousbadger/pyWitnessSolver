'''
Created on Mar 9, 2016

@author: charper
'''

class Path(object):
    '''
    An ordered list of distinct Node coordinates
    '''


    def __init__(self, params):
        self.node_list=[]
        self.node_set=set()
        
    def push(self, n):
        if n not in self.node_set:
            self.node_set.add(n)
            self.node_list.append(n)
        