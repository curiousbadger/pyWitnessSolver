'''
Created on Feb 23, 2016

@author: charper
'''
from PIL import Image as PILImage
from PIL import ImageDraw as PILImageDraw
from PIL import ImageFont
from lib.Graph import RectGridGraph
from math import ceil
from lib.Node import GridNode, GridSquare
from lib.Geometry import MultiBlock
from lib.util import UniqueNumberGenerator
class chImg(object):
    
    defaultImgDir='../img/'
    defaultImgExt='.png'
    
    def __init__(self,size=(1000,1000),mode='RGBA',color='black'):
        int_sz=[int(ceil(d)) for d in size]
        self.size=int_sz
        self.im=PILImage.new(mode,int_sz,color)
        self.d=PILImageDraw.Draw(self.im)
    
    
    def save(self,filename,directory=None,title=None):
        d=directory if directory else chImg.defaultImgDir
        ext=chImg.defaultImgExt
        p=d+filename+ext
        
        flipped_im=self.flipped()
        if title:
            # Create a new image that is the same width plus some percentage of the height
            title_height=int(.05*self.size[1])
            new_sz=(self.size[0], self.size[1]+title_height)
            title_sz=(self.size[0], title_height)
            bigger_image=PILImage.new('RGBA',new_sz,(255,255,255,0))
            print('new_sz',new_sz)
            title_image=PILImage.new('RGBA',title_sz,(255,255,255,0))
            td=PILImageDraw.Draw(title_image)
            font = ImageFont.truetype(font='arial', size=50)
            td.text((10,10), title, fill='white', font=font)
            bigger_image.paste(title_image, (0,0), mask=None)
            bigger_image.paste(flipped_im,(0,title_height), mask=None)
            print(bigger_image.size)
            #flipped_im.paste(title_image, (0,title_height))
            
        print('Saving image:',p)
        
        bigger_image.save(p,fmt=None)
    def drawtitle(self,text):
        pass
        font = ImageFont.truetype(font='arial', size=30)
        #im.d.text((10, 10), "hello",font=font)
    def show(self): self.flipped().show()
    def flipped(self): 
        return self.im.transpose(PILImage.FLIP_TOP_BOTTOM) 
    
        
    def line(self,xy,color,width=0): self.d.line(xy,color,width)
    def polygon(self,xy,fill=None,outline=None): self.d.polygon(xy, fill, outline)        
    def point(self,xy,fill=None): return self.d.point(xy, fill)

class GraphImage(RectGridGraph):
    '''
    A RectGridGraph with extra functionality for rendering/display.
    '''
    

    def __init__(self, gx, gy, *args):
        super().__init__(gx, gy)
        self.ung=UniqueNumberGenerator()

    def render_solution(self,title=None):
        filename=self.filename()+str(self.ung.get())
        self.render(filename,title)
        
    def render(self,filename=None,title=None):
        print ('rendering...')
        node_width=GridNode.rendering_weight
        square_width=GridSquare.rendering_weight
        
        total_w=(self.gx*node_width)+(self.gx-1)*square_width
        
        cw,ch=2000.0,2000.0
        canvas=[cw,ch]
        im=chImg(canvas)
        scalar=cw/total_w
        print('cw',cw,'scalar',scalar,'total_w',total_w)
        render_list=[n.get_imgRect().abs_coords(scalar) for n in self.iter_all()]
        
        for  n in render_list:
            im.polygon(n,n.color)
        
        if self.current_path:
            #self.inner_grid.reset()
            #self.set_current_path(self.current_path)
        
            # Draw path
            for seg in self.current_path:
                f,s=seg
                #print('f',f,'s',s)
                n1,n2=self[f],self[s]
                new_rect=n1.get_imgRect(scalar)+n2.get_imgRect(scalar)
                
                #print('new_rect',new_rect)
                im.polygon(new_rect, 'purple')
            
        #Draw traversable links for each square
        for sq in self.inner_grid.values():
            #print('sq',sq)
            new_rects=sq.overlay_traversable_rects()
            #print('new_rects',new_rects)
            for r in new_rects:
                im.polygon(r.abs_coords(scalar), r.color, 'red')
        if not filename:
            filename=self.filename()
        if title is None:
            title=filename
        
        im.save(filename,None,title)
        
    def filename(self):
        return self.class_name()+'_'+self.cust_string()
    def class_name(self): return 'sqareGraph'
    def cust_string(self):
        return 'gx'+str(self.gx)+'gy'+str(self.gy)
    
if __name__=='__main__':
    
    exit(0)
    
    exit(0)
    gi=GraphImage(7,8)
    gi.inner_grid[2,1].color='purple'
    print(gi.render_both())
    gi.render()