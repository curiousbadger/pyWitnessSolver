'''
Created on Feb 27, 2016

@author: charper
'''
import itertools
import string
import pickle
import os
import sqlite3

class simplePickler(object):
    default_dir='../paths/'
    default_ext='.p'
    def __init__(self,filename):
        d,e=simplePickler.default_dir,simplePickler.default_ext
        self.fn=os.path.join(d,filename+e)
        
    def dump(self,o):
        print('writing to',self.fn)
        f=open(self.fn,'wb')
        pickle.dump(o,f)
        f.close()
        
    def load(self):
        if not self.file_exists():
            raise Exception('File does not exist:'+self.fn)
        f=open(self.fn,'rb')
        o=pickle.load(f)
        f.close()
        return o
    
    def file_exists(self):
        return os.path.exists(self.fn)
    
class UniqueNumberGenerator(object):
    def __init__(self):
        self.generator=itertools.count()
    def get(self):
        return next(self.generator)
    def __next__(self):
        return next(self.generator)
class UniqueColorGenerator(object):
    ColorList=['white','aqua','red','yellow','blue','green','purple','orange','indigo','violet','cyan']
    ColorDict=dict(enumerate(ColorList,start=1))
    def __init__(self):
        self.generator=iter(UniqueColorGenerator.ColorList)
    def reset(self):
        self.generator=iter(UniqueColorGenerator.ColorList)
    def get(self):
        return next(self.generator)
    def __next__(self):
        return next(self.generator)

class UniqueStringGenerator(object):
    symbol_string = string.ascii_letters + string.punctuation + string.digits
    def __init__(self):        
        self.r_length=1
        self.generator=itertools.permutations(UniqueStringGenerator.symbol_string,self.r_length)
    def __next__(self):
        n=None
        while n==None:
            try:
                n=''.join(next(self.generator))
            except StopIteration:
                self.r_length+=1
                self.generator=self.generator=itertools.permutations(UniqueStringGenerator.symbol_string,self.r_length)
        return n
    def get(self):
        return next(self)

MasterUniqueNumberGenerator=UniqueNumberGenerator()
MasterUniqueStringGenerator=UniqueStringGenerator()
MasterUniqueColorGenerator=UniqueColorGenerator()
class sqliteDB(object):
    def __init__(self,puzzle_name):
        self.conn = sqlite3.connect('../../db/pyGrid.sqlite3')
        self.puzzle_name=puzzle_name
        self.num_inserts=0
    def path_exists(self,path):    
        sql="""
select count(*) from paths10x10
where path=='%s'
""" % (path)
        cursor = self.conn.execute(sql)    
        r=next(cursor)[0]
        return r==1
    
    def write_path(self,path):
        #print(path)
        #sql="INSERT INTO path_w_id (path,puzzle) \
        #    VALUES ('%s', '%s')" % (str(path),self.puzzle_name)
        path_str='|'.join([','.join([str(n) for n in c]) for c in path])
        
        if self.path_exists(path_str):
            return
#         sql="INSERT INTO raw_path (path) \
#             VALUES ('%s')" % (path_str)
        sql="""
insert into paths10x10 
select t.path from (
    select '%s' as path
) t
left join paths10x10 p
    on t.path=p.path
where p.path is null;
""" % (path_str)
        #print(sql)
        
        self.conn.execute(sql);
        self.conn.commit()
        self.num_inserts+=1
        if not self.num_inserts % 5000:
            print(self.num_inserts)
        #exit(0)
if __name__=='__main__':
    #db=sqliteDB('foo')
    #db.write_path(path='''0,0|0,1|0,2|0,3|0,4|0,5|0,6|0,7|0,8|0,9|1,9|1,8|1,7|1,6|1,5|1,4|1,3|1,2|1,1|1,0|2,0|2,1|2,2|2,3|2,4|2,5|2,6|2,7|2,8|2,9|3,9|3,8|3,7|3,6|3,5|3,4|3,3|3,2|3,1|3,0|4,0|4,1|4,2|4,3|4,4|4,5|4,6|4,7|4,8|4,9|5,9|5,8|5,7|5,6|5,5|5,4|5,3|5,2|5,1|5,0|6,0|6,1|6,2|6,3|6,4|6,5|6,6|6,7|6,8|6,9|7,9|7,8|7,7|7,6|7,5|7,4|7,3|7,2|7,1|7,0|8,0|8,1|8,2|8,3|8,4|8,5|8,6|8,7|8,8|8,9''')
    p=os.path.join('../paths/','foo.txt')
    ab=os.path.abspath(p)
    print(p,ab)