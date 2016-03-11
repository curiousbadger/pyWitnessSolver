'''
Created on Feb 27, 2016

@author: charper
'''
import itertools
import string
import pickle
import os
import sqlite3
from PIL.ImageColor import colormap
class sqliteDB(object):
    def __init__(self,puzzle_name):
        self.conn = sqlite3.connect('../../db/pyWitnessSolver.sqlite3')
        self.puzzle_name=puzzle_name
        self.num_inserts=0
        
    # TODO: Table is hardcoded
    def path_exists(self,puzzle_name, path):    
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

class simplePickler(object):
    # TODO: Put in config file
    default_dir='../../db/'
    default_ext='.p'
    def __init__(self,paths_filename):
        d,e=simplePickler.default_dir,simplePickler.default_ext
        self.fn=os.path.join(d,paths_filename+e)
        
    def dump(self,o):
        print('writing pickle to',self.fn)
        # Overwrites file if exists
        f=open(self.fn,'wb')
        pickle.dump(o,f)
        f.close()
        
    def load(self):
        if not self.file_exists(): raise Exception('File does not exist:'+self.fn)
        f=open(self.fn,'rb')
        o=pickle.load(f)
        f.close()
        return o
    
    def file_exists(self):
        return os.path.exists(self.fn)
    def filename(self):
        return self.fn
    
class UniqueNumberGenerator(object):
    def __init__(self):
        self.generator=itertools.count()
    def get(self):
        return next(self.generator)
    def __next__(self):
        return next(self.generator)
    
class UniqueColorGenerator(object):
    #ColorList=['indigo','violet','cyan','white','aqua','red','yellow','blue','green','purple','orange']
    #ColorList=['wheat', 'darkslateblue', 'rosybrown', 'darkblue', 'black', 'aliceblue', 'blanchedalmond', 'darkslategray', 'darkslategrey', 'lightblue', 'mediumorchid', 'violet', 'olivedrab', 'magenta', 'saddlebrown', 'lightgray', 'ivory', 'plum', 'darkorchid', 'snow', 'firebrick', 'yellowgreen', 'steelblue', 'mediumpurple', 'aqua', 'lightcyan', 'darkgreen', 'lightgoldenrodyellow', 'ghostwhite', 'indianred', 'lightslategrey', 'lightgreen', 'dimgrey', 'lightskyblue', 'turquoise', 'limegreen', 'linen', 'salmon', 'cyan', 'cadetblue', 'oldlace', 'green', 'peru', 'khaki', 'aquamarine', 'lightsalmon', 'coral', 'darkgoldenrod', 'hotpink', 'lightsteelblue', 'mistyrose', 'azure', 'mediumaquamarine', 'sandybrown', 'lightcoral', 'mediumseagreen', 'lemonchiffon', 'dimgray', 'whitesmoke', 'honeydew', 'beige', 'seagreen', 'silver', 'maroon', 'springgreen', 'darkcyan', 'gainsboro', 'lightpink', 'lawngreen', 'papayawhip', 'peachpuff', 'lavender', 'sienna', 'navy', 'yellow', 'greenyellow', 'mediumblue', 'floralwhite', 'grey', 'gold', 'palegoldenrod', 'lime', 'darkturquoise', 'pink', 'cornflowerblue', 'palegreen', 'darkseagreen', 'lightgrey', 'tan', 'darkgray', 'thistle', 'powderblue', 'darkmagenta', 'mediumslateblue', 'lightseagreen', 'gray', 'red', 'burlywood', 'palevioletred', 'mediumvioletred', 'tomato', 'olive', 'darkviolet', 'goldenrod', 'brown', 'blueviolet', 'purple', 'bisque', 'teal', 'paleturquoise', 'fuchsia', 'blue', 'orangered', 'lightyellow', 'cornsilk', 'forestgreen', 'dodgerblue', 'chartreuse', 'lavenderblush', 'orchid', 'deeppink', 'midnightblue', 'darkred', 'royalblue', 'darkgrey', 'mintcream', 'chocolate', 'seashell', 'white', 'mediumspringgreen', 'orange', 'navajowhite', 'moccasin', 'darksalmon', 'darkolivegreen', 'slategrey', 'mediumturquoise', 'skyblue', 'slategray', 'darkorange', 'antiquewhite', 'crimson', 'indigo', 'slateblue', 'deepskyblue', 'darkkhaki', 'lightslategray']
    ColorList=['red','green','blue','yellow','white','pink','black','orange', 'darkslateblue', 'rosybrown', 'darkblue', 'black', 'aliceblue', 'blanchedalmond', 'darkslategray', 'darkslategrey', 'lightblue', 'mediumorchid', 'violet', 'olivedrab', 'magenta', 'saddlebrown', 'lightgray', 'ivory', 'plum', 'darkorchid', 'snow', 'firebrick', 'yellowgreen', 'steelblue', 'mediumpurple', 'aqua', 'lightcyan', 'darkgreen', 'lightgoldenrodyellow', 'ghostwhite', 'indianred', 'lightslategrey', 'lightgreen', 'dimgrey', 'lightskyblue', 'turquoise', 'limegreen', 'linen', 'salmon', 'cyan', 'cadetblue', 'oldlace', 'green', 'peru', 'khaki', 'aquamarine', 'lightsalmon', 'coral', 'darkgoldenrod', 'hotpink', 'lightsteelblue', 'mistyrose', 'azure', 'mediumaquamarine', 'sandybrown', 'lightcoral', 'mediumseagreen', 'lemonchiffon', 'dimgray', 'whitesmoke', 'honeydew', 'beige', 'seagreen', 'silver', 'maroon', 'springgreen', 'darkcyan', 'gainsboro', 'lightpink', 'lawngreen', 'papayawhip', 'peachpuff', 'lavender', 'sienna', 'navy', 'yellow', 'greenyellow', 'mediumblue', 'floralwhite', 'grey', 'gold', 'palegoldenrod', 'lime', 'darkturquoise', 'pink', 'cornflowerblue', 'palegreen', 'darkseagreen', 'lightgrey', 'tan', 'darkgray', 'thistle', 'powderblue', 'darkmagenta', 'mediumslateblue', 'lightseagreen', 'gray', 'red', 'burlywood', 'palevioletred', 'mediumvioletred', 'tomato', 'olive', 'darkviolet', 'goldenrod', 'brown', 'blueviolet', 'purple', 'bisque', 'teal', 'paleturquoise', 'fuchsia', 'blue', 'orangered', 'lightyellow', 'cornsilk', 'forestgreen', 'dodgerblue', 'chartreuse', 'lavenderblush', 'orchid', 'deeppink', 'midnightblue', 'darkred', 'royalblue', 'darkgrey', 'mintcream', 'chocolate', 'seashell', 'white', 'mediumspringgreen', 'orange', 'navajowhite', 'moccasin', 'darksalmon', 'darkolivegreen', 'slategrey', 'mediumturquoise', 'skyblue', 'slategray', 'darkorange', 'antiquewhite', 'crimson', 'indigo', 'slateblue', 'deepskyblue', 'darkkhaki', 'lightslategray']
    
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
WastedCounter=UniqueNumberGenerator()

if __name__=='__main__':
    #print(UniqueColorGenerator.ColorList)
    for i in range(30):
        print(MasterUniqueColorGenerator.get())