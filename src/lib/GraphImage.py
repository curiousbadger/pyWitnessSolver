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

from src.log.simpleLogger import linf, ldbg, ldbg2
from lib.Geometry import Point, Rectangle
from lib.util import UniqueNumberGenerator, defaultValueServer,\
    MasterUniqueColorGenerator, UniqueColorGenerator
from lib.GridGraph import RectGridGraph
from lib.Partition import Partition
from lib.Node import GridNode, GridSquare
from lib.Edge import InnerEdge

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
        linf('Saving image:', img_filename)
        flipped_im=self.flipped()
        if title:
            # Create a new image that is the same width plus some percentage of the height
            title_height=int(.05*self.size[1])
            new_sz=(self.size[0], self.size[1]+title_height)
            title_sz=(self.size[0], title_height)
            #ldbg2('new_sz',new_sz,'title_sz',title_sz)
            
            bigger_image=PILImage.new('RGBA',new_sz,(255,255,255,0))
            title_image=PILImage.new('RGBA',title_sz,(255,255,255,0))
            
            td=PILImageDraw.Draw(title_image)
            font = ImageFont.truetype(font='arial', size=50)
            td.text((10,10), title, fill='white', font=font)
            bigger_image.paste(title_image, (0,0), mask=None)
            bigger_image.paste(flipped_im,(0,title_height), mask=None)
            
            flipped_im=bigger_image
            #flipped_im.paste(title_image, (0,title_height))
            
        linf('Saving image:',img_filename)
        
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
        
    def rectangle(self, xy, fill=None, outline=None):
        self.d.rectangle(xy, fill, outline)
        
    def point(self,xy,fill=None): 
        return self.d.point(xy, fill)

