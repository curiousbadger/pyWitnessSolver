'''
Created on Mar 29, 2016

@author: charper
'''
import logging
from collections import Counter
#from algorithms.sort.quicksort import quicksort

class simpleLogger(object):

    DEBUG2=logging.DEBUG-1
    def __init__(self, *args, **kwargs):
        self.logger=logging.getLogger('master')
        self.logger.setLevel(logging.INFO)
        
        # stderr stream handler
        self.stream_handler=logging.StreamHandler()
        self.stream_handler.setLevel(logging.INFO)
        
        # TODO: Use this instead and make client calls init handler?
        self.null_handler=logging.NullHandler()
        
        
        # %(asctime)s - %(name)s - %(levelname)s - %(message)s
        self.simple_format=logging.Formatter('%(message)s')
        
        # add simple_format to ch
        self.stream_handler.setFormatter(self.simple_format)
        
        self.time_format=logging.Formatter('%(asctime)s%(message)s')
        
        self.logger.addHandler(self.stream_handler)
        self.waste_counter=Counter()
        self.waste_list=[]
        self.master_state=logging.INFO
        
        self.level_receivers=[self.logger,self.stream_handler]
    
    # TODO: Decorators?
    def info(self, *args):
        return self._info(*args)
    def _info(self, *args):
        self.logger.info(msg=' '.join([str(a) for a in args]))
        
    def debug(self, *args):
        return self._debug(*args)
    def _debug(self, *args):
        self.logger.debug(' '.join([str(a) for a in args]))
    
    def debug2(self, *args):
        return self._debug2(*args)
    def _debug2(self, *args):
        self.logger.log(simpleLogger.DEBUG2, *args)
        
    def set_master_level(self,lvl):
        self.master_state=lvl
        for lr in self.level_receivers:
            lr.setLevel(self.master_state)
        #self.logger.setLevel(self.master_state)
        #self.stream_handler.setLevel(self.master_state)
        
    def deactivate(self):
        
        self.info=self.pass_it
        self.debug=self.pass_it
    
    def reactivate(self):
        self.set_master_level(self.master_state)
        self.info=self._info
        self.debug=self._debug
        
    def track_waste(self,*waste_msg):
        self.waste_list.append(waste_msg)
        
    def get_waste(self):
        c = Counter(self.waste_list)
        self.waste_list=[]
        return c
    
    def pass_it(self, *args):
        pass
    
defaultLogger=simpleLogger()
defaultLogger.set_master_level(logging.DEBUG)
linf=defaultLogger.info
ldbg=defaultLogger.debug
ldbg2=defaultLogger.debug2
track_waste=defaultLogger.track_waste


if __name__ == '__main__':
    ldbg('foo')
    linf('foo')