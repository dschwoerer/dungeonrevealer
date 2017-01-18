#!/usr/bin/python3

import sys
from PIL import Image
from PIL import ImageTk as itk
import tkinter as tk
import numpy as np
import cProfile as cp
def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
tk.Canvas.create_circle = _create_circle

from profilehooks import profile
im_fg=None
im_bg=None
fu=None
class MaxCanvas(tk.Canvas):
    def __init__(self,master=None,images=None):
        tk.Canvas.__init__(self,master,height=100,width=100)
        self.pack(fill=tk.BOTH, expand=tk.YES)
        self.redrawPending=None
        self.images=images
        self.images_=self.images[:]
    #@profile
    def __real_redraw(self,event=None):
        #clear:
        old=self.find_all()
        self.update_idletasks()
        self.redrawPending=None
        aw=max(self.winfo_width(),100)
        ah=max(self.winfo_height(),100)
        for iid,image in enumerate(self.images):
            f1=aw / float(image.width)
            f2=ah / float(image.height)
            self.fac=fac=min( f1, f2)
            nw=int(image.width*fac)
            nh=int(image.height*fac)
            image__=image.resize((nw,nh))
            self.images_[iid] = itk.PhotoImage(image__)
            self.x0=x0=(aw-nw)//2
            self.y0=y0=(ah-nh)//2
            self.create_image(x0,y0,
                              image=self.images_[iid],anchor=tk.NW)
        for i in old:
            self.delete(i)
    def redraw(self,event=None):
        self.__redraw(event)
    def __redraw(self,event):
        #print(".",end='')
        if self.redrawPending is None:
            self.redrawPending=self.after_idle(self.__real_redraw)

class Player(tk.Frame):
    def __init__(self,master=None,parent=None):
        tk.Frame.__init__(self,master)
        global im_fg,im_bg
        self.img=MaxCanvas(self,images=[im_bg,im_fg])
        self.master.title('Player Version')
        self.pack(fill=tk.BOTH, expand=tk.YES)
        self.bind_all('<Escape>',self.__exit)
        self.bind_all('<Configure>',self.redraw)
        self.parent=parent
    def redraw(self,event=None):
        self.parent.redraw()
        self.img.redraw(event)
    def __exit(self,event):
        exit

class Application(tk.Frame):
    def __init__(self, master=None):
        self.master=master
        tk.Frame.__init__(self,master)
        global im_fg,im_bg
        self.im_fg=im_fg.convert('RGBA')
        self.alpha = np.array(self.im_fg.split()[-1])
        #print(self.alpha)
        self.im_fg.putalpha(Image.fromarray(self.alpha//2))
        self.img=MaxCanvas(self,images=[im_bg,self.im_fg])
        self.master.title('Dungeon Master')
        self.pack(fill=tk.BOTH,expand=tk.YES)
        self.save_queue=None
        self.bind_all('<Escape>',self.__exit)
        self.bind_all('<Configure>',self.__redraw)
        self.img.bind('<Motion>',self.__motion)
        self.img.bind('<Button-1>',self.__left)
        self.img.bind('<ButtonRelease-1>',self.__left)
        self.img.bind('<Button-3>',self.__right)
        self.img.bind('<ButtonRelease-3>',self.__right)
        self.img.bind('<Button-4>',self.__larger)
        self.img.bind('<Button-5>',self.__smaller)
        self.newWindow=tk.Toplevel(self.master)
        self.player=Player(self.newWindow,parent=self)
        self.circ=None
        self.circSize=10
    def redraw(self,event=None):
        self.__redraw(event)
    #@profile
    def __redraw(self,event=None):
        self.img.redraw(event)
    def __exit(self,event):
        exit
    def __motion(self,event=None):
        self.img.delete(self.circ)
        self.circ=self.img.create_circle(event.x,event.y,self.circSize,outline="#f00")
    def __smaller(self,event):
        if self.circSize>5:
            self.circSize-=5
        self.__motion(event)
    def __larger(self,event):
        self.circSize+=5
        self.__motion(event)
    def __debug(self,event):
        print(event.num)
    def __left(self,event):
        fac=1/self.img.fac
        size=self.circSize*fac
        x0=(event.x-self.img.x0)*fac
        y0=(event.y-self.img.y0)*fac
        ashape=self.alpha.shape
        xs=max(int(x0-size),0)
        ys=max(int(y0-size),0)
        xe=min(int(x0+size+2),ashape[1])
        ye=min(int(y0+size+2),ashape[0])
        for x in range(xs,xe):
            for y in range(ys,ye):
                if (x-x0)**2+(y-y0)**2 < size**2:
                    self.alpha[y,x]=0
        if int(event.type) == 4:
            #print("rebinding")
            self.img.bind('<Motion>',self.__left)
        elif int(event.type) == 5:
            #print("restoring")
            self.im_fg.putalpha(Image.fromarray(self.alpha//2))
            im_fg.putalpha(Image.fromarray(self.alpha))
            self.img.bind('<Motion>',self.__motion)
            self.player.redraw()
            if self.save_queue:
                self.after_cancel(self.save_queue)
            self.save_queue=self.after(5000,self.__save)
        #else:
        #    print(event.type)
    def __right(self,event):
        if int(event.type) == 4:
            fac=1/self.img.fac
            self.xs=int((event.x-self.img.x0)*fac)
            self.ys=int((event.y-self.img.y0)*fac)
        elif int(event.type) == 5:
            fac=1/self.img.fac
            xe=int((event.x-self.img.x0)*fac)
            ye=int((event.y-self.img.y0)*fac)
            ashape=self.alpha.shape
            xs=max(min(xe,self.xs),0)
            ys=max(min(ye,self.ys),0)
            xe=min(max(xe,self.xs),ashape[1])
            ye=min(max(ye,self.ys),ashape[0])
            for x in range(xs,xe):
                for y in range(ys,ye):
                    self.alpha[y,x]=0
            self.im_fg.putalpha(Image.fromarray(self.alpha//2))
            im_fg.putalpha(Image.fromarray(self.alpha))
            self.player.redraw()
            if self.save_queue:
                self.after_cancel(self.save_queue)
            self.save_queue=self.after(5000,self.__save)
            
            #print("restoring")
        
    def __save(self,event=None):
        print("saving")
        of=sys.argv[1][:-4]+".png"
        im_fg.save(of,"PNG")
            
            
        
try:
    im_bg=Image.open(sys.argv[2])
except e:
    print("Usage:")
    print("\t%s <path-to-fg-image> <path-to-bg-image>"%sys.argv[0])
    sys.exit(1)

try:
    im_fg=Image.open(sys.argv[1])
except:
    dat = np.array(im_bg.convert("RGB"))
    im_fg=Image.fromarray(dat*0)
def main():
    root=tk.Tk()
    app = Application(root)
    root.mainloop()

if __name__ == '__main__':
    main()
