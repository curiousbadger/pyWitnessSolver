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
        
        
        '''To make this (hopefully) simpler, I have decided that the
        GridSquares will be 3x as wide,tall as the Path GridNodes.
        
        I don't really care about how big the image itself is, just make
        it "big enough" to clearly display the size of Grids we usually encounter.
        
        So if we have a 2000x2000 "canvas" to play with, we need to determine
        how much to scale objects to fit inside.
        
        Example: We have a RectangleGridPuzzle that is 4x3 counting Path OuterNodes,
        or 3x2 if you're counting the "inner" SquareNodes.
        
        So looking at it horizontally, on all rows we have 4 GridNodes and 
        3 GridSquares, which gives us 4+3*3=13 "elements" to play with, and
        I'm calling this "element_width" for lack of a better term.
        
        So each GridNode will be 2000 / 13 ~= 153 pixels wide and tall,
        and each GridSquare will be 153*3 ~= 462 pixels wide and tall.
        
        We use whichever dimension is greater, element_width or element_height
        to set the scalar, but the idea is the same.
        '''
        element_dimensions=GraphImage.calculate_total_element_dimensions([self.gx,self.gy])

        
        # Default canvas size
        cw,ch=2000.0,2000.0
        canvas=[cw,ch]
        int_canvas=[int(d) for d in canvas]
        im=chImg(canvas)
        scalar=cw/element_dimensions.max_dimension()
        
        
        # Iterate over entrance/exit Outer GridNodes
        for n in self.values():
            if not (n.is_entrance or n.is_exit):
                continue
            r=n.get_imgRect().abs_coords(scalar)
            im.polygon(r,r.color)
        
        # Iterate over Inner GridSquares
        for n in self.inner_grid.values():
            r=n.get_imgRect().abs_coords(scalar)
            im.polygon(r,r.color)
        
        # Draw rule shapes inside the GridSquares
        # TODO: This is a mess...
        rule_shape_nodes=[n for n in self.inner_grid.values() if n.rule_shape]
        if rule_shape_nodes:
            print('rule_shape_nodes', rule_shape_nodes)
            sq_transp_layer=PILImage.new('RGBA',int_canvas,(255,255,255,0))
            td=PILImageDraw.Draw(sq_transp_layer)
            # Default canvas size
            cw,ch=500.0,500.0
            sq_canvas=[cw,ch]
            sq_int_canvas=[int(d) for d in sq_canvas]
            for rsn in rule_shape_nodes:
                print('rsn', rsn)
                cur_rule_shape=rsn.rule_shape
                print('cur_rule_shape', cur_rule_shape)
                bounding_rec=cur_rule_shape.bounding_rectangle
                bounding_rec.offset=Point([0,0])
                print('bounding_rec', bounding_rec)
                
                square_dimensions=bounding_rec.get_dimensions()+Point([2,2])
                print('square_dimensions', square_dimensions)
                square_element_dimensions=GraphImage.calculate_total_element_dimensions(square_dimensions)
                print('square_element_dimensions', square_element_dimensions)
                sq_scalar=cw/square_element_dimensions.max_dimension()
                print('sq_scalar', sq_scalar)
                sq_im=PILImage.new('RGBA',sq_int_canvas,(255,255,255,0))
                sq_d=PILImageDraw.Draw(sq_im)
                r=Rectangle(Rectangle.get_sqare_points(3))
                for p in cur_rule_shape:
                    
                    print('p', p)
                    sq_offset=GraphImage.calculate_inner_square_offset(*p)
                    print('sq_offset', sq_offset)
                    r.offset = sq_offset
                    img_r=r.abs_coords(sq_scalar)
                    sq_d.polygon(img_r, 'green', 'yellow')
                    print('r', r)
                    print('img_r', img_r)
                    #sq_im.show()
            
                rule_square_rect=Rectangle(Rectangle.get_sqare_points(3))
                rule_square_offset=GraphImage.calculate_inner_square_offset(*rsn.key())
                rule_square_rect.offset=rule_square_offset
                rule_square_rect=rule_square_rect.abs_coords(scalar)
                dim=rule_square_rect.get_dimensions()
                print('rule_square_rect.lower_left', rule_square_rect.lower_left)
                print('rule_square_rect', rule_square_rect)
                print('dim', dim)
                if cur_rule_shape.can_rotate:
                    sq_im=sq_im.rotate(15, PILImage.BICUBIC, 1)
                sq_im.thumbnail(dim, PILImage.LANCZOS)
                #fn=self.paths_filename()+str(self.ung.get())
                #sq_im.show()
                sq_transp_layer.paste(sq_im, rule_square_rect.lower_left.as_int_tuple())    
                
            im.im=PILImage.alpha_composite(im.im, sq_transp_layer)
                    
            
        render_partitions=True
        if self.partitions and render_partitions:
            # Draw Partitions
            Partition.cg.reset()
            transp_layer=PILImage.new('RGBA',int_canvas,(255,255,255,0))
            d=PILImageDraw.Draw(transp_layer)
            for p in self.partitions:
                
                for pt,col in p.get_img_rects():
                    #print('pt',pt)
                    
                    offset=GraphImage.calculate_inner_square_offset(pt.x,pt.y)

                    pl=[[0,0],[3,0],[3,3],[0,3]]
                    plp=[Point(p) for p in pl]
                    col=chImg.color_with_alpha(col, 75)
    
                    squ_and_n_rect=Rectangle(plp,offset,col).abs_coords(scalar)
                    #print('squ_and_n_rect', squ_and_n_rect)
                    
                    #im.polygon(squ_and_n_rect, col, 'red')
                    d.polygon(squ_and_n_rect, col, 'purple')
            im.im=PILImage.alpha_composite(im.im, transp_layer)
        
        
        # Draw path
        draw_path=True
        if self.current_path and draw_path:
            transp_layer=PILImage.new('RGBA',int_canvas,(255,255,255,0))
            d=PILImageDraw.Draw(transp_layer)
            
            # 
            for sq in self.inner_grid.values():
                #Draw traversable links for each square
                new_rects=sq.overlay_traversable_rects()
                #print('new_rects',new_rects)
                for r in new_rects:
                    coords,col=r.abs_coords(scalar), r.color
                    col=chImg.color_with_alpha(r.color,75)
                    #print('col', col)
                    
                    d.polygon(coords, col, 'red')
                    #sd.polygon(coords, col, 'green')
            
        
            # Draw path
            for e in self.current_path:
                f,s=e.nodes
                #print('f',f,'s',s)
                
                new_rect=f.get_imgRect(scalar)+s.get_imgRect(scalar)
                col=chImg.color_with_alpha('white', 240)
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
    def calculate_total_element_dimensions(object_dimensions):
        node_weight=GridNode.rendering_weight
        square_weight=GridSquare.rendering_weight
        x,y=object_dimensions
        
        # Calculate the width,height in units of GridNode.rendering_weight
        # There are 1 fewer Squares than Nodes in a Grid. See the signpost problem... 
        element_width=(x*node_weight)+(x-1)*square_weight
        element_height=(y*node_weight)+(y-1)*square_weight
        element_dimensions=Point([element_width,element_height])
        return element_dimensions
        
        
    @staticmethod
    def calculate_inner_square_offset(x,y):
        '''Given an Inner GridSquare x,y coordinates, calculate the
        relative offset based on the rendering weights of Nodes vs. Squares
        
        Ex: If the GridSquare itself has coordinates (0,0), 
        the lower-left corner would be (1,1) in units of GridNode.rendering_weight
        
        Ex: If the GridSquare is at (1,0), the middle of the 
        the lower-left corner would be (5,2) in units of GridNode.rendering_weight
        '''
        combined_weight=GridSquare.rendering_weight + GridNode.rendering_weight
        offset = Point([x,y]).scaled(combined_weight)+Point([1,1])
        #offset = x * combined_weight, y * combined_weight
        return offset
            
    def class_name(self): return 'sqareGraph'
    def cust_string(self):
        return 'gx'+str(self.gx)+'gy'+str(self.gy)
    
if __name__=='__main__':
    
    gi=GraphImage(5,5)
    
    print(gi.render_both())
    gi.render()