class GraphImage(RectGridGraph):
    '''
    A RectGridGraph with extra functionality for rendering/display.
    
    '''
    render_weights={GridNode:1, GridSquare:3}
    
    def __init__(self, gx, gy, **kwargs):
        super().__init__(gx, gy, **kwargs)
        self.ung=UniqueNumberGenerator()
        self._scalar=1

    def render_solution(self,title=None):
        paths_filename=self.paths_filename()+str(self.ung.get())
        self.render(paths_filename,title)
        
    def set_scalar(self,scalar):
        self._scalar=scalar
    def scalar(self):
        return self._scalar
    def render(self,paths_filename=None,title=None):
        '''TODO: Convert this mess to use partial opacity layers...
        
        To make this (hopefully) simpler, I have decided that the
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
        self.set_scalar(scalar)
        ldbg('scalar', scalar)
        
        
        # BEGIN: Draw background
        # Draw entrance/exit Outer GridNodes
        for n in self.values():
            if not (n.is_entrance or n.is_exit):
                continue
            
            img_rect, col = self.translate_node_to_rectangles(n)[0]
            ldbg('img_rect, col', img_rect, col)
            im.rectangle(img_rect, col, outline=None)
        
        # Iterate over Inner GridSquares
        for gs in self.inner_grid.values():
            img_rects=self.translate_node_to_rectangles(gs)
            ldbg('img_rects', img_rects)
            
            #im.polygon(r,r.color)
            for img_rect, col in img_rects:
                im.rectangle(img_rect, col)
                pass
        # END  : Draw background
        
        
        # Draw GridSquare Edges as lines instead of small, pink squares :)
        overlay_img=PILImage.new('RGBA',int_canvas,(255,255,255,0))
        overlay_draw=PILImageDraw.Draw(overlay_img)
        for e in self.inner_grid.edges.values():
            if not e.is_fully_connected():
                continue
            na,nb=e
            ldbg2('na,nb', na,nb)
            coordinate_list=[Point(GraphImage.calculate_node_offset(*n.pt,n))+Point((1.5,1.5)) for n in e]
            coordinate_list=[p.scaled(scalar) for p in coordinate_list]
            ldbg('coordinate_list', coordinate_list)
            
            # peachpuff: Color Of The Year :)
            line_color = chImg.color_with_alpha('peachpuff', 65)
            line_width = int(.15*self.scalar())
            overlay_draw.line(coordinate_list, line_color, line_width)
        im.im=PILImage.alpha_composite(im.im, overlay_img)
           
        # Draw rule shapes inside the GridSquares
        # TODO: HACK This is an ABSOLUTE mess... LAYERING!!!
        rule_shape_nodes=[n for n in self.inner_grid.values() if n.rule_shape]
        if rule_shape_nodes:
            ldbg2('rule_shape_nodes', rule_shape_nodes)
            sq_transp_layer=PILImage.new('RGBA',int_canvas,(255,255,255,0))
            #td=PILImageDraw.Draw(sq_transp_layer)
            # Default canvas size
            cw,ch=500.0,500.0
            sq_canvas=[cw,ch]
            sq_int_canvas=[int(d) for d in sq_canvas]
            for rsn in rule_shape_nodes:
                linf('*** BEGIN RENDER rule_shape_node:', rsn)
                cur_rule_shape=rsn.rule_shape
                linf('cur_rule_shape', cur_rule_shape)
                # How big is the Rule Shape? We'll scale it's Points (Squares)
                bounding_rec=cur_rule_shape.bounding_rectangle
                linf('bounding_rec', bounding_rec)
                
                # TODO: Hack, +2,2 because no Path nodes...
                rule_shape_dimensions=bounding_rec.get_dimensions()+Point([2,2])
                #rule_shape_dimensions=Rectangle.get_square(max_dim).get_dimensions()+Point([2,2])
                linf('rule_shape_dimensions', rule_shape_dimensions)
                
                # This is a mini-Grid itself. Calculate dimensions in units of GridNode rendering weight
                square_element_dimensions=GraphImage.calculate_total_element_dimensions(rule_shape_dimensions)
                linf('square_element_dimensions', square_element_dimensions)
                
                # A mini-Grid needs a mini-scalar :)
                sq_scalar=cw/square_element_dimensions.max_dimension()
                linf('sq_scalar', sq_scalar)
                
                # Calculate the offset needed because we're putting a potentially non-square
                # Rule Shape into a square canvas
                # TODO: Don't know, ask me in the morning...
                shift_dim = rule_shape_dimensions - Point([1.0,1.0])
                #shift_dim = square_element_dimensions
                linf('shift_dim',shift_dim)
                
                vertical_shift =  shift_dim.x / shift_dim.y
                horizontal_shift =  shift_dim.y / shift_dim.x
                # TODO: Hack, I have NO idea
                if vertical_shift > horizontal_shift:
                    vertical_shift *= 1.5
                    horizontal_shift = 0
                else:
                    vertical_shift = 0
                    horizontal_shift *= 1.5
                rule_shape_offset=Point([horizontal_shift, vertical_shift])
                linf('rule_shape_offset', rule_shape_offset)
                
                # Get a new image to draw in. We'll paste this into our layer when finished
                sq_im=PILImage.new('RGBA',sq_int_canvas,(255,255,255,0))
                sq_d=PILImageDraw.Draw(sq_im)
                r=Rectangle(Rectangle.get_sqare_points(3))
                for p in cur_rule_shape:
                    linf('    Current Rule Shape point:', p)
                    
                    # TODO: HACK, just getting the corresponding InnerGrid Square to pass
                    # to calculate_node_offset so that it will apply the right
                    # Square offset. Ugh.... :(
                    hack_temp_square=self.inner_grid[p]
                    sq_offset=GraphImage.calculate_node_offset(*p,hack_temp_square)
                    linf('    sq_offset', sq_offset)
                    r.offset = sq_offset + rule_shape_offset
                    img_r=r.abs_coords(sq_scalar)
                    sq_d.polygon(img_r, 'green', 'yellow')
                    linf('    r', r)
                    linf('    img_r', img_r)
                    #sq_im.show()
            
                rule_square_rect=Rectangle(Rectangle.get_sqare_points(3))
                rule_square_offset=GraphImage.calculate_node_offset(*rsn.key(), rsn)
                rule_square_rect.offset=rule_square_offset
                rule_square_rect=rule_square_rect.abs_coords(scalar)
                dim=rule_square_rect.get_dimensions()
                linf('rule_square_rect.lower_left', rule_square_rect.lower_left)
                linf('rule_square_rect', rule_square_rect)
                linf('dim', dim)
                if cur_rule_shape.can_rotate:
                    sq_im=sq_im.rotate(15, PILImage.BICUBIC, 1)
                sq_im.thumbnail(dim, PILImage.LANCZOS)
                #fn=self.paths_filename()+str(self.ung.get())
                #sq_im.show()
                sq_transp_layer.paste(sq_im, rule_square_rect.lower_left.as_int_tuple())    
                
            im.im=PILImage.alpha_composite(im.im, sq_transp_layer)
                    
        # Overlay anything Partitions want to add
        render_partitions=True
        if self.partitions and render_partitions:
            overlay_img=PILImage.new('RGBA',int_canvas,(255,255,255,0))
            overlay_draw=PILImageDraw.Draw(overlay_img)
            
            # Overlay Rule Shape solution positions
            for p in self.partitions:
                partition_color_generator=UniqueColorGenerator()
                for edge_set in p.solution_shapes_to_edges():
                    # Get a color for this Rule Shape
                    col=partition_color_generator.get()
                    col=chImg.color_with_alpha(col, 50)
                    ldbg('edge_set',edge_set,'color',col)
                    for e in edge_set:
                        squares=[s for s in e]
                        ldbg('squares',squares)
                        rule_shape_rects=[GraphImage.get_node_rectangle(s, self.scalar(), shrink=.8) for s in squares]
                        ldbg('rule_shape_rects', rule_shape_rects)
                        rule_shape_points_list=[]
                        for r in rule_shape_rects:
                            rule_shape_points_list.extend(r)
                        ldbg('rule_shape_points_list', rule_shape_points_list)
                        new_rect=Rectangle.get_bounding_rectangle(rule_shape_points_list)
                        ldbg('new_rect', new_rect)
                        overlay_draw.rectangle(new_rect.as_2_points(), col, outline=None)
                
            im.im=PILImage.alpha_composite(im.im, overlay_img)

        
        # Draw path
        draw_path=True
        if self.current_path and draw_path:
            overlay_img=PILImage.new('RGBA',int_canvas,(255,255,255,0))
            overlay_draw=PILImageDraw.Draw(overlay_img)
            
            '''Render traversable Edges as little Rectangles between Squares (now using lines)
            for sq in self.inner_grid.values():
                #Draw traversable links for each square
                new_rects=sq.overlay_traversable_rects()
                #ldbg2('new_rects',new_rects)
                for r in new_rects:
                    coords,col=r.abs_coords(scalar), r.color
                    col=chImg.color_with_alpha(r.color,75)
                    #ldbg2('col', col)
                    d.polygon(coords, col, 'red')
                    #sd.polygon(coords, col, 'green')
            '''
        
            # Draw path
            for e in self.current_path:
                #f,s=e.nodes
                
                # "Add" the two path Node rectangles together to draw a rectangle between them
                rect_points=[]
                for n in e.nodes:
                    rect_points.extend(self.translate_node_to_rectangles(n)[0][0])
                
                path_rectangle=Rectangle.get_bounding_rectangle(rect_points)
                path_2_pt_rect=path_rectangle.as_2_points()

                ldbg('rect_points', rect_points)
                ldbg('path_rectangle',path_rectangle)
                ldbg('path_2_pt_rect', path_2_pt_rect)

                col=chImg.color_with_alpha('blue', 150)
                overlay_draw.rectangle(path_2_pt_rect, col, outline=None)
            im.im=PILImage.alpha_composite(im.im, overlay_img)
        
        

        #PILImage.alpha_composite(bb, square_traversable_layer)
        #square_traversable_layer.save('../../img/test_transp.png')
        #comp=PILImage.alpha_composite(im.im, square_traversable_layer)
        #comp.save('../../img/test_transp_blue.png')
        
        if not paths_filename:
            paths_filename=self.paths_filename()
        if title is None:
            title=paths_filename
        
        im.save(paths_filename,title=title)
    
    def translate_node_to_rectangles(self, n):
        ''' Given a Node (Inner or Outer), return a list of Rectangles to draw.
        
        TODO: Is there a good reason to split these up? '''
        if type(n)== GridNode:
            return self.translate_grid_node(n)
        elif type(n)== GridSquare:
            return self.translate_grid_square(gs=n)
        
    def translate_grid_node(self, n):
        ret_list=[]
        background_rect=GraphImage.get_node_rectangle(n, self.scalar())
        ret_list.append((background_rect, n.get_color()))
        return ret_list
    
    def translate_grid_square(self, gs):
        ''' Given a GridSquare, return a list of (absolute coordinate, color) pairs 
        
        TODO: Handle rule shape/colors here as well '''
        ret_list=[]
        background_rect=GraphImage.get_node_rectangle(gs, self.scalar())
        ret_list.append((background_rect, gs.get_color()))
        return ret_list
    
    
    @staticmethod
    def calculate_total_element_dimensions(object_dimensions):
        ''' Given an object with dimensions object_dimensions (x,y) 
        Return the total number of elements in units of 
        GridNode rendering_weight
        
        Or, how many GridNodes high and wide is this object?
        '''
        node_weight=GraphImage.render_weights[GridNode]
        square_weight=GraphImage.render_weights[GridSquare]
        
        x,y=object_dimensions
        ldbg('calculate_total_element_dimensions:', x, y)
        
        # Calculate the width,height in units of GridNode.rendering_weight
        # There are 1 fewer Squares than Nodes in a Grid. See the signpost problem... 
        element_width=(x*node_weight)+(x-1)*square_weight
        element_height=(y*node_weight)+(y-1)*square_weight
        element_dimensions=Point([element_width,element_height])
        return element_dimensions
    
    @staticmethod
    def get_node_rectangle(n, scalar=1, shrink=1):
        # How big is the node?
        width=GraphImage.render_weights[n.__class__]
        # Where is it, in relative coordinates?
        offset=GraphImage.calculate_node_offset(*n.key(),n)
        # Return a square scaled and offset appropriately
        return Rectangle.get_2_point_square(width, offset, scalar, shrink)
        
    @staticmethod
    def calculate_node_offset(x,y,n=None):
        '''Given a Node (GridNode or GridSquare) x,y coordinates, calculate the
        relative offset based on the rendering weights of Nodes vs. Squares.
        
        Ex: If a GridNode has coordinates (0,0),
        the lower-left corner would be (0,0) in units of GridNode.rendering_weight
        
        Ex: If a GridNode has coordinates (1,0),
        the lower-left corner would be (4,0) in units of GridNode.rendering_weight
        
        GridSquares are similar except that they are shifted up and over by 1 always.
        Ex: If the GridSquare itself has coordinates (0,0), 
        the lower-left corner would be (1,1) in units of GridNode.rendering_weight
        
        Ex: If the GridSquare is at (1,0), the middle of the 
        the lower-left corner would be (5,2) in units of GridNode.rendering_weight
        '''
        if n:
            x,y=n.key()
            
        combined_weight=GridSquare.rendering_weight + GridNode.rendering_weight
        offset = Point([x,y]).scaled(combined_weight)
        # Shift GridSquares up and over by 1
        if type(n)==GridSquare:
            offset = offset + Point([GridNode.rendering_weight,GridNode.rendering_weight])
        #offset = x * combined_weight, y * combined_weight
        ldbg2(n, offset)
        return offset
            
    def cust_string(self):
        return 'gx'+str(self.gx)+'gy'+str(self.gy)


if __name__=='__main__':
    ''' Given an Edge, draw a line
    
    Need x,y coords of each endpoint
    '''
    
    gi=GraphImage(11,11,auto_assign_edges=False)
    na=gi.inner_grid[0,0]
    nb=gi.inner_grid[0,1]
    nc=gi.inner_grid[3,4]
    na.color='red'
    nb.color = 'green'
    nc.color='blue'
    na_nc=frozenset([na,nc])
    e=InnerEdge(na_nc)
    gi.inner_grid.edges[na_nc]=e
    
    for i in range(100-6):
        y,x=divmod(i, 10)
        key=(x,y)

        n=gi.inner_grid[key]
        print(n)
        for j in range(1,1+6):
            jx=(i+j)%10
            jy=(i+j)//10
            ns=gi.inner_grid[jx,jy]
            print('ns', ns)
            na_nb=frozenset([n,ns])
            print('na_nb', na_nb)
            e=InnerEdge(na_nb)
            gi.inner_grid.edges[na_nb]=e
    #print(gi.render_both())
    exit(0)
    gi.render()
    