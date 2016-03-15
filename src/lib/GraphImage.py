'''
Created on Feb 23, 2016

@author: charper

The idea here was to keep the image rendering stuff in a separate class so people could use this
without Pillow (PIL). I'm tempted to scrap that separation since Pillow is so easy to install.
'''
import os
from math import ceil

from PIL import Image as PILImage
from PIL import ImageDraw as PILImageDraw
from PIL import ImageFont,ImageColor

from lib.Geometry import Point, Rectangle
from lib.util import UniqueNumberGenerator, defaultValueServer
from lib.Graph import RectGridGraph
from lib.Partition import Partition
from lib.Node import GridNode, GridSquare

class chImg(object):
    '''Wrapper around Pillow Image.
    
    TODO: Should probably just inherit instead of has-a'''
    
    def __init__(self,size=(1000,1000),mode='RGBA',color='black'):
        int_sz=[int(ceil(d)) for d in size]
        self.size=int_sz
        self.im=PILImage.new(mode,int_sz,color)
        self.d=PILImageDraw.Draw(self.im)
    
    @staticmethod
    def color_with_alpha(col_str,alpha):
        '''Convert a color string to a tuple of 2-byte RGB values and add
        an alpha band'''
        col_from_str=list(ImageColor.getrgb(col_str))
        col_from_str.append(alpha)
        if any(b<0 or b>255 for b in col_from_str):
            raise ValueError('col_str',col_str,'alpha',alpha)
        new_col=tuple(col_from_str)
        return new_col
        
    def save(self,paths_filename,directory=None,title=None):
        
        # Get default values
        d,ext=defaultValueServer.get_directory_extension_pair('image')

        img_filename=os.path.join(d,paths_filename+ext)
        
        flipped_im=self.flipped()
        if title:
            # Create a new image that is the same width plus some percentage of the height
            title_height=int(.05*self.size[1])
            new_sz=(self.size[0], self.size[1]+title_height)
            title_sz=(self.size[0], title_height)
            #print('new_sz',new_sz,'title_sz',title_sz)
            
            bigger_image=PILImage.new('RGBA',new_sz,(255,255,255,0))
            title_image=PILImage.new('RGBA',title_sz,(255,255,255,0))
            
            td=PILImageDraw.Draw(title_image)
            font = ImageFont.truetype(font='arial', size=50)
            td.text((10,10), title, fill='white', font=font)
            bigger_image.paste(title_image, (0,0), mask=None)
            bigger_image.paste(flipped_im,(0,title_height), mask=None)
            
            flipped_im=bigger_image
            #flipped_im.paste(title_image, (0,title_height))
            
        print('Saving image:',img_filename)
        
        flipped_im.save(img_filename,fmt=None)
        
    def drawtitle(self,text):
        pass
        font = ImageFont.truetype(font='arial', size=30)
        #im.d.text((10, 10), "hello",font=font)
    def show(self): self.flipped().show()
    def flipped(self): 
        return self.im.transpose(PILImage.FLIP_TOP_BOTTOM) 
    
    def line(self,xy,color,width=0): 
        self.d.line(xy,color,width)
    def polygon(self,xy,fill=None,outline=None): 
        self.d.polygon(xy, fill, outline)        
    def point(self,xy,fill=None): 
        return self.d.point(xy, fill)

class GraphImage(RectGridGraph):
    '''
    A RectGridGraph with extra functionality for rendering/display.
    
    '''
    
    def __init__(self, gx, gy, *args):
        super().__init__(gx, gy)
        self.ung=UniqueNumberGenerator()

    def render_solution(self,title=None):
        paths_filename=self.paths_filename()+str(self.ung.get())
        self.render(paths_filename,title)
        
    def render(self,paths_filename=None,title=None):
        '''TODO: Convert this mess to use partial opacity layers...'''
        print ('rendering...',paths_filename)
        node_width=GridNode.rendering_weight
        square_width=GridSquare.rendering_weight
        
        total_w=(self.gx*node_width)+(self.gx-1)*square_width
        total_h=(self.gy*node_width)+(self.gy-1)*square_width
        print('total_w', total_w)
        print('total_h', total_h)
        max_dim=max([total_w,total_h])
        # Default canvas size
        cw,ch=2000.0,2000.0
        canvas=[cw,ch]
        int_canvas=[int(d) for d in canvas]
        im=chImg(canvas)
        scalar=cw/max_dim
        #print('cw',cw,'scalar',scalar,'total_w',total_w)
        
        # Iterate over all Nodes (Outer and Inner)
        render_list=[n.get_imgRect().abs_coords(scalar) for n in self.iter_all()]
        for n in render_list:
            im.polygon(n,n.color)
        
        #Draw traversable links for each square
        for sq in self.inner_grid.values():
            #print('sq',sq)
            new_rects=sq.overlay_traversable_rects()
            #print('new_rects',new_rects)
            for r in new_rects:
                coords,col=r.abs_coords(scalar), r.color
                col=chImg.color_with_alpha(r.color,128)

                #print(col)
                
                im.polygon(coords, col, 'red')
                #sd.polygon(coords, col, 'green')
        
        # Draw rule shapes/colors
        for sq in self.inner_grid.values():
            rule_rect=sq.overlay_rule()
            if rule_rect:
                coords,col=rule_rect.abs_coords(scalar), rule_rect.color
                #print('col',col)
                im.polygon(coords, col, 'green')
        
        
        # Draw Partitions
        
        Partition.cg.reset()
        transp_layer=PILImage.new('RGBA',int_canvas,(255,255,255,0))
        d=PILImageDraw.Draw(transp_layer)
        for p in self.partitions:
            
            for pt,col in p.get_img_rects():
                #print('pt',pt)
                
                offset=GraphImage.calculate_inner_sqare_offset(pt.x,pt.y)
                
                offset=Point(offset)+Point([1,1])
                
                pl=[[0,0],[3,0],[3,3],[0,3]]
                plp=[Point(p) for p in pl]
                col=chImg.color_with_alpha(col, 200)

                squ_and_n_rect=Rectangle(plp,offset,col).abs_coords(scalar)
                #print('squ_and_n_rect', squ_and_n_rect)
                
                #im.polygon(squ_and_n_rect, col, 'red')
                d.polygon(squ_and_n_rect, col, 'purple')
                
                
        im.im=PILImage.alpha_composite(im.im, transp_layer)
        
        # Draw path
        if self.current_path:
            #self.inner_grid.reset()
            #self.set_current_path(self.current_path)
        
            # Draw path
            transp_layer=PILImage.new('RGBA',int_canvas,(255,255,255,0))
            d=PILImageDraw.Draw(transp_layer)
            for e in self.current_path:
                f,s=e.nodes
                #print('f',f,'s',s)
                
                new_rect=f.get_imgRect(scalar)+s.get_imgRect(scalar)
                col=(255,255,255,200)
                #print('new_rect',new_rect)
                d.polygon(new_rect, col)
            im.im=PILImage.alpha_composite(im.im, transp_layer)
            
        #PILImage.alpha_composite(bb, square_traversable_layer)
        #square_traversable_layer.save('../../img/test_transp.png')
        #comp=PILImage.alpha_composite(im.im, square_traversable_layer)
        #comp.save('../../img/test_transp_blue.png')
        
        if not paths_filename:
            paths_filename=self.paths_filename()
        if title is None:
            title=paths_filename
        
        im.save(paths_filename,title=title)
    
    @staticmethod
    def calculate_inner_sqare_offset(x,y):
        '''Given an Inner GridSquare x,y coordinates, calculate the
        relative offset based on the rendering weights of Nodes vs. Squares
        
        Ex: If the lower-left GridNode is at (0,0), the middle of the 
        lower-left GridSquare would be (2,2)'''
        combined_weight=GridSquare.rendering_weight + GridNode.rendering_weight
        offset = Point([x,y]).scaled(combined_weight)
        #offset = x * combined_weight, y * combined_weight
        return offset
            
    def class_name(self): return 'sqareGraph'
    def cust_string(self):
        return 'gx'+str(self.gx)+'gy'+str(self.gy)
    
if __name__=='__main__':
    
    gi=GraphImage(5,5)
    
    print(gi.render_both())
    gi.render()